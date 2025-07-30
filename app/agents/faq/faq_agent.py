from typing import Dict, Any

def faq_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state['response'] = "Esta es una respuesta automática de FAQ."
    return state