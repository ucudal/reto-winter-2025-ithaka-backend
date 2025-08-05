#!/usr/bin/env python3
"""
Script para probar el problema de timeout específico
"""

import asyncio

import aiohttp


async def test_faq_timeout_issue():
    """Prueba específicamente el problema de timeout con FAQs"""

    url = "http://localhost:8000/api/v1/copilotkit"

    # Casos de prueba que deberían activar el agente FAQ
    faq_test_cases = [
        {
            "message": "¿Qué es el programa Fellows?",
            "description": "Pregunta directa sobre Fellows"
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
            "message": "costo precio gratis",
            "description": "Palabras clave costos"
        },
        {
            "message": "¿Qué cursos electivos hay?",
            "description": "Pregunta sobre cursos"
        },
        {
            "message": "curso electivo minor",
            "description": "Palabras clave cursos"
        }
    ]

    # Casos de prueba que NO deberían activar FAQ
    non_faq_test_cases = [
        {
            "message": "Hola, ¿cómo estás?",
            "description": "Saludo general"
        },
        {
            "message": "¿Qué tiempo hace hoy?",
            "description": "Pregunta no relacionada"
        },
        {
            "message": "Cuéntame un chiste",
            "description": "Pregunta casual"
        }
    ]

    print("🧪 Probando problema de timeout con FAQs")
    print("=" * 60)

    async with aiohttp.ClientSession() as session:
        # Probar casos FAQ
        print("\n📚 Probando casos que deberían activar FAQ:")
        for i, test_case in enumerate(faq_test_cases, 1):
            print(f"\n📝 Test FAQ {i}: {test_case['description']}")
            print(f"Pregunta: {test_case['message']}")

            try:
                payload = {
                    "message": test_case["message"],
                    "conversation_id": None,
                    "user_email": None,
                    "properties": {}
                }

                # Configurar timeout más corto para detectar el problema
                timeout = aiohttp.ClientTimeout(total=30)

                async with session.post(url, json=payload, timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Respuesta exitosa en {response.headers.get('x-response-time', 'N/A')}ms:")
                        print(f"   Agente usado: {data.get('agent_used', 'N/A')}")
                        print(f"   Respuesta: {data.get('response', '')[:100]}...")
                        if data.get('metadata', {}).get('faq_results'):
                            print(f"   FAQs encontradas: {len(data.get('metadata', {}).get('faq_results', []))}")
                        else:
                            print(f"   FAQs encontradas: 0 (usando respuesta mock)")
                    else:
                        error_text = await response.text()
                        print(f"❌ Error {response.status}: {error_text}")

            except asyncio.TimeoutError:
                print(f"⏰ TIMEOUT: La petición tardó más de 30 segundos")
            except Exception as e:
                print(f"❌ Error de conexión: {e}")

        # Probar casos NO FAQ
        print("\n🔍 Probando casos que NO deberían activar FAQ:")
        for i, test_case in enumerate(non_faq_test_cases, 1):
            print(f"\n📝 Test NO-FAQ {i}: {test_case['description']}")
            print(f"Pregunta: {test_case['message']}")

            try:
                payload = {
                    "message": test_case["message"],
                    "conversation_id": None,
                    "user_email": None,
                    "properties": {}
                }

                timeout = aiohttp.ClientTimeout(total=30)

                async with session.post(url, json=payload, timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Respuesta exitosa en {response.headers.get('x-response-time', 'N/A')}ms:")
                        print(f"   Agente usado: {data.get('agent_used', 'N/A')}")
                        print(f"   Respuesta: {data.get('response', '')[:100]}...")
                    else:
                        error_text = await response.text()
                        print(f"❌ Error {response.status}: {error_text}")

            except asyncio.TimeoutError:
                print(f"⏰ TIMEOUT: La petición tardó más de 30 segundos")
            except Exception as e:
                print(f"❌ Error de conexión: {e}")


async def test_workflow_directly():
    """Prueba el workflow directamente para identificar el problema"""

    print("\n🔧 Probando workflow directamente...")

    try:
        from app.graph.workflow import process_user_message

        # Test con pregunta FAQ
        print("\n📝 Probando workflow con pregunta FAQ:")
        result = await process_user_message(
            user_message="¿Qué es el programa Fellows?",
            conversation_id=None,
            chat_history=[],
            user_email=None
        )

        print(f"✅ Workflow completado:")
        print(f"   Agente usado: {result.get('agent_used')}")
        print(f"   Respuesta: {result.get('response', '')[:100]}...")
        print(f"   Tiempo de procesamiento: {result.get('processing_time', 'N/A')}")

    except Exception as e:
        print(f"❌ Error en workflow: {e}")


async def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de timeout específicas")

    # Probar el problema de timeout
    await test_faq_timeout_issue()

    # Probar workflow directamente
    await test_workflow_directly()

    print("\n🎉 Pruebas completadas")


if __name__ == "__main__":
    asyncio.run(main())
