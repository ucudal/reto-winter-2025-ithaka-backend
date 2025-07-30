#!/usr/bin/env python3
"""
Script de prueba para el sistema de scoring de postulaciones.
Este script prueba tanto el motor de scoring como los endpoints de la API.
"""

import asyncio
import sys
import os
import requests
import json

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.score_engine import evaluar_postulacion

def test_score_engine():
    """Prueba el motor de scoring con textos de ejemplo"""
    print("=== Prueba del Motor de Scoring ===")
    
    textos_prueba = [
        {
            "texto": "Me apasiona la tecnología y quiero innovar en el campo de la inteligencia artificial. Planeo desarrollar soluciones creativas que transformen la manera en que las personas interactúan con la tecnología. Mi objetivo es crear aplicaciones que no solo sean funcionales, sino también intuitivas y revolucionarias.",
            "descripcion": "Texto con alta creatividad y compromiso"
        },
        {
            "texto": "Quiero trabajar en el proyecto porque me interesa mucho.",
            "descripcion": "Texto corto y simple"
        },
        {
            "texto": "Mi compromiso con el aprendizaje es constante. Me esfuerzo por mejorar mis habilidades cada día y aspirar a alcanzar metas más altas. La dedicación y constancia son valores fundamentales en mi desarrollo profesional.",
            "descripcion": "Texto enfocado en compromiso"
        },
        {
            "texto": "",
            "descripcion": "Texto vacío"
        }
    ]
    
    for i, test_case in enumerate(textos_prueba, 1):
        print(f"\n--- {test_case['descripcion']} ---")
        print(f"Texto: {test_case['texto'][:100]}{'...' if len(test_case['texto']) > 100 else ''}")
        
        scores = evaluar_postulacion(test_case['texto'])
        print(f"Creatividad: {scores['creatividad']}")
        print(f"Claridad: {scores['claridad']}")
        print(f"Compromiso: {scores['compromiso']}")
        print(f"Score Total: {scores['score_total']}")

def test_api_endpoints():
    """Prueba los endpoints de la API"""
    print("\n=== Prueba de Endpoints de la API ===")
    
    base_url = "http://localhost:8000/api/v1"
    
    # Prueba del endpoint de evaluación de texto
    print("\n--- Probando endpoint /scoring/evaluate ---")
    try:
        response = requests.post(
            f"{base_url}/scoring/evaluate",
            json={
                "texto": "Me apasiona la tecnología y quiero innovar en el campo de la inteligencia artificial."
            }
        )
        
        if response.status_code == 200:
            scores = response.json()
            print("✅ Endpoint funcionando correctamente")
            print(f"Creatividad: {scores['creatividad']}")
            print(f"Claridad: {scores['claridad']}")
            print(f"Compromiso: {scores['compromiso']}")
            print(f"Score Total: {scores['score_total']}")
        else:
            print(f"❌ Error en el endpoint: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. Asegúrate de que la API esté corriendo.")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_database_operations():
    """Prueba las operaciones de base de datos"""
    print("\n=== Prueba de Operaciones de Base de Datos ===")
    
    try:
        # Importar aquí para evitar errores si la base de datos no está configurada
        from app.services.scoring_service import procesar_postulaciones
        
        print("✅ Módulo de scoring service importado correctamente")
        
        # Nota: Para probar las operaciones de base de datos, necesitas tener la base de datos configurada
        print("ℹ️  Para probar las operaciones de base de datos, ejecuta el script de prueba completo:")
        print("   python app/test_scoring.py")
        
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas del sistema de scoring...")
    
    # Prueba del motor de scoring
    test_score_engine()
    
    # Prueba de endpoints de la API
    test_api_endpoints()
    
    # Prueba de operaciones de base de datos
    test_database_operations()
    
    print("\n=== Resumen de Pruebas ===")
    print("✅ Motor de scoring: Funcionando")
    print("ℹ️  Endpoints de API: Requieren servidor corriendo")
    print("ℹ️  Base de datos: Requiere configuración de BD")
    
    print("\n📋 Para ejecutar todas las pruebas completas:")
    print("1. Asegúrate de que la base de datos esté configurada")
    print("2. Ejecuta el servidor: uvicorn app.main:app --reload")
    print("3. Ejecuta las pruebas completas: python app/test_scoring.py")

if __name__ == "__main__":
    main() 