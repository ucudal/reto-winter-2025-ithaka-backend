def detect_intent(text: str) -> str:
    text = text.lower()
    postulacion_keywords = ["postular", "postulación", "aplicar", "trabajo", "meter", "meterme"]
    faq_keywords = ["horario", "requisito", "pregunta frecuente", "contacto", "dónde queda", "pregunta"]

    if any(word in text for word in postulacion_keywords):
        return "postulacion"
    if any(word in text for word in faq_keywords):
        return "faq"
    return "fallback"

def supervisor_node(state: dict) -> dict:
    user_message = state['user_message']
    intent = detect_intent(user_message)
    if intent == "postulacion":
        state['intent'] = "wizard_agent"
    elif intent == "faq":
        state['intent'] = "faq_agent"
    else:
        state['intent'] = "fallback"
    return state