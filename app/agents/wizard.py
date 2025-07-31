"""
Agente Wizard - Maneja el flujo completo del formulario de postulación
Incluye validaciones, evaluaciones con IA, y human-in-the-loop
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db.config.database import get_async_session
from ..db.models import WizardSession, Conversation, Postulation
from ..config.questions import WIZARD_QUESTIONS, get_question, is_conditional_question, should_continue_after_question_11
from ..services.evaluation_service import evaluation_service
from ..agents.validator import validator_agent
from ..graph.state import ConversationState
from utils.notifier import send_email_confirmation
import logging

logger = logging.getLogger(__name__)


class WizardAgent:
    """Agente para manejar el flujo del wizard de postulación"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.max_questions = 20

    async def handle_wizard_flow(self, state: ConversationState) -> ConversationState:
        """Maneja el flujo principal del wizard"""

        user_message = state["user_message"].strip().lower()

        # Manejar comandos especiales primero (más flexible)
        if self._is_cancel_command(user_message):
            return await self._handle_cancel(state)
        elif self._is_go_back_command(user_message):
            return await self._handle_go_back(state)

        # Obtener o crear sesión del wizard
        wizard_session = await self._get_or_create_session(state)
        if not wizard_session:
            return self._create_error_state(state, "No se pudo inicializar la sesión del wizard")

        current_question = wizard_session["current_question"]

        # Si es el primer mensaje, mostrar pregunta inicial
        if wizard_session["state"] == "STARTING":
            return await self._show_question(state, current_question, wizard_session)

        # Procesar respuesta a la pregunta actual
        return await self._process_response(state, wizard_session)

    async def _get_or_create_session(self, state: ConversationState) -> Optional[Dict[str, Any]]:
        """Obtiene sesión existente o crea una nueva"""

        try:
            conversation_id = state.get("conversation_id")
            if not conversation_id:
                logger.error("No conversation_id in state")
                return None

            async for session in get_async_session():
                # Buscar sesión existente
                stmt = select(WizardSession).where(
                    WizardSession.conv_id == conversation_id,
                    WizardSession.state.in_(["ACTIVE", "PAUSED", "STARTING"])
                )
                result = await session.execute(stmt)
                existing_session = result.scalar_one_or_none()

                if existing_session:
                    # Convertir a dict para manejo fácil
                    return {
                        "id": existing_session.id,
                        "conv_id": existing_session.conv_id,
                        "current_question": existing_session.current_question,
                        "responses": existing_session.responses or {},
                        "state": existing_session.state
                    }

                # Crear nueva sesión
                new_session = WizardSession(
                    conv_id=conversation_id,
                    current_question=1,
                    responses={},
                    state="ACTIVE"  # Marcar como ACTIVE desde el inicio
                )
                session.add(new_session)
                await session.commit()
                await session.refresh(new_session)

                return {
                    "id": new_session.id,
                    "conv_id": new_session.conv_id,
                    "current_question": new_session.current_question,
                    "responses": new_session.responses or {},
                    "state": new_session.state
                }

        except Exception as e:
            logger.error(f"Error managing wizard session: {e}")
            return None

    async def _show_question(
        self,
        state: ConversationState,
        question_number: int,
        wizard_session: Dict[str, Any]
    ) -> ConversationState:
        """Muestra una pregunta específica al usuario"""

        question_config = get_question(question_number)
        if not question_config:
            return await self._complete_wizard(state, wizard_session)

        # Verificar si es pregunta condicional
        if not is_conditional_question(question_number, wizard_session["responses"]):
            # Saltar pregunta condicional
            return await self._next_question(state, wizard_session)

        # Construir mensaje de la pregunta
        question_text = question_config["text"]

        # Agregar contexto si es necesario
        if question_config.get("note"):
            question_text += f"\n\n💡 {question_config['note']}"

        # Agregar comandos disponibles
        commands_text = "\n\n📝 **Comandos disponibles:**"
        if question_number > 1:
            commands_text += "\n• Escribe `volver` para ir a la pregunta anterior"
        commands_text += "\n• Escribe `cancelar` para terminar el proceso"

        question_text += commands_text

        # Actualizar estado
        state["agent_context"] = {
            "response": question_text,
            "question_number": question_number,
            "waiting_for_answer": True,
            "wizard_session_id": wizard_session["id"]
        }

        state["wizard_session_id"] = wizard_session["id"]
        state["current_question"] = question_number
        state["wizard_state"] = "ACTIVE"
        state["next_action"] = "send_response"
        state["should_continue"] = False
        state["human_feedback_needed"] = True

        # Actualizar sesión en BD
        await self._update_session_state(wizard_session["id"], "ACTIVE")

        return state

    async def _process_response(
        self,
        state: ConversationState,
        wizard_session: Dict[str, Any]
    ) -> ConversationState:
        """Procesa la respuesta del usuario a una pregunta"""

        user_response = state["user_message"].strip()
        current_question = wizard_session["current_question"]
        question_config = get_question(current_question)

        if not question_config:
            return self._create_error_state(state, "Pregunta no encontrada")

        # Validar respuesta
        validation_result = await self._validate_response(question_config, user_response)

        if not validation_result["is_valid"]:
            # Respuesta no válida, mostrar error y pedir de nuevo
            return await self._show_validation_error(state, validation_result, wizard_session)

        # Respuesta válida, evaluar si es pregunta evaluativa
        if question_config.get("type") == "evaluative":
            return await self._evaluate_response(state, question_config, user_response, wizard_session)

        # Respuesta válida y no evaluativa, continuar
        return await self._save_and_continue(state, question_config, user_response, wizard_session)

    async def _validate_response(
        self,
        question_config: Dict[str, Any],
        user_response: str
    ) -> Dict[str, Any]:
        """Valida la respuesta usando el ValidatorAgent"""

        try:
            return validator_agent.validate_wizard_response(question_config, user_response)
        except Exception as e:
            logger.error(f"Error validating response: {e}")
            return {"is_valid": False, "error": "Error en validación"}

    async def _evaluate_response(
        self,
        state: ConversationState,
        question_config: Dict[str, Any],
        user_response: str,
        wizard_session: Dict[str, Any]
    ) -> ConversationState:
        """Evalúa respuesta usando IA y criterios de rúbrica"""

        try:
            question_number = wizard_session["current_question"]
            context = {
                "previous_responses": wizard_session["responses"],
                "question_config": question_config
            }

            evaluation = await evaluation_service.evaluate_response(
                question_number, user_response, context
            )

            if evaluation["is_acceptable"]:
                # Respuesta aceptable, continuar
                return await self._save_and_continue(state, question_config, user_response, wizard_session)
            else:
                # Respuesta necesita mejoras, human-in-the-loop
                return await self._request_improvement(state, evaluation, user_response, wizard_session)

        except Exception as e:
            logger.error(f"Error evaluating response: {e}")
            # En caso de error, aceptar la respuesta y continuar
            return await self._save_and_continue(state, question_config, user_response, wizard_session)

    async def _request_improvement(
        self,
        state: ConversationState,
        evaluation: Dict[str, Any],
        user_response: str,
        wizard_session: Dict[str, Any]
    ) -> ConversationState:
        """Solicita mejoras en la respuesta basándose en la evaluación"""

        try:
            question_number = wizard_session["current_question"]
            suggestions = await evaluation_service.generate_improvement_suggestions(
                question_number, user_response, evaluation
            )

            improvement_message = f"""
📝 **Tu respuesta:** {user_response}

🤔 **Feedback:** {evaluation.get('feedback', 'Tu respuesta puede mejorarse')}

💡 **Sugerencias para mejorar:**
{suggestions}

**¿Quieres mejorar tu respuesta o continuar con la actual?**

Opciones:
• Escribe una respuesta mejorada
• Escribe `continuar` para avanzar con tu respuesta actual
• Escribe `volver` para ir a la pregunta anterior
• Escribe `cancelar` para terminar el proceso
"""

            state["agent_context"] = {
                "response": improvement_message,
                "waiting_for_improvement": True,
                "original_response": user_response,
                "evaluation": evaluation,
                "wizard_session_id": wizard_session["id"]
            }

            state["next_action"] = "send_response"
            state["should_continue"] = False
            state["human_feedback_needed"] = True

            return state

        except Exception as e:
            logger.error(f"Error requesting improvement: {e}")
            # En caso de error, continuar con la respuesta original
            question_config = get_question(wizard_session["current_question"])
            return await self._save_and_continue(state, question_config, user_response, wizard_session)

    async def _save_and_continue(
        self,
        state: ConversationState,
        question_config: Dict[str, Any],
        user_response: str,
        wizard_session: Dict[str, Any]
    ) -> ConversationState:
        """Guarda la respuesta y continúa con la siguiente pregunta"""

        # Guardar respuesta
        field_name = question_config.get(
            "field_name", f"question_{wizard_session['current_question']}")
        wizard_session["responses"][field_name] = user_response

        # Actualizar sesión en BD
        await self._update_session_responses(wizard_session["id"], wizard_session["responses"])

        # Verificar si continuar después de pregunta 11
        if wizard_session["current_question"] == 11:
            if not should_continue_after_question_11(wizard_session["responses"]):
                # El usuario no tiene idea/emprendimiento, completar registro básico
                return await self._complete_basic_registration(state, wizard_session)

        # Continuar con siguiente pregunta
        return await self._next_question(state, wizard_session)

    async def _next_question(
        self,
        state: ConversationState,
        wizard_session: Dict[str, Any]
    ) -> ConversationState:
        """Avanza a la siguiente pregunta"""

        next_question_number = wizard_session["current_question"] + 1

        if next_question_number > self.max_questions:
            # Completar wizard
            return await self._complete_wizard(state, wizard_session)

        # Actualizar número de pregunta
        wizard_session["current_question"] = next_question_number
        await self._update_session_question(wizard_session["id"], next_question_number)

        # Mostrar siguiente pregunta
        return await self._show_question(state, next_question_number, wizard_session)

    async def _handle_go_back(self, state: ConversationState) -> ConversationState:
        """Maneja el comando 'volver'"""

        wizard_session = await self._get_or_create_session(state)
        if not wizard_session:
            return self._create_error_state(state, "No se encontró sesión activa")

        current_question = wizard_session["current_question"]

        if current_question <= 1:
            state["agent_context"] = {
                "response": "Ya estás en la primera pregunta. No puedes volver más atrás.\n\n¿Quieres continuar o `cancelar` el proceso?",
                "wizard_session_id": wizard_session["id"]
            }
        else:
            # Volver a la pregunta anterior
            previous_question = current_question - 1
            wizard_session["current_question"] = previous_question
            await self._update_session_question(wizard_session["id"], previous_question)

            return await self._show_question(state, previous_question, wizard_session)

        state["next_action"] = "send_response"
        state["should_continue"] = False
        state["human_feedback_needed"] = True

        return state

    async def _handle_cancel(self, state: ConversationState) -> ConversationState:
        """Maneja el comando 'cancelar'"""

        wizard_session = await self._get_or_create_session(state)
        if wizard_session:
            await self._update_session_state(wizard_session["id"], "CANCELLED")

        cancel_message = """
❌ **Proceso cancelado**

Has cancelado el proceso de postulación. Tus respuestas se han guardado y podrás retomarlas más tarde si lo deseas.

Si cambias de opinión, simplemente escribe `postular` de nuevo y podrás continuar desde donde lo dejaste.

¿Hay algo más en lo que pueda ayudarte?
"""

        state["agent_context"] = {"response": cancel_message}
        state["wizard_state"] = "CANCELLED"
        state["next_action"] = "send_response"
        state["should_continue"] = False
        state["human_feedback_needed"] = False

        return state

    async def _complete_basic_registration(
        self,
        state: ConversationState,
        wizard_session: Dict[str, Any]
    ) -> ConversationState:
        """Completa registro básico cuando el usuario no tiene idea/emprendimiento"""

        await self._update_session_state(wizard_session["id"], "COMPLETED")

        completion_message = """
✅ **¡Registro completado!**

Gracias por completar tu información básica. Aunque no tengas una idea específica de emprendimiento en este momento, estás dando el primer paso en el camino emprendedor.

**¿Qué sigue?**
• El equipo de Ithaka revisará tu información
• Te contactaremos para ofrecerte recursos y programas que te ayuden a desarrollar tu espíritu emprendedor
• Podrás participar en nuestras actividades y talleres

**Mientras tanto:**
• Síguenos en redes sociales para estar al día con nuestras actividades
• Revisa nuestros cursos electivos disponibles
• ¡Mantente atento a futuras convocatorias!

¡Te deseamos mucho éxito en tu camino emprendedor! 🚀
"""

        # Enviar email de confirmación si hay email
        user_email = wizard_session["responses"].get("email")
        user_name = wizard_session["responses"].get("full_name", "").split(
        )[0] if wizard_session["responses"].get("full_name") else "emprendedor"

        if user_email:
            try:
                send_email_confirmation(user_email, user_name)
            except Exception as e:
                logger.error(f"Error sending confirmation email: {e}")

        state["agent_context"] = {"response": completion_message}
        state["wizard_state"] = "COMPLETED"
        state["next_action"] = "send_response"
        state["should_continue"] = False
        state["human_feedback_needed"] = False

        return state

    async def _complete_wizard(
        self,
        state: ConversationState,
        wizard_session: Dict[str, Any]
    ) -> ConversationState:
        """Completa el wizard y guarda la postulación"""

        try:
            # Guardar postulación completa
            async for session in get_async_session():
                postulation = Postulation(
                    conv_id=wizard_session["conv_id"],
                    payload_json=wizard_session["responses"]
                )
                session.add(postulation)
                await session.commit()

                # Actualizar estado del wizard
                await self._update_session_state(wizard_session["id"], "COMPLETED")

                break

            completion_message = """
🎉 **¡Postulación completada exitosamente!**

¡Felicitaciones! Has completado todo el proceso de postulación a Ithaka. 

**¿Qué sigue?**
• Nuestro equipo revisará tu postulación
• En caso de avanzar en el proceso, nos pondremos en contacto contigo
• Recibirás un email de confirmación en tu correo

**Mientras tanto:**
• Puedes seguir desarrollando tu idea
• Síguenos en redes sociales para más recursos
• Participa en nuestras actividades abiertas

¡Te deseamos mucho éxito con tu emprendimiento! 🚀

**¿Hay algo más en lo que pueda ayudarte?**
"""

            # Enviar email de confirmación
            user_email = wizard_session["responses"].get("email")
            user_name = wizard_session["responses"].get("full_name", "").split(
            )[0] if wizard_session["responses"].get("full_name") else "emprendedor"

            if user_email:
                try:
                    send_email_confirmation(user_email, user_name)
                except Exception as e:
                    logger.error(f"Error sending confirmation email: {e}")

            state["agent_context"] = {"response": completion_message}
            state["wizard_state"] = "COMPLETED"
            state["next_action"] = "send_response"
            state["should_continue"] = False
            state["human_feedback_needed"] = False

            return state

        except Exception as e:
            logger.error(f"Error completing wizard: {e}")
            return self._create_error_state(state, "Error completando la postulación")

    async def _show_validation_error(
        self,
        state: ConversationState,
        validation_result: Dict[str, Any],
        wizard_session: Dict[str, Any]
    ) -> ConversationState:
        """Muestra error de validación y pide respuesta nuevamente"""

        question_config = get_question(wizard_session["current_question"])

        error_message = f"""
❌ **Error en tu respuesta:**

{validation_result.get('error', 'Respuesta no válida')}

**Por favor, intenta de nuevo:**

{question_config.get('text', '')}
"""

        state["agent_context"] = {
            "response": error_message,
            "validation_error": True,
            "wizard_session_id": wizard_session["id"]
        }
        state["next_action"] = "send_response"
        state["should_continue"] = False
        state["human_feedback_needed"] = True

        return state

    def _create_error_state(self, state: ConversationState, error_message: str) -> ConversationState:
        """Crea un estado de error"""

        state["agent_context"] = {
            "response": f"❌ Error: {error_message}\n\n¿Hay algo más en lo que pueda ayudarte?",
            "error": True
        }
        state["next_action"] = "send_response"
        state["should_continue"] = False
        state["human_feedback_needed"] = False

        return state

    async def _update_session_state(self, session_id: int, new_state: str):
        """Actualiza el estado de la sesión en BD"""
        try:
            async for session in get_async_session():
                stmt = select(WizardSession).where(
                    WizardSession.id == session_id)
                result = await session.execute(stmt)
                wizard_session = result.scalar_one_or_none()

                if wizard_session:
                    wizard_session.state = new_state
                    await session.commit()
                break
        except Exception as e:
            logger.error(f"Error updating session state: {e}")

    async def _update_session_question(self, session_id: int, question_number: int):
        """Actualiza el número de pregunta actual en BD"""
        try:
            async for session in get_async_session():
                stmt = select(WizardSession).where(
                    WizardSession.id == session_id)
                result = await session.execute(stmt)
                wizard_session = result.scalar_one_or_none()

                if wizard_session:
                    wizard_session.current_question = question_number
                    await session.commit()
                break
        except Exception as e:
            logger.error(f"Error updating session question: {e}")

    async def _update_session_responses(self, session_id: int, responses: Dict[str, Any]):
        """Actualiza las respuestas en BD"""
        try:
            async for session in get_async_session():
                stmt = select(WizardSession).where(
                    WizardSession.id == session_id)
                result = await session.execute(stmt)
                wizard_session = result.scalar_one_or_none()

                if wizard_session:
                    wizard_session.responses = responses
                    await session.commit()
                break
        except Exception as e:
            logger.error(f"Error updating session responses: {e}")

    def _is_cancel_command(self, user_message: str) -> bool:
        """Detecta comandos de cancelación de manera flexible"""
        cancel_patterns = [
            "cancelar", "cancel", "cancelo", "quiero cancelar",
            "quiero salir", "salir", "terminar", "no quiero continuar",
            "abandonar", "parar", "detener", "finalizar",
            "cancelar por favor", "me quiero salir", "ya no quiero"
        ]

        # Verificar si algún patrón está contenido en el mensaje
        for pattern in cancel_patterns:
            if pattern in user_message:
                return True
        return False

    def _is_go_back_command(self, user_message: str) -> bool:
        """Detecta comandos de volver atrás de manera flexible"""
        back_patterns = [
            "volver", "back", "regresar", "anterior", "atras", "atrás",
            "quiero volver", "ir atrás", "pregunta anterior", "paso anterior",
            "volver atrás", "me devuelvo", "retroceder", "hacia atrás",
            "volver por favor", "quiero regresar", "ir para atrás"
        ]

        # Verificar si algún patrón está contenido en el mensaje
        for pattern in back_patterns:
            if pattern in user_message:
                return True
        return False


# Instancia global del agente
wizard_agent = WizardAgent()

# Función para usar en el grafo LangGraph


async def handle_wizard_flow(state: ConversationState) -> ConversationState:
    """Función wrapper para LangGraph"""
    return await wizard_agent.handle_wizard_flow(state)
