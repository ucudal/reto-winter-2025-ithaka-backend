def fallback_agent_node(state: dict) -> dict:
    state['response'] = "No entendí tu intención. ¿Podés reformular tu consulta?"
    return state