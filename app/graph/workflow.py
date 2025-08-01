"""
Workflow principal de LangGraph para orquestar todos los agentes del sistema Ithaka
"""

from datetime import datetime
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from .state import ConversationState
from ..agents.supervisor import route_message, decide_next_agent
from ..agents.wizard import handle_wizard_flow
from ..agents.faq import handle_faq_query
# TODO: Integrar validator cuando esté disponible
# from ..agents.validator import validate_data
import logging

logger = logging.getLogger(__name__)


class IthakaWorkflow:
    """Workflow principal que maneja toda la lógica de conversación"""

    def __init__(self):
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Construye el grafo de estados LangGraph"""

        # Crear el grafo con el estado compartido
        workflow = StateGraph(ConversationState)

        # Agregar nodos (agentes)
        workflow.add_node("supervisor", route_message)
        workflow.add_node("wizard", handle_wizard_flow)
        workflow.add_node("faq", handle_faq_query)
        # TODO: Agregar validator node cuando esté disponible
        # workflow.add_node("validator", validate_data)

        # Definir punto de entrada
        workflow.set_entry_point("supervisor")

        # Agregar bordes condicionales desde el supervisor
        workflow.add_conditional_edges(
            "supervisor",
            decide_next_agent,
            {
                "wizard": "wizard",
                "faq": "faq",
                # TODO: Agregar validator cuando esté disponible
                # "validator": "validator",
                "end": END
            }
        )

        # El wizard puede continuar consigo mismo o terminar
        workflow.add_conditional_edges(
            "wizard",
            self._wizard_should_continue,
            {
                "continue": "wizard",
                "end": END
            }
        )

        # Los otros agentes terminan el flujo
        workflow.add_edge("faq", END)
        # TODO: Agregar validator edge cuando esté disponible
        # workflow.add_edge("validator", END)

        # Compilar el grafo
        return workflow.compile()

    def _wizard_should_continue(self, state: ConversationState) -> str:
        """Determina si el wizard debe continuar o terminar"""
        wizard_state = state.get("wizard_state", "INACTIVE")
        next_action = state.get("next_action", "complete")
        
        # Si el wizard está activo y necesita continuar, mantener el flujo
        if wizard_state == "ACTIVE" and next_action == "send_response":
            return "continue"
        
        # Si está completado o hay error, terminar
        if wizard_state in ["COMPLETED", "ERROR"]:
            return "end"
        
        # Si no hay decisión clara, terminar
        return "end"

    async def process_message(
        self,
        user_message: str,
        conversation_id: int = None,
        chat_history: list = None,
        user_email: str = None
    ) -> Dict[str, Any]:
        """Procesa un mensaje del usuario a través del grafo de agentes"""

        try:
            # Crear estado inicial como diccionario
            initial_state = {
                "conversation_id": conversation_id,
                "user_message": user_message,
                "chat_history": chat_history or [],
                "user_email": user_email,
                "user_name": None,
                "current_agent": "supervisor",
                "agent_context": {},
                "wizard_session_id": None,
                "current_question": 1,
                "wizard_responses": {},
                "wizard_state": "INACTIVE",
                "supervisor_decision": None,
                "faq_results": None,
                "validation_results": None,
                "next_action": "process",
                "should_continue": True,
                "human_feedback_needed": False,
                "timestamp": datetime.now(),
                "session_data": {}
            }

            # Ejecutar el grafo
            logger.info(f"Processing message: {user_message[:50]}...")
            result = await self.graph.ainvoke(initial_state)

            # Extraer información relevante del resultado
            response_data = {
                "response": result.get("agent_context", {}).get("response", "Lo siento, no pude procesar tu mensaje."),
                "agent_used": result.get("current_agent", "unknown"),
                "conversation_id": result.get("conversation_id"),
                "wizard_session_id": result.get("wizard_session_id"),
                "wizard_state": result.get("wizard_state", "INACTIVE"),
                "current_question": result.get("current_question"),
                "human_feedback_needed": result.get("human_feedback_needed", False),
                "human_validation_needed": result.get("human_validation_needed", False),
                "should_continue": result.get("should_continue", False),
                "next_action": result.get("next_action", "complete"),
                "faq_results": result.get("faq_results"),
                "validation_results": result.get("validation_results"),
                "session_data": result.get("session_data", {})
            }

            logger.info(
                f"Message processed successfully by {response_data['agent_used']}")
            return response_data

        except Exception as e:
            raise e
            logger.error(f"Error processing message through workflow: {e}")

            # Respuesta de fallback
            return {
                "response": "Lo siento, tuve un problema técnico procesando tu mensaje. ¿Podrías intentar de nuevo?",
                "agent_used": "error_handler",
                "conversation_id": conversation_id,
                "wizard_session_id": None,
                "wizard_state": "INACTIVE",
                "current_question": 1,
                "human_feedback_needed": False,
                "should_continue": False,
                "next_action": "complete",
                "error": str(e)
            }


# Instancia global del workflow
ithaka_workflow = IthakaWorkflow()

# Función de conveniencia para usar desde otros módulos


async def process_user_message(
    user_message: str,
    conversation_id: int = None,
    chat_history: list = None,
    user_email: str = None
) -> Dict[str, Any]:
    """Función de conveniencia para procesar mensajes de usuario"""
    return await ithaka_workflow.process_message(
        user_message=user_message,
        conversation_id=conversation_id,
        chat_history=chat_history,
        user_email=user_email
    )
