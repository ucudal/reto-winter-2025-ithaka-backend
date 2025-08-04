"""
Servicio de chat actualizado para integrar con el sistema de agentes LangGraph
"""

import asyncio
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from ..db.config.database import get_async_session
from ..db.models import Conversation, Message, WizardSession
from ..graph.workflow import process_user_message
import logging

logger = logging.getLogger(__name__)


class ChatService:
    """Servicio principal de chat integrado con agentes IA"""

    def __init__(self):
        pass

    async def process_message(
        self,
        user_message: str,
        user_email: str = None,
        conversation_id: int = None
    ) -> Dict[str, Any]:
        """Procesa un mensaje del usuario usando el sistema de agentes"""

        try:
            # Obtener o crear conversación
            if not conversation_id and user_email:
                conversation_id = await self._get_or_create_conversation(user_email)
            elif not conversation_id and not user_email:
                # Para preguntas FAQ sin email, crear conversación temporal
                conversation_id = await self._create_temporary_conversation()

            # Obtener historial de la conversación
            chat_history = []
            if conversation_id:
                chat_history = await self._get_chat_history(conversation_id)

            # Recuperar estado del wizard si existe
            wizard_state = await self._get_wizard_state(conversation_id)

            # Procesar mensaje a través del workflow de agentes
            result = await process_user_message(
                user_message=user_message,
                conversation_id=conversation_id,
                chat_history=chat_history,
                user_email=user_email,
                wizard_state=wizard_state
            )

            # Guardar mensajes en la base de datos
            if conversation_id:
                await self._save_messages(
                    conversation_id=conversation_id,
                    user_message=user_message,
                    bot_response=result["response"]
                )

            # Persistir estado del wizard si es necesario
            if result.get("wizard_state") in ["ACTIVE", "COMPLETED"]:
                await self._save_wizard_state(
                    conversation_id=conversation_id,
                    wizard_session_id=result.get("wizard_session_id"),
                    wizard_state=result.get("wizard_state"),
                    current_question=result.get("current_question"),
                    wizard_responses=result.get("wizard_responses", {})
                )

            # Actualizar email de conversación si se proporcionó durante el wizard
            if user_email and conversation_id:
                await self._update_conversation_email(conversation_id, user_email)

            return {
                "success": True,
                "response": result["response"],
                "conversation_id": result["conversation_id"] or conversation_id,
                "agent_used": result["agent_used"],
                "wizard_session_id": result.get("wizard_session_id"),
                "wizard_state": result.get("wizard_state", "INACTIVE"),
                "current_question": result.get("current_question"),
                "human_feedback_needed": result.get("human_feedback_needed", False),
                "human_validation_needed": result.get("human_validation_needed", False),
                "metadata": {
                    "next_action": result.get("next_action"),
                    "faq_results": result.get("faq_results"),
                    "validation_results": result.get("validation_results")
                }
            }

        except Exception as e:
            raise e
            logger.error(f"Error in chat service: {e}")
            return {
                "success": False,
                "response": "Lo siento, tuve un problema procesando tu mensaje. ¿Podrías intentar de nuevo?",
                "error": str(e),
                "conversation_id": conversation_id,
                "agent_used": "error_handler"
            }

    async def _get_or_create_conversation(self, user_email: str) -> int:
        """Obtiene conversación existente o crea una nueva"""

        try:
            async for session in get_async_session():
                # Buscar conversación existente por email
                stmt = select(Conversation).where(
                    Conversation.email == user_email)
                result = await session.execute(stmt)
                existing_conversation = result.scalar_one_or_none()

                if existing_conversation:
                    logger.info(
                        f"Found existing conversation {existing_conversation.id} for {user_email}")
                    return existing_conversation.id

                # Crear nueva conversación
                new_conversation = Conversation(email=user_email)
                session.add(new_conversation)
                await session.commit()
                await session.refresh(new_conversation)

                logger.info(
                    f"Created new conversation {new_conversation.id} for {user_email}")
                return new_conversation.id

        except Exception as e:
            raise e
            logger.error(f"Error managing conversation: {e}")
            raise

    async def _get_chat_history(self, conversation_id: int, limit: int = 10) -> List[Dict[str, str]]:
        """Obtiene historial reciente de la conversación"""

        try:
            async for session in get_async_session():
                stmt = select(Message).where(
                    Message.conv_id == conversation_id
                ).order_by(
                    Message.ts.desc()
                ).limit(limit)

                result = await session.execute(stmt)
                messages = result.scalars().all()

                # Convertir a formato de historial (más reciente primero, luego revertir)
                history = []
                for message in reversed(messages):
                    history.append({
                        "role": message.role,
                        "content": message.content,
                        "timestamp": message.ts.isoformat()
                    })

                return history

        except Exception as e:
            raise e
            logger.error(f"Error getting chat history: {e}")
            return []

    async def _save_messages(
        self,
        conversation_id: int,
        user_message: str,
        bot_response: str
    ):
        """Guarda mensajes del usuario y bot en la base de datos"""

        try:
            async for session in get_async_session():
                # Mensaje del usuario
                user_msg = Message(
                    conv_id=conversation_id,
                    role="user",
                    content=user_message
                )
                session.add(user_msg)

                # Respuesta del bot
                bot_msg = Message(
                    conv_id=conversation_id,
                    role="assistant",
                    content=bot_response
                )
                session.add(bot_msg)

                await session.commit()
                logger.info(
                    f"Saved messages for conversation {conversation_id}")

        except Exception as e:
            raise e
            logger.error(f"Error saving messages: {e}")
            # No re-lanzar el error para no interrumpir el flujo principal

    async def _update_conversation_email(self, conversation_id: int, email: str):
        """Actualiza el email de una conversación si no lo tenía"""

        try:
            async for session in get_async_session():
                stmt = select(Conversation).where(
                    Conversation.id == conversation_id)
                result = await session.execute(stmt)
                conversation = result.scalar_one_or_none()

                if conversation and not conversation.email:
                    conversation.email = email
                    await session.commit()
                    logger.info(
                        f"Updated email for conversation {conversation_id}")

        except Exception as e:
            raise e
            logger.error(f"Error updating conversation email: {e}")

    async def get_conversation_info(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene información de una conversación"""

        try:
            async for session in get_async_session():
                stmt = select(Conversation).where(
                    Conversation.id == conversation_id)
                result = await session.execute(stmt)
                conversation = result.scalar_one_or_none()

                if conversation:
                    return {
                        "id": conversation.id,
                        "email": conversation.email,
                        "started_at": conversation.started_at.isoformat(),
                        "message_count": len(conversation.messages) if conversation.messages else 0
                    }

                return None

        except Exception as e:
            raise e
            logger.error(f"Error getting conversation info: {e}")
            return None

    async def _create_temporary_conversation(self) -> int:
        """Crea una conversación temporal para preguntas FAQ sin email"""

        try:
            async for session in get_async_session():
                # Crear conversación temporal sin email
                new_conversation = Conversation(
                    email=None,  # Sin email para conversaciones temporales
                )

                session.add(new_conversation)
                await session.commit()
                await session.refresh(new_conversation)

                logger.info(
                    f"Created temporary conversation {new_conversation.id}")
                return new_conversation.id

        except Exception as e:
            raise e
            logger.error(f"Error creating temporary conversation: {e}")
            # Si falla, devolver un ID temporal negativo para indicar que es temporal
            return -1

    async def _get_wizard_state(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """Recupera el estado del wizard desde la base de datos"""
        try:
            async for session in get_async_session():
                stmt = select(WizardSession).where(
                    and_(
                        WizardSession.conv_id == conversation_id,
                        WizardSession.state.in_(["ACTIVE", "PAUSED"])
                    )
                ).order_by(WizardSession.updated_at.desc())
                
                result = await session.execute(stmt)
                wizard_session = result.scalar_one_or_none()
                
                if wizard_session:
                    return {
                        "wizard_session_id": f"wizard_{wizard_session.id}",
                        "wizard_state": wizard_session.state,
                        "current_question": wizard_session.current_question,
                        "wizard_responses": wizard_session.responses or {}
                    }
                
                break
        except Exception as e:
            logger.error(f"Error getting wizard state: {e}")
        
        return None

    async def _save_wizard_state(
        self,
        conversation_id: int,
        wizard_session_id: str,
        wizard_state: str,
        current_question: int,
        wizard_responses: Dict[str, Any]
    ):
        """Guarda o actualiza el estado del wizard en la base de datos"""
        try:
            async for session in get_async_session():
                # Buscar sesión existente
                stmt = select(WizardSession).where(
                    and_(
                        WizardSession.conv_id == conversation_id,
                        WizardSession.state.in_(["ACTIVE", "PAUSED"])
                    )
                )
                result = await session.execute(stmt)
                existing_session = result.scalar_one_or_none()
                
                if existing_session:
                    # Actualizar sesión existente
                    existing_session.current_question = current_question
                    existing_session.responses = wizard_responses
                    existing_session.state = wizard_state
                else:
                    # Crear nueva sesión
                    new_session = WizardSession(
                        conv_id=conversation_id,
                        current_question=current_question,
                        responses=wizard_responses,
                        state=wizard_state
                    )
                    session.add(new_session)
                
                await session.commit()
                logger.info(f"Saved wizard state for conversation {conversation_id}")
                
                break
        except Exception as e:
            logger.error(f"Error saving wizard state: {e}")


# Instancia global del servicio
chat_service = ChatService()
