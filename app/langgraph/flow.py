import logging
from functools import lru_cache
from typing import TypedDict

from langgraph.constants import END
from langgraph.graph import StateGraph

from app.agents.fallback.fallback_agent import fallback_agent_node
from app.agents.faq.faq_agent import faq_agent_node
from app.agents.supervisor.supervisor_agent import supervisor_node
from app.agents.wizard.wizard_agent import wizard_agent_node


class ChatState(TypedDict, total=False):
    user_message: str
    intent: str
    response: str

def _route_intent(state: dict) -> str:
    intent = state.get('intent', 'fallback')
    valid_intents = {'wizard_agent', 'faq_agent', 'fallback'}

    if intent not in valid_intents:
        logging.warning(f"Invalid intent detected: {intent}, routing to fallback")
        return 'fallback'

    return intent

@lru_cache(maxsize=1)
def _get_compiled_graph():
    return build_graph()

def build_graph():
    graph = StateGraph(ChatState)

    graph.add_node('supervisor', supervisor_node)
    graph.add_node('wizard_agent', wizard_agent_node)
    graph.add_node('faq_agent', faq_agent_node)
    graph.add_node('fallback', fallback_agent_node)

    graph.add_conditional_edges(
        "supervisor",
        _route_intent,
        path_map={
            'wizard_agent': 'wizard_agent',
            'faq_agent': 'faq_agent',
            'fallback': 'fallback',
        }
    )

    graph.add_edge('wizard_agent', END)
    graph.add_edge('faq_agent', END)
    graph.add_edge('fallback', END)

    graph.set_entry_point('supervisor')
    return graph.compile()

def run_flow(user_message: str) -> str:
    try:
        if not user_message or not isinstance(user_message, str):
            logging.warning("Invalid user message provided")
            return 'Mensaje inválido.'
        graph = _get_compiled_graph()
        state = {'user_message': user_message.strip()}

        logging.info(f"Processing message: {user_message[:50]}...")
        final_state = graph.invoke(state)

        response = final_state.get('response', 'No hubo respuesta.')
        logging.info(f"Generated response: {response[:50]}...")
        return response

    except Exception as e:
        logging.error(f"Error in run_flow: {str(e)}")
        return 'Error procesando la consulta. Por favor intenta nuevamente.'
