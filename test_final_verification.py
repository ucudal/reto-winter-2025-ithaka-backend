#!/usr/bin/env python3
"""
Script final para verificar que todo esté funcionando correctamente
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

async def test_final_verification():
    """Verificación final del sistema"""
    
    url = "http://localhost:8000/api/v1/copilotkit"
    
    # Casos de prueba que deberían funcionar correctamente
    test_cases = [
        {
            "message": "¿Qué es el programa Fellows?",
            "description": "Pregunta FAQ directa",
            "expected_agent": "faq"
        },
        {
            "message": "fellows programa beca",
            "description": "Palabras clave Fellows",
            "expected_agent": "faq"
        },
        {
            "message": "¿Cuánto cuestan los cursos?",
            "description": "Pregunta sobre costos",
            "expected_agent": "faq"
        },
        {
            "message": "Hola, ¿cómo estás?",
            "description": "Saludo general",
            "expected_agent": "faq"
        }
    ]
    
    print("🎯 VERIFICACIÓN FINAL DEL SISTEMA")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test {i}: {test_case['description']}")
            print(f"Pregunta: {test_case['message']}")
            
            try:
                payload = {
                    "message": test_case["message"],
                    "conversation_id": None,
                    "user_email": None,
                    "properties": {}
                }
                
                # Configurar timeout de 30 segundos
                timeout = aiohttp.ClientTimeout(total=30)
                
                start_time = time.time()
                async with session.post(url, json=payload, timeout=timeout) as response:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        agent_used = data.get('agent_used', 'N/A')
                        expected_agent = test_case['expected_agent']
                        
                        print(f"✅ Respuesta exitosa en {response_time:.2f}ms:")
                        print(f"   Agente usado: {agent_used} (esperado: {expected_agent})")
                        print(f"   Respuesta: {data.get('response', '')[:100]}...")
                        
                        if agent_used == expected_agent:
                            print(f"   ✅ Agente correcto")
                        else:
                            print(f"   ⚠️  Agente diferente al esperado")
                            
                    else:
                        error_text = await response.text()
                        print(f"❌ Error {response.status}: {error_text}")
                        
            except asyncio.TimeoutError:
                print(f"⏰ TIMEOUT: La petición tardó más de 30 segundos")
            except Exception as e:
                print(f"❌ Error de conexión: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Verificación completada")
    print("\n📋 RESUMEN DE CAMBIOS IMPLEMENTADOS:")
    print("1. ✅ Corregida variable de entorno LANGGRAPH_DEPLOYMENT_URL")
    print("2. ✅ Mejorado logging en endpoint CopilotKit")
    print("3. ✅ Expandida configuración de CORS")
    print("4. ✅ Creados componentes de test para debugging")
    print("\n🔧 PRÓXIMOS PASOS:")
    print("1. Verificar que el frontend esté corriendo en http://localhost:3000")
    print("2. Probar el chat desde el frontend")
    print("3. Si persiste el problema, revisar logs del frontend y backend")

async def main():
    """Función principal"""
    await test_final_verification()

if __name__ == "__main__":
    asyncio.run(main()) 