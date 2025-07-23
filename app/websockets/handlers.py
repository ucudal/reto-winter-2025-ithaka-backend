import json
import uuid
from typing import Dict, Any, Optional

from .schemas import ChatMessage
from app.services.chat_service import chat_service
from app.db.config.database import get_db, SessionLocal
from app.db.models import Conversation, ChatMessage as DBChatMessage, Application
from sqlalchemy.orm import Session


async def handle_user_message(websocket, manager, message: str):
    """Maneja mensajes del usuario e integra con el servicio de IA"""
    try:
        data = json.loads(message)
        user_msg = ChatMessage(**data)

        # Generar o usar session_id existente
        session_id = data.get("session_id", str(uuid.uuid4()))

        # Obtener o crear conversación en la base de datos
        db = SessionLocal()
        conversation_data = await get_or_create_conversation(db, session_id)

        # Guardar mensaje del usuario
        user_db_message = DBChatMessage(
            conversation_id=conversation_data["conversation_id"],
            message=user_msg.message,
            sender="user",
            message_type=user_msg.type,
            meta_data={"session_id": session_id}
        )
        db.add(user_db_message)
        db.commit()

        # Procesar con el servicio de IA
        ai_response = await chat_service.process_message(
            message=user_msg.message,
            session_id=session_id,
            conversation_data=conversation_data
        )

        # Guardar respuesta de la IA
        ai_db_message = DBChatMessage(
            conversation_id=conversation_data["conversation_id"],
            message=ai_response.message,
            sender="assistant",
            message_type=ai_response.message_type,
            meta_data=ai_response.meta_data
        )
        db.add(ai_db_message)

        # Actualizar conversación con el paso actual
        if ai_response.meta_data:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_data["conversation_id"]
            ).first()
            if conversation:
                conversation.current_step = ai_response.meta_data.get(
                    "current_step", 0)

                # Actualizar o crear application si hay datos
                application_data = ai_response.meta_data.get(
                    "application_data", {})
                if application_data:
                    await update_or_create_application(
                        db, conversation_data["conversation_id"], application_data
                    )

        db.commit()
        db.close()

        # Crear respuesta para el cliente
        bot_response = ChatMessage(
            message=ai_response.message,
            sender="bot",
            type=ai_response.message_type,
            metadata={
                "session_id": session_id,
                "current_step": ai_response.next_step,
                "validation_errors": ai_response.validation_errors,
                "conversation_mode": ai_response.meta_data.get("conversation_mode") if ai_response.meta_data else None
            }
        )

        # Enviar respuesta por WebSocket
        await manager.send_message(bot_response.model_dump_json(), websocket)

    except json.JSONDecodeError:
        error_msg = ChatMessage(
            message="Error: Formato de mensaje inválido",
            sender="bot",
            type="error"
        )
        await manager.send_message(error_msg.model_dump_json(), websocket)

    except Exception as e:
        print(f"Error procesando mensaje: {e}")
        error_msg = ChatMessage(
            message="Disculpa, hubo un error procesando tu mensaje. ¿Podrías intentar de nuevo?",
            sender="bot",
            type="error"
        )
        await manager.send_message(error_msg.model_dump_json(), websocket)


