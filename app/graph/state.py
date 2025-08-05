from typing import Optional, Any

from typing_extensions import TypedDict


class WizardQuestionState(TypedDict):
    """Estado específico para una pregunta del wizard"""
    question_number: int
    question_text: str
    question_type: str  # "personal", "evaluativa", "opcional"
    user_response: Optional[str]
    is_valid: bool
    validation_errors: list[str]
    evaluation_feedback: Optional[str]
    needs_improvement: bool
    iteration_count: int


# Definir ConversationState como un diccionario normal para compatibilidad con LangGraph
ConversationState = dict[str, Any]
