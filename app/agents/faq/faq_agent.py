from typing import Any


def faq_agent_node(state: dict[str, Any]) -> dict[str, Any]:
    state['response'] = "Esta es una respuesta automática de FAQ."
    return state