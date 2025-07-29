from langgraph.graph import StateGraph
from app.agents.end.end import end_node
from app.agents.fallback.fallback_agent import fallback_agent_node
from app.agents.supervisor.supervisor_agent import supervisor_node
from app.agents.wizard.wizard_agent import wizard_agent_node
from app.agents.faq.faq_agent import faq_agent_node
from typing import TypedDict

class ChatState(TypedDict, total=False):
    user_message: str
    intent: str
    response: str

def build_graph():
    graph = StateGraph(ChatState)

    graph.add_node('end', end_node)
    graph.add_node('supervisor', supervisor_node)
    graph.add_node('wizard_agent', wizard_agent_node)
    graph.add_node('faq_agent', faq_agent_node)
    graph.add_node('fallback', fallback_agent_node)

    graph.add_conditional_edges(
        "supervisor",
        lambda state: state['intent'],
        path_map={
            'wizard_agent': 'wizard_agent',
            'faq_agent': 'faq_agent',
            'fallback': 'fallback',
        }
    )

    graph.add_edge('wizard_agent', 'end')
    graph.add_edge('faq_agent', 'end')
    graph.add_edge('fallback', 'end')

    graph.set_entry_point('supervisor')
    return graph.compile()

def run_flow(user_message: str) -> str:
    graph = build_graph()
    state = {'user_message': user_message}
    final_state = graph.invoke(state)
    return final_state.get('response', 'No hubo respuesta.')
