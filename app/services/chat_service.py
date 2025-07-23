import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict, Annotated

from app.config.settings import settings
from app.services.wizard_config import (
    WIZARD_STEPS, get_next_step, get_step_by_number, is_wizard_complete
)
from app.services.faq_service import faq_service
from app.schemas.chat_schemas import ChatbotResponse

# Estado del agente conversacional


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    current_step: int
    application_data: Dict[str, Any]
    session_id: str
    conversation_mode: str  # "wizard", "faq", "general"
    validation_errors: List[str]
    show_question: bool  # Nueva bandera para controlar la presentación de la pregunta


class ChatService:
    def __init__(self):
        self.llm = None
        self.graph = None
        self.memory = MemorySaver()
        self._initialize_llm()
        self._build_graph()

    def _initialize_llm(self):
        """Inicializa el modelo de lenguaje"""
        if settings.openai_api_key:
            try:
                self.llm = ChatOpenAI(
                    api_key=settings.openai_api_key,
                    model="gpt-4o-mini",
                    temperature=0.7,
                    max_tokens=1000
                )
                print("LLM OpenAI inicializado")
            except Exception as e:
                print(f"Error inicializando LLM: {e}")
                self.llm = None
        else:
            print("API key de OpenAI no configurada")

    def _build_graph(self):
        """Construye el grafo de LangGraph para el flujo conversacional"""
        if not self.llm:
            print("No se puede construir el grafo sin LLM")
            return

        # Crear el grafo
        workflow = StateGraph(AgentState)

        # Agregar nodos
        workflow.add_node("classify_intent", self._classify_intent)
        workflow.add_node("handle_wizard", self._handle_wizard)
        workflow.add_node("handle_faq", self._handle_faq)
        workflow.add_node("handle_general", self._handle_general)
        workflow.add_node("validate_input", self._validate_input)
        workflow.add_node("generate_response", self._generate_response)

        # Definir flujo
        workflow.add_edge(START, "classify_intent")
        workflow.add_conditional_edges(
            "classify_intent",
            self._route_conversation,
            {
                "wizard": "handle_wizard",
                "faq": "handle_faq",
                "general": "handle_general"
            }
        )
        workflow.add_edge("handle_wizard", "validate_input")
        workflow.add_edge("handle_faq", "generate_response")
        workflow.add_edge("handle_general", "generate_response")
        workflow.add_edge("validate_input", "generate_response")
        workflow.add_edge("generate_response", END)

        # Compilar con memoria
        self.graph = workflow.compile(checkpointer=self.memory)
        print("Grafo de conversación construido")

    def _classify_intent(self, state: AgentState) -> AgentState:
        """Clasifica la intención del usuario"""
        if not self.llm:
            state["conversation_mode"] = "general"
            return state

        last_message = state["messages"][-1].content.lower()
        print(f"DEBUG: Clasificando mensaje: '{last_message}'")

        # Palabras clave para clasificar
        wizard_keywords = ["postular", "formulario",
                           "aplicar", "emprendimiento", "idea", "datos"]
        faq_keywords = ["qué es", "cómo", "cuándo",
                        "dónde", "fellows", "cursos", "help", "ayuda"]

        # Si ya está en modo wizard, continuar en wizard
        if state.get("current_step", 0) > 0:
            state["conversation_mode"] = "wizard"
            print("DEBUG: Modo wizard (current_step > 0)")
        elif any(keyword in last_message for keyword in wizard_keywords):
            state["conversation_mode"] = "wizard"
            print("DEBUG: Modo wizard (keywords)")
        elif any(keyword in last_message for keyword in faq_keywords):
            state["conversation_mode"] = "faq"
            print("DEBUG: Modo FAQ (keywords)")
        else:
            # Usar LLM para clasificar intenciones más complejas
            try:
                classification_prompt = ChatPromptTemplate.from_messages([
                    ("system", """Clasifica la intención del usuario en una de estas categorías:
                    - "wizard": Quiere postular, completar formulario, o hablar sobre su emprendimiento/idea
                    - "faq": Tiene preguntas sobre Ithaka, cursos, programas, o información general
                    - "general": Conversación general, saludos, o temas no relacionados
                    
                    Responde solo con la categoría."""),
                    ("human", "{message}")
                ])

                chain = classification_prompt | self.llm
                result = chain.invoke({"message": last_message})
                classification = result.content.strip().lower()
                print(f"DEBUG: Clasificación LLM: '{classification}'")

                if classification in ["wizard", "faq", "general"]:
                    state["conversation_mode"] = classification
                else:
                    state["conversation_mode"] = "general"

            except Exception as e:
                print(f"Error en clasificación: {e}")
                state["conversation_mode"] = "general"

        print(f"DEBUG: Modo final: {state['conversation_mode']}")
        return state

    def _route_conversation(self, state: AgentState) -> str:
        """Enruta la conversación basado en el modo"""
        return state["conversation_mode"]

    def _handle_wizard(self, state: AgentState) -> AgentState:
        """Maneja el flujo del wizard de postulación"""
        current_step = state.get("current_step", 0)
        application_data = state.get("application_data", {})
        last_message = state["messages"][-1].content

        # Si es el inicio, comenzar con paso 1 sin procesar el mensaje
        if current_step == 0:
            state["current_step"] = 1
            # Marcar que debe mostrar la pregunta
            state["show_question"] = True
        else:
            # Procesar respuesta del usuario para el paso actual
            step = get_step_by_number(current_step)
            processed_value = self._process_user_input(last_message, step)

            if processed_value is not None:
                application_data[step.field_name] = processed_value
                state["application_data"] = application_data

                # Avanzar al siguiente paso
                next_step = get_next_step(current_step, application_data)
                state["current_step"] = next_step
                state["show_question"] = True  # Mostrar la siguiente pregunta

        return state

    def _handle_faq(self, state: AgentState) -> AgentState:
        """Maneja las preguntas frecuentes"""
        last_message = state["messages"][-1].content
        print(f"DEBUG: Buscando FAQs para: '{last_message}'")

        # Buscar FAQs relevantes
        faqs = faq_service.search_faqs(last_message, n_results=2)
        print(f"DEBUG: FAQs encontradas: {len(faqs) if faqs else 0}")

        if faqs:
            # Agregar información de FAQs al estado para usar en la respuesta
            state["faq_results"] = faqs
            print(
                f"DEBUG: Primera FAQ: {faqs[0]['question'] if faqs else 'None'}")
        else:
            state["faq_results"] = []
            print("DEBUG: No se encontraron FAQs")

        return state

    def _handle_general(self, state: AgentState) -> AgentState:
        """Maneja conversación general"""
        # No requiere procesamiento especial
        return state

    def _validate_input(self, state: AgentState) -> AgentState:
        """Valida la entrada del usuario para el paso actual del wizard"""
        current_step = state.get("current_step", 0)
        application_data = state.get("application_data", {})
        show_question = state.get("show_question", False)
        validation_errors = []

        # No validar si debemos mostrar una pregunta nueva
        if show_question:
            state["validation_errors"] = []
            return state

        if current_step > 0 and current_step <= len(WIZARD_STEPS):
            step = get_step_by_number(current_step)
            value = application_data.get(step.field_name)

            # Validar según tipo
            if step.validation_type == "email" and value:
                if not self._validate_email(value):
                    validation_errors.append(
                        "Por favor ingresa un email válido")
            elif step.validation_type == "phone" and value:
                if not self._validate_phone(value):
                    validation_errors.append(
                        "Por favor ingresa un número de teléfono válido")
            elif step.required and not value:
                validation_errors.append("Este campo es obligatorio")

        state["validation_errors"] = validation_errors
        return state

    def _generate_response(self, state: AgentState) -> AgentState:
        """Genera la respuesta final usando el LLM"""
        if not self.llm:
            # Respuesta de fallback sin LLM
            response_msg = AIMessage(
                content="Lo siento, el servicio de IA no está disponible en este momento.")
            state["messages"].append(response_msg)
            return state

        try:
            conversation_mode = state.get("conversation_mode", "general")
            current_step = state.get("current_step", 0)
            application_data = state.get("application_data", {})
            validation_errors = state.get("validation_errors", [])
            show_question = state.get(
                "show_question", True)  # Obtener la bandera

            if conversation_mode == "wizard":
                response = self._generate_wizard_response(
                    current_step, application_data, validation_errors, show_question)
            elif conversation_mode == "faq":
                faq_results = state.get("faq_results", [])
                response = self._generate_faq_response(
                    state["messages"][-1].content, faq_results)
            else:
                response = self._generate_general_response(
                    state["messages"][-1].content)

            state["messages"].append(AIMessage(content=response))
            # Resetear la bandera después de generar la respuesta
            state["show_question"] = False

        except Exception as e:
            print(f"Error generando respuesta: {e}")
            error_msg = AIMessage(
                content="Disculpa, hubo un error procesando tu mensaje. ¿Podrías intentar de nuevo?")
            state["messages"].append(error_msg)
            # Resetear la bandera en caso de error
            state["show_question"] = False

        return state

    def _generate_wizard_response(self, current_step: int, application_data: Dict, validation_errors: List[str], show_question: bool) -> str:
        """Genera respuesta para el flujo del wizard"""
        # Si debemos mostrar una pregunta nueva, ignorar errores de validación
        if show_question:
            if current_step == -1:
                # Wizard completado
                if is_wizard_complete(application_data):
                    return "¡Excelente! Has completado tu postulación exitosamente. Te contactaremos a la brevedad para continuar con el proceso. ¡Gracias por confiar en Ithaka para tu proyecto emprendedor!"
                else:
                    return "Parece que hay algunos datos faltantes. ¿Te gustaría revisar tu postulación?"

            if current_step > 0 and current_step <= len(WIZARD_STEPS):
                step = get_step_by_number(current_step)
                question = step.question

                # Agregar opciones si es un campo de selección
                if step.options:
                    options_text = "\n".join(
                        [f"• {option}" for option in step.options])
                    question += f"\n\nPuedes elegir entre:\n{options_text}"

                return question

            return "¡Hola! Estoy aquí para ayudarte con tu postulación a Ithaka. ¿Estás listo para comenzar?"

        # Si hay errores de validación, mostrarlos
        if validation_errors:
            error_text = " ".join(validation_errors)
            return f"{error_text}. Por favor intenta de nuevo."

        # Fallback - no debería llegar aquí
        return "Continúa con tu respuesta."

    def _generate_faq_response(self, user_question: str, faq_results: List[Dict]) -> str:
        """Genera respuesta basada en FAQs"""
        if not faq_results:
            return """No encontré información específica sobre esa pregunta en nuestras FAQs. 
            
¿Te gustaría que te ayude con tu postulación o tienes alguna otra consulta sobre Ithaka?

Algunas cosas en las que puedo ayudarte:
• Proceso de postulación
• Información sobre cursos y programas
• Programa Fellows
• Recursos para emprendedores"""

        # Usar la FAQ más relevante
        best_faq = faq_results[0]
        response = f"**{best_faq['question']}**\n\n{best_faq['answer']}"

        # Si hay más resultados relevantes, mencionarlos
        if len(faq_results) > 1:
            response += "\n\n**También podrías estar interesado en:**"
            for faq in faq_results[1:]:
                response += f"\n• {faq['question']}"

        response += "\n\n¿Hay algo más en lo que pueda ayudarte?"

        return response

    def _generate_general_response(self, user_message: str) -> str:
        """Genera respuesta para conversación general"""
        try:
            system_prompt = f"""Eres un asistente amigable de Ithaka, el centro de emprendimiento e innovación de la UCU. 
            
Tu objetivo es:
1. Responder de manera amigable y motivadora
2. Dirigir la conversación hacia cómo puedes ayudar con postulaciones o información sobre Ithaka
3. Mantener un tono profesional pero cercano
4. Ser breve y conciso

Contexto de Ithaka: {settings.ithaka_context}"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]

            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            print(f"Error en respuesta general: {e}")
            return "¡Hola! Soy tu asistente de Ithaka. ¿En qué puedo ayudarte hoy? Puedo ayudarte con tu postulación o responder preguntas sobre nuestros programas."

    def _process_user_input(self, user_input: str, step) -> Any:
        """Procesa la entrada del usuario según el tipo de campo"""
        input_clean = user_input.strip()

        if step.validation_type == "boolean":
            # Detectar respuestas sí/no
            if any(word in input_clean.lower() for word in ["sí", "si", "yes", "afirmativo", "correcto", "exacto"]):
                return True
            elif any(word in input_clean.lower() for word in ["no", "not", "negativo", "incorrecto"]):
                return False
            return None
        elif step.validation_type == "select":
            # Encontrar opción que coincida
            for option in step.options:
                if option.lower() in input_clean.lower():
                    return option
            return input_clean  # Retornar input original si no hay coincidencia exacta
        elif step.validation_type == "multiple_select":
            # Detectar múltiples opciones
            selected = []
            for option in step.options:
                if option.lower() in input_clean.lower():
                    selected.append(option)
            return ", ".join(selected) if selected else input_clean
        else:
            return input_clean

    def _validate_email(self, email: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _validate_phone(self, phone: str) -> bool:
        """Valida formato de teléfono"""
        # Aceptar varios formatos de teléfono
        pattern = r'^[\+]?[1-9]?[\d\s\-\(\)]{8,15}$'
        return re.match(pattern, phone.replace(" ", "")) is not None

    async def process_message(self, message: str, session_id: str, conversation_data: Dict = None) -> ChatbotResponse:
        """
        Procesa un mensaje del usuario y retorna la respuesta
        """
        if not self.graph:
            return ChatbotResponse(
                message="El servicio de IA no está disponible en este momento.",
                message_type="error"
            )

        try:
            # Preparar estado inicial
            initial_state = {
                "messages": [HumanMessage(content=message)],
                "current_step": conversation_data.get("current_step", 0) if conversation_data else 0,
                "application_data": conversation_data.get("application_data", {}) if conversation_data else {},
                "session_id": session_id,
                "conversation_mode": "general",
                "validation_errors": [],
                "show_question": True  # Inicializar la bandera
            }

            # Configuración para memoria persistente
            config = {"configurable": {"thread_id": session_id}}

            # Ejecutar el grafo
            result = self.graph.invoke(initial_state, config)

            # Extraer respuesta
            last_ai_message = None
            for msg in reversed(result["messages"]):
                if isinstance(msg, AIMessage):
                    last_ai_message = msg
                    break

            response_text = last_ai_message.content if last_ai_message else "No se pudo generar una respuesta."

            # Preparar metadata de respuesta
            metadata = {
                "current_step": result.get("current_step", 0),
                "application_data": result.get("application_data", {}),
                "conversation_mode": result.get("conversation_mode", "general")
            }

            return ChatbotResponse(
                message=response_text,
                message_type="text",
                next_step=result.get("current_step"),
                validation_errors=result.get("validation_errors"),
                meta_data=metadata
            )

        except Exception as e:
            print(f"Error procesando mensaje: {e}")
            return ChatbotResponse(
                message="Disculpa, hubo un error procesando tu mensaje. ¿Podrías intentar de nuevo?",
                message_type="error"
            )


# Instancia global del servicio
chat_service = ChatService()
