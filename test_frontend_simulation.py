#!/usr/bin/env python3
"""
Script para simular las peticiones del frontend y identificar el problema de timeout
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

async def simulate_frontend_request():
    """Simula exactamente las peticiones que hace el frontend"""
    
    url = "http://localhost:8000/api/v1/copilotkit"
    
    # Headers que usa CopilotKit
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Casos de prueba que deberían causar el problema
    test_cases = [
        {
            "message": "¿Qué es el programa Fellows?",
            "description": "Pregunta FAQ directa"
        },
        {
            "message": "fellows programa beca",
            "description": "Palabras clave Fellows"
        },
        {
            "message": "¿Cuánto cuestan los cursos?",
            "description": "Pregunta sobre costos"
        },
        {
            "message": "Hola, ¿cómo estás?",
            "description": "Saludo general (no FAQ)"
        }
    ]
    
    print("🧪 Simulando peticiones del frontend")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test {i}: {test_case['description']}")
            print(f"Pregunta: {test_case['message']}")
            
            # Payload exacto que envía CopilotKit
            payload = {
                "message": test_case["message"],
                "conversation_id": None,
                "user_email": None,
                "properties": {}
            }
            
            start_time = time.time()
            
            try:
                # Configurar timeout similar al del frontend
                timeout = aiohttp.ClientTimeout(total=60)
                
                async with session.post(url, json=payload, headers=headers, timeout=timeout) as response:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Respuesta exitosa en {response_time:.2f}ms:")
                        print(f"   Agente usado: {data.get('agent_used', 'N/A')}")
                        print(f"   Respuesta: {data.get('response', '')[:150]}...")
                        
                        # Verificar si hay FAQs encontradas
                        metadata = data.get('metadata', {})
                        faq_results = metadata.get('faq_results', [])
                        if faq_results:
                            print(f"   FAQs encontradas: {len(faq_results)}")
                        else:
                            print(f"   FAQs encontradas: 0 (usando respuesta mock)")
                            
                    else:
                        error_text = await response.text()
                        print(f"❌ Error {response.status}: {error_text}")
                        
            except asyncio.TimeoutError:
                print(f"⏰ TIMEOUT: La petición tardó más de 60 segundos")
                print(f"   Tiempo transcurrido: {time.time() - start_time:.2f}s")
            except Exception as e:
                print(f"❌ Error de conexión: {e}")

async def test_concurrent_requests():
    """Prueba múltiples peticiones concurrentes para simular uso real"""
    
    url = "http://localhost:8000/api/v1/copilotkit"
    
    # Preguntas que deberían activar FAQ
    faq_questions = [
        "¿Qué es el programa Fellows?",
        "¿Cuánto cuestan los cursos?",
        "fellows programa beca",
        "costo precio gratis",
        "¿Qué cursos electivos hay?"
    ]
    
    print("\n🔄 Probando peticiones concurrentes")
    print("=" * 40)
    
    async def make_request(question: str, request_id: int):
        """Hace una petición individual"""
        payload = {
            "message": question,
            "conversation_id": None,
            "user_email": None,
            "properties": {}
        }
        
        headers = {"Content-Type": "application/json"}
        timeout = aiohttp.ClientTimeout(total=30)
        
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.post(url, json=payload, headers=headers, timeout=timeout) as response:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Request {request_id}: {response_time:.2f}ms - {data.get('agent_used', 'N/A')}")
                    else:
                        print(f"❌ Request {request_id}: Error {response.status}")
                        
        except asyncio.TimeoutError:
            print(f"⏰ Request {request_id}: TIMEOUT")
        except Exception as e:
            print(f"❌ Request {request_id}: Error - {e}")
    
    # Ejecutar peticiones concurrentes
    tasks = [make_request(q, i+1) for i, q in enumerate(faq_questions)]
    await asyncio.gather(*tasks, return_exceptions=True)

async def main():
    """Función principal"""
    print("🚀 Iniciando simulación del frontend")
    
    # Simular peticiones individuales
    await simulate_frontend_request()
    
    # Simular peticiones concurrentes
    await test_concurrent_requests()
    
    print("\n🎉 Simulación completada")

if __name__ == "__main__":
    asyncio.run(main()) 