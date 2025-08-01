"""
Agente de Validación - Valida y formatea respuestas del usuario
"""

import os
from typing import Optional
from openai import AsyncOpenAI
from copilotkit import CopilotKitState
from copilotkit.langgraph import interrupt
import logging

logger = logging.getLogger(__name__)

class ValidationAgent:
    """Agente para validar y formatear respuestas del usuario"""
    
    def __init__(self, copilot_state: CopilotKitState = None):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.copilot_state = copilot_state or CopilotKitState()
    
    async def validate_question(self, user_input: str, validation_prompt: str) -> Optional[str]:
        """Valida una pregunta abierta con IA"""
        try:
            prompt = f"""
Eres un asistente que ayuda a formatear información.

INSTRUCCIÓN DE VALIDACIÓN:
{validation_prompt}

ENTRADA DEL USUARIO:
{user_input}

INSTRUCCIONES:
1. Analiza la entrada del usuario
2. Aplica la validación especificada
3. Devuelve SOLO el dato formateado correctamente
4. Si no es válido o no se puede extraer, devuelve "None"

RESPUESTA FORMATEADA:
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un validador experto que formatea información de manera precisa."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            result = response.choices[0].message.content.strip()
            
            # Validación humana si es necesaria
            if await self._needs_human_validation(user_input, result):
                result = await self._get_human_validation(
                    f"Validar respuesta:\nUsuario: {user_input}\nIA: {result}"
                )
            
            # Verificar si la respuesta es válida
            if result.lower() == "none" or not result:
                return None
            
            return result
            
        except Exception as e:
            raise e
            logger.error(f"Error validating question: {e}")
            return None
    
    async def _needs_human_validation(self, user_input: str, ai_response: str) -> bool:
        """Determina si se necesita validación humana"""
        if ai_response == "None":
            return True
        if len(ai_response.split()) < len(user_input.split()) / 2:
            return True
        return False
    
    async def _get_human_validation(self, prompt: str) -> str:
        """Obtiene validación humana a través de CopilotKit"""
        return await interrupt(prompt)
    
    async def validate_email(self, email: str) -> Optional[str]:
        """Valida formato de email"""
        try:
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(pattern, email):
                return email.lower().strip()
            return None
        except Exception as e:
            raise e
            logger.error(f"Error validating email: {e}")
            return None
    
    async def validate_name(self, name: str) -> Optional[str]:
        """Valida y formatea nombre completo"""
        try:
            # Limpiar y formatear nombre
            cleaned_name = name.strip()
            if len(cleaned_name.split()) < 2:
                return None
            
            # Intentar formatear como "Apellido, Nombre"
            parts = cleaned_name.split()
            if len(parts) >= 2:
                # Si ya tiene coma, mantener formato
                if "," in cleaned_name:
                    return cleaned_name
                # Si no, formatear como "Apellido, Nombre"
                else:
                    return f"{parts[-1]}, {' '.join(parts[:-1])}"
            
            return None
            
        except Exception as e:
            raise e
            logger.error(f"Error validating name: {e}")
            return None