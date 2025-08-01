"""
Agente Wizard - Maneja formularios interactivos para postulación de proyectos
"""

import os
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI
from ..graph.state import ConversationState
from .validation_agent import ValidationAgent
import logging
import json
from copilotkit import CopilotKitState

logger = logging.getLogger(__name__)

class WizardAgent:
    """Agente para manejar formularios interactivos de postulación"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.validation = ValidationAgent()
        self._initialize_nodes()
    
    def _initialize_nodes(self):
        """Inicializa los nodos del formulario usando TypedDict"""
        self.nodes: Dict[str, Dict[str, Any]] = {
            "welcome": {
                "node_id": "welcome",
                "node_type": "welcome",
                "content": "¡Bienvenido al formulario de postulación de Ithaka!\n\nTe guiaré paso a paso para completar tu postulación.",
                "next": "full_name",
                "prev": None,
                "id": None,
                "example": None,
                "validation": None,
                "error_msg": None,
                "options": None,
                "required": False
            },
            "full_name": {
                "node_id": "full_name",
                "node_type": "question",
                "content": "1. Por favor ingresa tu nombre completo",
                "example": "Ejemplo: Juan Pérez o Pérez, Juan",
                "validation": "Extrae el nombre en formato 'Apellido, Nombre'.",
                "error_msg": "No pude identificar tu nombre completo. Por favor usa: Apellido, Nombre",
                "next": "email",
                "prev": "welcome",
                "id": "full_name",
                "options": None,
                "required": True
            },
            "email": {
                "node_id": "email",
                "node_type": "question",
                "content": "2. Ingresa tu correo electrónico",
                "example": "Ejemplo: juan@ejemplo.com",
                "validation": "Extrae la dirección de correo electrónico válida.",
                "error_msg": "Correo electrónico inválido. Por favor ingresa un correo válido.",
                "next": "location",
                "prev": "full_name",
                "id": "email",
                "options": None,
                "required": True
            },
            "location": {
                "node_id": "location",
                "node_type": "multiple_choice",
                "content": "3. Selecciona tu país y localidad de residencia",
                "options": [
                    {"value": "montevideo", "label": "Uruguay - Montevideo"},
                    {"value": "interior", "label": "Uruguay - Interior"},
                    {"value": "otro", "label": "Otro país"}
                ],
                "error_msg": "Por favor selecciona una opción válida.",
                "next": "support_needed",
                "prev": "email",
                "id": "location",
                "example": None,
                "validation": None,
                "required": True
            },
            "support_needed": {
                "node_id": "support_needed",
                "node_type": "multiselect",
                "content": "4. Indica cuál de estos apoyos necesitas de Ithaka (Puedes seleccionar varios)",
                "options": [
                    {"value": "tutoria", "label": "Tutoría para validar la idea"},
                    {"value": "plan_negocios", "label": "Soporte para armar el plan de negocios"},
                    {"value": "financiamiento", "label": "Ayuda para obtener financiamiento"},
                    {"value": "capacitacion", "label": "Capacitación"},
                    {"value": "tema_especifico", "label": "Ayuda para un tema específico"},
                    {"value": "otro", "label": "Otro"}
                ],
                "error_msg": "Por favor selecciona al menos una opción.",
                "next": "completion",
                "prev": "location",
                "id": "support_needed",
                "example": None,
                "validation": None,
                "required": True
            },
            "completion": {
                "node_id": "completion",
                "node_type": "completion",
                "content": "¡Gracias por completar el formulario! Hemos recibido tus respuestas.",
                "next": None,
                "prev": "support_needed",
                "id": None,
                "example": None,
                "validation": None,
                "error_msg": None,
                "options": None,
                "required": False
            }
        }

    async def handle_wizard_flow(self, state: ConversationState) -> ConversationState:
        """Maneja el flujo del wizard en el contexto de LangGraph"""
        
        user_message = state["user_message"]
        wizard_state = state.get("wizard_state", "INACTIVE")
        current_question = state.get("current_question", 1)
        wizard_responses = state.get("wizard_responses", {})

        try:
            # Si es la primera vez, iniciar el wizard
            if wizard_state == "INACTIVE":
                return await self._start_wizard(state)
            
            # Si ya está activo, procesar la respuesta
            if wizard_state == "ACTIVE":
                return await self._process_wizard_response(state)
            
            # Si está completado, mostrar resumen
            if wizard_state == "COMPLETED":
                return await self._show_completion_summary(state)

        except Exception as e:
            raise e
            logger.error(f"Error in wizard flow: {e}")
            return self._handle_wizard_error(state, str(e))

        return state

    async def _start_wizard(self, state: ConversationState) -> ConversationState:
        """Inicia el wizard"""
        try:
            # Inicializar estado del wizard
            state["wizard_state"] = "ACTIVE"
            state["current_question"] = 1
            state["wizard_responses"] = {}
            state["wizard_session_id"] = f"wizard_{state.get('conversation_id', 'new')}"
            
            # Obtener primera pregunta
            current_node = self.nodes["welcome"]
            response = self._format_node_response(current_node)
            
            state["agent_context"] = {
                "response": response,
                "wizard_started": True,
                "current_node": current_node["node_id"]
            }
            state["next_action"] = "send_response"
            state["should_continue"] = False
            
            return state
            
        except Exception as e:
            raise e
            logger.error(f"Error starting wizard: {e}")
            return self._handle_wizard_error(state, str(e))

    async def _process_wizard_response(self, state: ConversationState) -> ConversationState:
        """Procesa la respuesta del usuario en el wizard"""
        try:
            user_message = state["user_message"]
            current_question = state.get("current_question", 1)
            wizard_responses = state.get("wizard_responses", {})
            
            # Verificar si estamos esperando validación humana
            if state.get("human_validation_needed"):
                return await self._handle_human_validation_response(state, user_message)
            
            # Determinar el nodo actual basado en la pregunta
            current_node_id = self._get_node_id_by_question(current_question)
            current_node = self.nodes[current_node_id]
            
            # Procesar comandos especiales
            if user_message.lower() in ["atras", "back", "anterior"]:
                return await self._go_back(state)
            
            if user_message.lower() in ["guardar", "save", "pausar"]:
                return await self._save_progress(state)
            
            # Procesar respuesta según tipo de nodo
            if current_node["node_type"] == "welcome":
                return await self._advance_to_next(state, current_node)
            
            elif current_node["node_type"] == "question":
                result = await self._process_question_response(state, current_node, user_message)
            
            elif current_node["node_type"] == "multiple_choice":
                result = await self._process_multiple_choice_response(state, current_node, user_message)
            
            elif current_node["node_type"] == "multiselect":
                result = await self._process_multiselect_response(state, current_node, user_message)
            
            elif current_node["node_type"] == "completion":
                return await self._complete_wizard(state)
            
            else:
                result = {"error": "Tipo de nodo no soportado"}
            
            # Si hay error, mantener en la misma pregunta
            if "error" in result:
                state["agent_context"] = {
                    "response": result["error"],
                    "current_node": current_node["node_id"],
                    "validation_error": True
                }
                state["next_action"] = "send_response"
                state["should_continue"] = False
                return state
            
            # Si se necesita validación humana
            if result.get("status") == "human_validation_needed":
                state["agent_context"] = {
                    "response": result["message"],
                    "current_node": current_node["node_id"],
                    "human_validation_needed": True,
                    "pending_validation": user_message
                }
                state["next_action"] = "send_response"
                state["should_continue"] = False
                return state
            
            # Avanzar al siguiente nodo
            return await self._advance_to_next(state, current_node)
            
        except Exception as e:
            raise e
            logger.error(f"Error processing wizard response: {e}")
            return self._handle_wizard_error(state, str(e))

    async def _handle_human_validation_response(self, state: ConversationState, user_response: str) -> ConversationState:
        """Maneja la respuesta de validación humana"""
        try:
            pending_validation = state.get("pending_validation", "")
            current_node_id = state.get("current_node")
            current_node = self.nodes[current_node_id]
            
            # Si el usuario confirma, usar la respuesta original
            if user_response.lower() in ["sí", "si", "yes", "confirmar", "confirm", "ok", "correcto"]:
                validated_result = pending_validation
            else:
                # Si el usuario corrige, validar la nueva entrada
                validated_result = await self.validation.validate_question(user_response, current_node["validation"])
                if validated_result == "HUMAN_VALIDATION_NEEDED":
                    validated_result = user_response  # Usar la entrada del usuario directamente
            
            # Guardar respuesta validada
            wizard_responses = state.get("wizard_responses", {})
            wizard_responses[current_node["id"]] = validated_result
            state["wizard_responses"] = wizard_responses
            
            # Limpiar estado de validación humana
            state["human_validation_needed"] = False
            state["pending_validation"] = None
            
            # Avanzar al siguiente nodo
            return await self._advance_to_next(state, current_node)
            
        except Exception as e:
            raise e
            logger.error(f"Error handling human validation: {e}")
            return self._handle_wizard_error(state, str(e))

    async def _process_question_response(self, state: ConversationState, node: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Procesa respuesta de pregunta abierta"""
        try:
            # Validar usando el agente de validación
            validated = await self.validation.validate_question(user_input, node["validation"])
            
            # Si se necesita validación humana
            if validated == "HUMAN_VALIDATION_NEEDED":
                return {
                    "status": "human_validation_needed",
                    "message": f"Necesito validación humana para: '{user_input}'. Por favor confirma o corrige la información."
                }
            
            if not validated:
                return {"error": node["error_msg"]}
            
            # Guardar respuesta validada
            wizard_responses = state.get("wizard_responses", {})
            wizard_responses[node["id"]] = validated
            state["wizard_responses"] = wizard_responses
            
            return {"status": "success"}
            
        except Exception as e:
            raise e
            logger.error(f"Error validating question response: {e}")
            return {"error": "Ocurrió un error al validar tu respuesta"}

    async def _process_multiple_choice_response(self, state: ConversationState, node: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Procesa respuesta de selección única"""
        try:
            if not node["options"]:
                return {"error": "Opciones no definidas"}
            
            # Buscar opción seleccionada
            selected_option = None
            user_input_lower = user_input.lower().strip()
            
            for option in node["options"]:
                if (user_input_lower == option["value"].lower() or 
                    user_input_lower == option["label"].lower() or
                    user_input_lower in option["label"].lower()):
                    selected_option = option
                    break
            
            if not selected_option:
                # Mostrar opciones disponibles
                options_text = "\n".join([f"• {opt['label']}" for opt in node["options"]])
                return {"error": f"Por favor selecciona una de estas opciones:\n{options_text}"}
            
            # Guardar respuesta
            wizard_responses = state.get("wizard_responses", {})
            wizard_responses[node["id"]] = selected_option["value"]
            state["wizard_responses"] = wizard_responses
            
            return {"status": "success"}
            
        except Exception as e:
            raise e
            logger.error(f"Error processing multiple choice: {e}")
            return {"error": node["error_msg"]}

    async def _process_multiselect_response(self, state: ConversationState, node: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Procesa respuesta de selección múltiple"""
        try:
            if not node["options"]:
                return {"error": "Opciones no definidas"}
            
            # Parsear selecciones múltiples
            selections = [s.strip().lower() for s in user_input.split(",")]
            selected_values = []
            
            for selection in selections:
                for option in node["options"]:
                    if (selection == option["value"].lower() or 
                        selection == option["label"].lower() or
                        selection in option["label"].lower()):
                        selected_values.append(option["value"])
                        break
            
            if not selected_values and node["required"]:
                options_text = "\n".join([f"• {opt['label']}" for opt in node["options"]])
                return {"error": f"Por favor selecciona al menos una opción:\n{options_text}"}
            
            # Guardar respuesta
            wizard_responses = state.get("wizard_responses", {})
            wizard_responses[node["id"]] = selected_values
            state["wizard_responses"] = wizard_responses
            
            return {"status": "success"}
            
        except Exception as e:
            raise e
            logger.error(f"Error processing multiselect: {e}")
            return {"error": node["error_msg"]}

    async def _advance_to_next(self, state: ConversationState, current_node: Dict[str, Any]) -> ConversationState:
        """Avanza al siguiente nodo"""
        if not current_node["next"]:
            return await self._complete_wizard(state)
        
        # Actualizar pregunta actual
        next_question = state.get("current_question", 1) + 1
        state["current_question"] = next_question
        
        # Obtener siguiente nodo
        next_node = self.nodes[current_node["next"]]
        response = self._format_node_response(next_node)
        
        state["agent_context"] = {
            "response": response,
            "current_node": next_node["node_id"],
            "question_number": next_question
        }
        state["next_action"] = "send_response"
        state["should_continue"] = False
        
        return state

    async def _go_back(self, state: ConversationState) -> ConversationState:
        """Retrocede a la pregunta anterior"""
        current_question = state.get("current_question", 1)
        
        if current_question <= 1:
            state["agent_context"] = {
                "response": "No hay preguntas anteriores. ¿Quieres cancelar el formulario?",
                "current_node": "welcome"
            }
            state["next_action"] = "send_response"
            state["should_continue"] = False
            return state
        
        # Retroceder una pregunta
        state["current_question"] = current_question - 1
        
        # Obtener nodo anterior
        current_node_id = self._get_node_id_by_question(current_question - 1)
        current_node = self.nodes[current_node_id]
        response = self._format_node_response(current_node)
        
        state["agent_context"] = {
            "response": response,
            "current_node": current_node["node_id"],
            "question_number": current_question - 1
        }
        state["next_action"] = "send_response"
        state["should_continue"] = False
        
        return state

    async def _save_progress(self, state: ConversationState) -> ConversationState:
        """Guarda el progreso actual"""
        try:
            progress = {
                "wizard_session_id": state.get("wizard_session_id"),
                "current_question": state.get("current_question"),
                "wizard_responses": state.get("wizard_responses", {}),
                "wizard_state": state.get("wizard_state")
            }
            
            # TODO: Guardar en base de datos cuando esté disponible
            # await self._save_to_database(progress)
            
            state["agent_context"] = {
                "response": "Progreso guardado exitosamente. Puedes continuar más tarde.",
                "progress_saved": True
            }
            state["next_action"] = "send_response"
            state["should_continue"] = False
            
            return state
            
        except Exception as e:
            raise e
            logger.error(f"Error saving progress: {e}")
            return self._handle_wizard_error(state, "Error al guardar el progreso")

    async def _complete_wizard(self, state: ConversationState) -> ConversationState:
        """Completa el wizard y muestra resumen"""
        try:
            wizard_responses = state.get("wizard_responses", {})
            
            # Generar resumen usando IA
            summary = await self._generate_completion_summary(wizard_responses)
            
            state["wizard_state"] = "COMPLETED"
            state["agent_context"] = {
                "response": summary,
                "wizard_completed": True,
                "final_responses": wizard_responses
            }
            state["next_action"] = "send_response"
            state["should_continue"] = False
            
            return state
            
        except Exception as e:
            raise e
            logger.error(f"Error completing wizard: {e}")
            return self._handle_wizard_error(state, str(e))

    async def _generate_completion_summary(self, responses: Dict[str, Any]) -> str:
        """Genera un resumen de las respuestas usando IA"""
        try:
            responses_text = "\n".join([f"• {key}: {value}" for key, value in responses.items()])
            
            prompt = f"""
Genera un resumen amigable y profesional de las respuestas del formulario de postulación:

RESPUESTAS RECIBIDAS:
{responses_text}

INSTRUCCIONES:
1. Agradece por completar el formulario
2. Resume brevemente la información proporcionada
3. Menciona los próximos pasos (contacto del equipo, revisión, etc.)
4. Mantén un tono profesional pero amigable
5. Incluye información de contacto si es relevante

RESUMEN:
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres el asistente de Ithaka. Genera resúmenes profesionales y amigables."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise e
            logger.error(f"Error generating completion summary: {e}")
            return """
¡Gracias por completar el formulario de postulación de Ithaka!

Hemos recibido tu información y nuestro equipo la revisará. Te contactaremos pronto con los próximos pasos.

Si tienes alguna pregunta, no dudes en contactarnos.

¡Que tengas un excelente día!
"""

    def _format_node_response(self, node: Dict[str, Any]) -> str:
        """Formatea la respuesta del nodo para el usuario"""
        response = node["content"]
        
        if node["example"]:
            response += f"\n\n{node['example']}"
        
        if node["options"]:
            response += "\n\nOpciones disponibles:"
            for i, option in enumerate(node["options"], 1):
                response += f"\n{i}. {option['label']}"
        
        if node["node_type"] == "multiselect":
            response += "\n\n(Puedes seleccionar múltiples opciones separadas por comas)"
        
        response += "\n\nComandos disponibles: 'atras', 'guardar', 'cancelar'"
        
        return response

    def _get_node_id_by_question(self, question_number: int) -> str:
        """Obtiene el ID del nodo basado en el número de pregunta"""
        node_mapping = {
            1: "welcome",
            2: "full_name", 
            3: "email",
            4: "location",
            5: "support_needed",
            6: "completion"
        }
        return node_mapping.get(question_number, "welcome")

    def _handle_wizard_error(self, state: ConversationState, error_message: str) -> ConversationState:
        """Maneja errores del wizard"""
        logger.error(f"Wizard error: {error_message}")
        
        state["agent_context"] = {
            "response": f"Lo siento, tuve un problema técnico: {error_message}\n\n¿Quieres intentar de nuevo o cancelar el formulario?",
            "error": True
        }
        state["next_action"] = "send_response"
        state["should_continue"] = False
        
        return state

    async def _show_completion_summary(self, state: ConversationState) -> ConversationState:
        """Muestra el resumen de completación"""
        wizard_responses = state.get("wizard_responses", {})
        summary = await self._generate_completion_summary(wizard_responses)
        
        state["agent_context"] = {
            "response": summary,
            "wizard_completed": True
        }
        state["next_action"] = "send_response"
        state["should_continue"] = False
        
        return state


# Instancia global del agente
wizard_agent = WizardAgent()

# Función para usar en el grafo LangGraph
async def handle_wizard_flow(state: ConversationState) -> ConversationState:
    """Función wrapper para LangGraph"""
    return await wizard_agent.handle_wizard_flow(state)