async def get_or_create_conversation(db: Session, session_id: str) -> Dict[str, Any]:
    """Obtiene o crea una conversación en la base de datos"""
    try:
        # Buscar conversación existente
        conversation = db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()

        if not conversation:
            # Crear nueva conversación
            conversation = Conversation(
                session_id=session_id,
                status="active",
                current_step=0
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # Obtener datos de la aplicación si existe
        application_data = {}
        application = db.query(Application).filter(
            Application.conversation_id == conversation.id
        ).first()

        if application:
            application_data = {
                "full_name": application.full_name,
                "email": application.email,
                "phone": application.phone,
                "document_id": application.document_id,
                "country_city": application.country_city,
                "campus_preference": application.campus_preference,
                "ucu_relation": application.ucu_relation,
                "faculty": application.faculty,
                "how_found_ithaka": application.how_found_ithaka,
                "motivation": application.motivation,
                "has_idea": application.has_idea,
                "additional_comments": application.additional_comments,
                "team_members_data": application.team_members_data,
                "is_first_venture": application.is_first_venture,
                "problem_opportunity": application.problem_opportunity,
                "solution_clients": application.solution_clients,
                "innovation_differential": application.innovation_differential,
                "business_model": application.business_model,
                "project_stage": application.project_stage,
                "support_needed": application.support_needed,
                "additional_info": application.additional_info
            }
            # Filtrar valores None
            application_data = {k: v for k,
                                v in application_data.items() if v is not None}

        return {
            "conversation_id": conversation.id,
            "current_step": conversation.current_step,
            "application_data": application_data
        }

    except Exception as e:
        print(f"Error en get_or_create_conversation: {e}")
        # En caso de error, crear una conversación temporal
        return {
            "conversation_id": None,
            "current_step": 0,
            "application_data": {}
        }


async def update_or_create_application(db: Session, conversation_id: int, application_data: Dict[str, Any]):
    """Actualiza o crea una aplicación con los datos proporcionados"""
    try:
        if not conversation_id:
            return

        # Buscar aplicación existente
        application = db.query(Application).filter(
            Application.conversation_id == conversation_id
        ).first()

        if not application:
            # Crear nueva aplicación
            application = Application(conversation_id=conversation_id)
            db.add(application)

        # Actualizar campos
        for field, value in application_data.items():
            if hasattr(application, field) and value is not None:
                setattr(application, field, value)

        # Calcular porcentaje de completitud
        total_fields = len([f for f in application_data.keys()
                           if application_data[f] is not None])
        required_fields = 10  # Campos básicos requeridos
        if application_data.get("has_idea"):
            required_fields += 6  # Campos adicionales para emprendimientos

        completion_percentage = min(
            100, int((total_fields / required_fields) * 100))
        application.completion_percentage = completion_percentage

        # Actualizar estado
        if completion_percentage >= 100:
            application.status = "completed"
        else:
            application.status = "draft"

        db.commit()

    except Exception as e:
        print(f"Error actualizando aplicación: {e}")
        db.rollback()


async def handle_connection_close(websocket, manager, session_id: str = None):
    """Maneja el cierre de conexión WebSocket"""
    try:
        manager.disconnect(websocket)

        if session_id:
            # Opcional: marcar conversación como inactiva
            db = SessionLocal()
            conversation = db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).first()

            if conversation and conversation.status == "active":
                # No cambiar a "abandoned" inmediatamente,
                # podría reconectarse
                pass

            db.close()

    except Exception as e:
        print(f"Error cerrando conexión: {e}")


async def get_conversation_history(session_id: str) -> Dict[str, Any]:
    """Obtiene el historial de conversación para un session_id"""
    try:
        db = SessionLocal()

        conversation = db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()

        if not conversation:
            return {"messages": [], "current_step": 0, "application_data": {}}

        # Obtener mensajes
        messages = db.query(DBChatMessage).filter(
            DBChatMessage.conversation_id == conversation.id
        ).order_by(DBChatMessage.timestamp).all()

        # Obtener datos de aplicación
        application = db.query(Application).filter(
            Application.conversation_id == conversation.id
        ).first()

        application_data = {}
        if application:
            # Convertir a diccionario (similar a update_or_create_application)
            application_data = {
                field: getattr(application, field)
                for field in [
                    "full_name", "email", "phone", "document_id", "country_city",
                    "campus_preference", "ucu_relation", "faculty", "how_found_ithaka",
                    "motivation", "has_idea", "additional_comments", "team_members_data",
                    "is_first_venture", "problem_opportunity", "solution_clients",
                    "innovation_differential", "business_model", "project_stage",
                    "support_needed", "additional_info"
                ]
                if getattr(application, field) is not None
            }

        db.close()

        return {
            "messages": [
                {
                    "message": msg.message,
                    "sender": msg.sender,
                    "type": msg.message_type,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in messages
            ],
            "current_step": conversation.current_step,
            "application_data": application_data
        }

    except Exception as e:
        print(f"Error obteniendo historial: {e}")
        return {"messages": [], "current_step": 0, "application_data": {}}
