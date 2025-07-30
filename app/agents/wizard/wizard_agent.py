from typing import Any


def wizard_agent_node(state: dict[str, Any]) -> dict[str, Any]:
    state['response'] = "Perfecto, iniciamos el proceso de postulación."
    return state