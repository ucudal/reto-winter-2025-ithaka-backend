from typing import Any


def fallback_agent_node(state: dict[str, Any]) -> dict[str, Any]:
    state['response'] = "No entendí tu intención. ¿Podés reformular tu consulta?"
    return state