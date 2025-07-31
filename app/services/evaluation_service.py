import os
import json
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI
# Removed unused import
import logging

logger = logging.getLogger(__name__)


class EvaluationService:
    """Servicio para evaluar respuestas del wizard usando IA y rúbrica"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.rubrica = self._load_rubrica()
        self.max_iterations = self.rubrica.get(
            "configuracion", {}).get("max_iteraciones_mejora", 3)

    def _load_rubrica(self) -> Dict[str, Any]:
        """Carga la rúbrica desde el archivo JSON"""
        try:
            config_path = os.path.join(os.path.dirname(
                __file__), "..", "config", "rubrica.json")
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading rubrica: {e}")
            return {"criterios_evaluacion": {}, "configuracion": {}}

    async def evaluate_response(
        self,
        question_number: int,
        user_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evalúa una respuesta del usuario según la rúbrica"""

        question_key = f"pregunta_{question_number}"

        # Si no hay criterios específicos, solo validar longitud mínima
        if question_key not in self.rubrica["criterios_evaluacion"]:
            return {
                "is_acceptable": len(user_response.strip()) >= 10,
                "feedback": None,
                "suggestions": [],
                "score": 1.0 if len(user_response.strip()) >= 10 else 0.5
            }

        question_config = self.rubrica["criterios_evaluacion"][question_key]

        # Para preguntas informativas, solo verificar coherencia básica
        if question_config.get("tipo") == "informativa":
            return await self._evaluate_informative_question(question_config, user_response)

        # Para preguntas evaluativas, usar IA para evaluación profunda
        if question_config.get("tipo") == "evaluativa":
            return await self._evaluate_with_ai(question_config, user_response, context)

        # Para preguntas opcionales, aceptar cualquier respuesta
        return {
            "is_acceptable": True,
            "feedback": "Gracias por la información adicional.",
            "suggestions": [],
            "score": 1.0
        }

    async def _evaluate_informative_question(
        self,
        config: Dict[str, Any],
        response: str
    ) -> Dict[str, Any]:
        """Evalúa preguntas informativas básicas"""

        response_clean = response.strip()
        min_length = self.rubrica.get("configuracion", {}).get(
            "longitud_minima_evaluativas", 10)

        is_acceptable = len(response_clean) >= min_length and response_clean.lower(
        ) not in ["no sé", "no se", ""]

        return {
            "is_acceptable": is_acceptable,
            "feedback": None if is_acceptable else "Por favor, proporciona más detalles en tu respuesta.",
            "suggestions": [] if is_acceptable else ["Sé más específico en tu respuesta", "Proporciona más contexto"],
            "score": 1.0 if is_acceptable else 0.6
        }

    async def _evaluate_with_ai(
        self,
        config: Dict[str, Any],
        response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evalúa respuestas complejas usando IA"""

        try:
            # Construir prompt de evaluación
            evaluation_prompt = self._build_evaluation_prompt(
                config, response, context)

            response_ai = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un evaluador experto en emprendimiento que analiza respuestas según criterios específicos. Responde en JSON válido."
                    },
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )

            # Parsear respuesta JSON
            evaluation_result = json.loads(
                response_ai.choices[0].message.content)

            return {
                "is_acceptable": evaluation_result.get("is_acceptable", False),
                "feedback": evaluation_result.get("feedback"),
                "suggestions": evaluation_result.get("suggestions", []),
                "score": evaluation_result.get("score", 0.5),
                "strengths": evaluation_result.get("strengths", []),
                "areas_for_improvement": evaluation_result.get("areas_for_improvement", [])
            }

        except Exception as e:
            logger.error(f"Error in AI evaluation: {e}")
            # Fallback a evaluación básica
            return {
                "is_acceptable": len(response.strip()) >= 20,
                "feedback": "No pudimos evaluar tu respuesta completamente. ¿Podrías proporcionar más detalles?",
                "suggestions": ["Sé más específico", "Proporciona ejemplos concretos"],
                "score": 0.7
            }

    def _build_evaluation_prompt(
        self,
        config: Dict[str, Any],
        response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Construye el prompt para la evaluación de IA"""

        prompt = f"""
Evalúa la siguiente respuesta para la pregunta: "{config['titulo']}"

CRITERIOS DE EVALUACIÓN:
{chr(10).join(f"- {criterio}" for criterio in config['criterios'])}

PROMPT DE EVALUACIÓN ESPECÍFICO:
{config['prompt_evaluacion']}

RESPUESTA A EVALUAR:
"{response}"

{"CONTEXTO ADICIONAL:" + json.dumps(context, indent=2, ensure_ascii=False) if context else ""}

Responde ÚNICAMENTE en JSON con esta estructura:
{{
    "is_acceptable": boolean,
    "score": float (0.0 a 1.0),
    "feedback": "string con retroalimentación específica",
    "suggestions": ["lista", "de", "sugerencias", "concretas"],
    "strengths": ["fortalezas", "identificadas"],
    "areas_for_improvement": ["áreas", "de", "mejora"]
}}
"""
        return prompt

    async def generate_improvement_suggestions(
        self,
        question_number: int,
        current_response: str,
        evaluation_result: Dict[str, Any]
    ) -> str:
        """Genera sugerencias específicas para mejorar una respuesta"""

        try:
            question_key = f"pregunta_{question_number}"
            config = self.rubrica["criterios_evaluacion"].get(question_key, {})

            prompt = f"""
Como mentor de emprendimiento, ayuda a mejorar esta respuesta:

PREGUNTA: {config.get('titulo', 'Pregunta')}
RESPUESTA ACTUAL: "{current_response}"

EVALUACIÓN PREVIA:
- Score: {evaluation_result.get('score', 0)}
- Feedback: {evaluation_result.get('feedback', '')}
- Áreas de mejora: {evaluation_result.get('areas_for_improvement', [])}

Proporciona 2-3 sugerencias concretas y específicas para mejorar la respuesta. Sé constructivo y orientado a la acción.
"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un mentor empático y constructivo que ayuda a emprendedores a mejorar sus postulaciones."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating improvement suggestions: {e}")
            return "Te sugiero ser más específico y proporcionar ejemplos concretos en tu respuesta."


# Instancia global del servicio
evaluation_service = EvaluationService()
