"""
Agente Supervisor - Router principal del sistema
Analiza la intención del usuario y decide a qué agente derivar
"""

import os
from openai import AsyncOpenAI
from ..graph.state import ConversationState
import logging

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """Agente supervisor que analiza intenciones y rutea conversaciones"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    async def route_message(self, state: ConversationState) -> ConversationState:
        """Analiza el mensaje del usuario y decide el routing"""

        user_message = state["user_message"].lower().strip()
        chat_history = state.get("chat_history", [])
        # conversation_id = state.get("conversation_id") # TODO: Agregar cuando esté disponible

        # TODO: Verificar sesiones activas del wizard cuando esté disponible
        # if state.get("wizard_session_id") and state.get("wizard_state") == "ACTIVE":
        #     logger.info("Routing to wizard - active session detected in state")
        #     return self._route_to_wizard(state)

        # TODO: Verificar sesiones en BD cuando wizard esté disponible
        # if conversation_id:
        #     active_wizard_session = await self._check_active_wizard_session(conversation_id)
        #     if active_wizard_session:
        #         logger.info(f"Routing to wizard - active session {active_wizard_session['id']} found in DB")
        #         state["wizard_session_id"] = active_wizard_session["id"]
        #         state["wizard_state"] = active_wizard_session["state"]
        #         state["current_question"] = active_wizard_session["current_question"]
        #         state["wizard_responses"] = active_wizard_session["responses"]
        #         return self._route_to_wizard(state)

        # Análisis de intención usando patrones simples primero
        intention = self._analyze_intention_simple(user_message)

        # Si no hay claridad, usar IA para análisis más profundo
        if intention == "unclear":
            intention = await self._analyze_intention_with_ai(user_message, chat_history)

        # Actualizar estado según la intención
        state["supervisor_decision"] = intention
        state["current_agent"] = intention

        logger.info(
            f"Supervisor decision: {intention} for message: {user_message[:50]}")

        return state

    def _analyze_intention_simple(self, message: str) -> str:
        """Análisis simple de intención basado en palabras clave"""

        # TODO: Patrones para wizard cuando esté disponible
        # wizard_keywords = [
        #     "postular", "emprender", "formulario", "idea", "negocio",
        #     "startup", "proyecto", "emprendimiento", "incubadora",
        #     "quiero postular", "tengo una idea"
        # ]

        # Patrones para FAQ
        faq_keywords = [
            "pregunta", "consulta", "información", "qué es", "cómo",
            "cuándo", "dónde", "programa", "curso", "fellows", "minor",
            "actividades", "contacto", "campus", "costo"
        ]

        # TODO: Comandos del wizard cuando esté disponible
        # wizard_commands = ["volver", "cancelar", "continuar", "siguiente"]

        # TODO: Verificar comandos del wizard cuando esté disponible
        # if any(cmd in message for cmd in wizard_commands):
        #     return "wizard"

        # TODO: Verificar patrones de postulación cuando wizard esté disponible
        # if any(keyword in message for keyword in wizard_keywords):
        #     return "wizard"

        # Verificar patrones de FAQ
        if any(keyword in message for keyword in faq_keywords):
            return "faq"

        # Si no match, necesita análisis más profundo
        return "unclear"

    async def _analyze_intention_with_ai(self, message: str, history: list) -> str:
        """Análisis de intención usando IA cuando no hay claridad"""

        try:
            # Construir contexto de la conversación
            context = ""
            if history:
                # Últimos 3 mensajes para contexto
                last_messages = history[-3:]
                context = "\n".join(
                    [f"{msg['role']}: {msg['content']}" for msg in last_messages])

            prompt = f"""
Analiza la intención del usuario en este mensaje y determina a qué agente debe dirigirse.

CONTEXTO DE CONVERSACIÓN:
{context}

MENSAJE ACTUAL DEL USUARIO:
"{message}"

REGLAS DE CLASIFICACIÓN:
- "faq" - SIEMPRE para preguntas sobre: programas (Fellows, minor), cursos, información de Ithaka, costos, convocatorias, campus, requisitos, actividades. Incluye preguntas indirectas como "podrías explicarme...", "sabes sobre...", "me gustaría saber..."
- TODO: "validator" - SOLO para validar datos específicos cuando esté disponible
- TODO: "wizard" - SOLO para postular ideas/proyectos cuando esté disponible

EJEMPLOS:
- "¿Qué es el programa Fellows?" → faq
- "no se si podrías explicarme qué es el programa fellows?" → faq  
- "sabes sobre los cursos de Ithaka?" → faq
- TODO: "valida este email: test@test.com" → validator (cuando esté disponible)
- TODO: "quiero postular mi idea" → wizard (cuando esté disponible)

Responde ÚNICAMENTE con una palabra: faq
"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un router experto que analiza intenciones del usuario."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )

            intention = response.choices[0].message.content.strip().lower()

            # Validar respuesta
            # TODO: Agregar "validator" y "wizard" cuando estén disponibles
            if intention in ["faq"]:
                return intention
            else:
                logger.warning(f"Invalid AI intention response: {intention}")
                return "faq"  # Default fallback

        except Exception as e:
            logger.error(f"Error in AI intention analysis: {e}")
            return "faq"  # Safe fallback

    # TODO: Implementar cuando wizard esté disponible
    # def _route_to_wizard(self, state: ConversationState) -> ConversationState:
    #     """Rutea específicamente al wizard"""
    #     state["supervisor_decision"] = "wizard"
    #     state["current_agent"] = "wizard"
    #     return state

    # TODO: Implementar cuando wizard esté disponible
    # async def _check_active_wizard_session(self, conversation_id: int) -> Optional[Dict[str, Any]]:
    #     """Verifica si hay una sesión activa del wizard en la base de datos"""
    #     try:
    #         async for session in get_async_session():
    #             stmt = select(WizardSession).where(
    #                 WizardSession.conv_id == conversation_id,
    #                 WizardSession.state.in_(["ACTIVE", "PAUSED", "STARTING"])
    #             )
    #             result = await session.execute(stmt)
    #             active_session = result.scalar_one_or_none()
    #             if active_session:
    #                 return {
    #                         "id": active_session.id,
    #                         "conv_id": active_session.conv_id,
    #                         "current_question": active_session.current_question,
    #                         "responses": active_session.responses or {},
    #                         "state": active_session.state
    #                     }
    #             break
    #     except Exception as e:
    #         logger.error(f"Error checking active wizard session: {e}")
    #     return None

    def decide_next_agent(self, state: ConversationState) -> str:
        """Decide el próximo agente en el flujo del grafo"""

        current_agent = state.get("current_agent", "supervisor")
        supervisor_decision = state.get("supervisor_decision")

        # Si hay decisión del supervisor, seguir esa ruta
        # TODO: Agregar "validator" y "wizard" cuando estén disponibles
        if supervisor_decision in ["faq"]:
            return supervisor_decision

        # Si no hay decisión clara, ir a FAQ como default
        return "faq"


# Instancia global del agente
supervisor_agent = SupervisorAgent()

# Función para usar en el grafo LangGraph


async def route_message(state: ConversationState) -> ConversationState:
    """Función wrapper para LangGraph"""
    return await supervisor_agent.route_message(state)


def decide_next_agent(state: ConversationState) -> str:
    """Función wrapper para routing condicional en LangGraph"""
    return supervisor_agent.decide_next_agent(state)
