from typing import Dict, Any


def fallback_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state['response'] = "No entendí tu intención. ¿Podés reformular tu consulta?"
    return state