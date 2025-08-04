#!/usr/bin/env python3
"""
Script para probar la integración del backend con CopilotKit
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

async def test_copilotkit_endpoint():
    """Prueba el endpoint de CopilotKit"""
    
    url = "http://localhost:8000/api/v1/copilotkit"
    
    # Casos de prueba
    test_cases = [
        {
            "message": "¿Qué es el programa Fellows?",
            "description": "Pregunta sobre programa Fellows"
        },
        {
            "message": "¿Cuánto cuestan los cursos de Ithaka?",
            "description": "Pregunta sobre costos"
        },
        {
            "message": "¿Qué cursos electivos puedo hacer?",
            "description": "Pregunta sobre cursos electivos"
        },
        {
            "message": "¿Cómo me entero de las convocatorias?",
            "description": "Pregunta sobre convocatorias"
        }
    ]
    
    print("🧪 Probando integración CopilotKit - Backend Ithaka")
    print("=" * 60)
    
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
                
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Respuesta exitosa:")
                        print(f"   Agente usado: {data.get('agent_used', 'N/A')}")
                        print(f"   Respuesta: {data.get('response', '')[:200]}...")
                        if data.get('metadata'):
                            print(f"   Metadata: {data.get('metadata')}")
                    else:
                        error_text = await response.text()
                        print(f"❌ Error {response.status}: {error_text}")
                        
            except Exception as e:
                print(f"❌ Error de conexión: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")

async def test_health_endpoints():
    """Prueba los endpoints de health check"""
    
    endpoints = [
        "http://localhost:8000/",
        "http://localhost:8000/health",
        "http://localhost:8000/api/v1/copilotkit/health"
    ]
    
    print("\n🏥 Probando endpoints de health check")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            try:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ {endpoint}: {data}")
                    else:
                        print(f"❌ {endpoint}: Status {response.status}")
            except Exception as e:
                print(f"❌ {endpoint}: Error - {e}")

async def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de integración Ithaka Backend")
    
    # Probar health endpoints
    await test_health_endpoints()
    
    # Probar endpoint de CopilotKit
    await test_copilotkit_endpoint()
    
    print("\n🎉 Todas las pruebas completadas")

if __name__ == "__main__":
    asyncio.run(main()) 