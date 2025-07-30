import os
import json
from typing import Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class AIScoreEngine:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def evaluar_postulacion(self, texto: str) -> Dict[str, Any]:
        """
        Evalúa una postulación usando IA para análisis sofisticado.
        """
        if not texto or not texto.strip():
            return {
                "creatividad": 0,
                "claridad": 0,
                "compromiso": 0,
                "score_total": 0,
                "analisis": "Texto vacío"
            }
        
        try:
            # Prompt para la IA
            prompt = f"""
            Analiza el siguiente texto de una postulación y evalúa al candidato en tres dimensiones:

            TEXTO: "{texto}"

            Por favor evalúa en una escala de 0-100:

            1. CREATIVIDAD (0-100): Capacidad de generar ideas originales, pensamiento innovador, vocabulario variado, desarrollo de conceptos únicos.

            2. CLARIDAD (0-100): Comunicación efectiva, estructura del texto, uso de conectores, coherencia lógica, facilidad de comprensión.

            3. COMPROMISO (0-100): Motivación demostrada, dedicación, planificación futura, expresiones de interés genuino, metas claras.

            Responde SOLO con un JSON válido en este formato exacto:
            {{
                "creatividad": [número 0-100],
                "claridad": [número 0-100],
                "compromiso": [número 0-100],
                "score_total": [promedio ponderado: creatividad*0.4 + claridad*0.3 + compromiso*0.3],
                "analisis": "Breve análisis de 2-3 oraciones explicando la evaluación"
            }}
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un evaluador experto de postulaciones. Analiza textos de manera objetiva y justa."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3, 
                max_tokens=300
            )
            
            # Extraer y parsear la respuesta JSON
            content = response.choices[0].message.content.strip()
            
            # Intentar extraer JSON del texto
            try:
                # Buscar JSON en la respuesta
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = content[start:end]
                    scores = json.loads(json_str)
                    
                    # Validar que los scores estén en el rango correcto
                    for key in ['creatividad', 'claridad', 'compromiso']:
                        if key in scores:
                            scores[key] = max(0, min(100, int(scores[key])))
                    
                    # Calcular score total si no está presente
                    if 'score_total' not in scores:
                        scores['score_total'] = round(
                            scores['creatividad'] * 0.4 + 
                            scores['claridad'] * 0.3 + 
                            scores['compromiso'] * 0.3, 2
                        )
                    
                    return scores
                else:
                    raise ValueError("No se encontró JSON válido en la respuesta")
                    
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error parseando respuesta de IA: {e}")
                print(f"Respuesta recibida: {content}")
                # Fallback a evaluación básica
                return self._evaluacion_fallback(texto)
                
        except Exception as e:
            print(f"Error en evaluación con IA: {e}")
            # Fallback a evaluación básica
            return self._evaluacion_fallback(texto)
    
    def _evaluacion_fallback(self, texto: str) -> Dict[str, Any]:
        """
        Evaluación básica de fallback cuando la IA no está disponible.
        """
        # Análisis básico basado en longitud y palabras clave
        score_base = min(100, len(texto) // 2)
        
        return {
            "creatividad": score_base,
            "claridad": score_base,
            "compromiso": score_base,
            "score_total": round(score_base, 2),
            "analisis": "Evaluación básica (IA no disponible)"
        }

# Instancia global
ai_engine = AIScoreEngine()

async def evaluar_postulacion_ai(texto: str) -> Dict[str, Any]:
    """
    Función wrapper para evaluar postulaciones con IA.
    """
    return await ai_engine.evaluar_postulacion(texto) 