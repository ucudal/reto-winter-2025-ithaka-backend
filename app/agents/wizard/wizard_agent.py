from typing import Dict, Any

def wizard_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state['response'] = "Perfecto, iniciamos el proceso de postulación."
    return state