import logging

INTENT_KEYWORDS = {
    "postulacion": ["postular", "postulación", "aplicar", "trabajo", "meter", "meterme"],
    "faq": ["horario", "requisito", "pregunta frecuente", "contacto", "dónde queda", "pregunta"]
}

def detect_intent(text: str) -> str:
    if not text or not isinstance(text, str):
        logging.warning("Invalid input for intent detection")
        return "fallback"

    text = text.lower()

    if any(word in text for word in INTENT_KEYWORDS["postulacion"]):
        return "postulacion"
    if any(word in text for word in INTENT_KEYWORDS["faq"]):
        return "faq"

    logging.info(f"No intent detected for message: {text[:50]}...")
    return "fallback"

def supervisor_node(state: dict) -> dict:
    if not isinstance(state, dict) or 'user_message' not in state:
        logging.error("Invalid state passed to supervisor_node")
        state['intent'] = "fallback"
        return state

    user_message = state['user_message']

    if not user_message:
        state['intent'] = "fallback"
        return state

    intent = detect_intent(user_message)
    logging.info(f"Detected intent: {intent} for message: {user_message[:50]}...")

    if intent == "postulacion":
        state['intent'] = "wizard_agent"
    elif intent == "faq":
        state['intent'] = "faq_agent"
    else:
        state['intent'] = "fallback"
    return state