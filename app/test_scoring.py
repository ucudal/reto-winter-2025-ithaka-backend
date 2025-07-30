import asyncio
import sys
import os

# Agregar el directorio raíz al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.scoring_service import procesar_postulaciones, procesar_postulacion_especifica
from app.services.score_engine import evaluar_postulacion

async def test_score_engine():
    """Prueba el motor de scoring con textos de ejemplo"""
    print("=== Prueba del Motor de Scoring ===")
    
    # Textos de prueba
    textos_prueba = [
        "Me apasiona la tecnología y quiero innovar en el campo de la inteligencia artificial. Planeo desarrollar soluciones creativas que transformen la manera en que las personas interactúan con la tecnología. Mi objetivo es crear aplicaciones que no solo sean funcionales, sino también intuitivas y revolucionarias.",
        
        "Quiero trabajar en el proyecto porque me interesa mucho.",
        
        "Mi compromiso con el aprendizaje es constante. Me esfuerzo por mejorar mis habilidades cada día y aspirar a alcanzar metas más altas. La dedicación y constancia son valores fundamentales en mi desarrollo profesional.",
        
        "",  # Texto vacío
    ]
    
    for i, texto in enumerate(textos_prueba, 1):
        print(f"\n--- Texto de prueba {i} ---")
        print(f"Texto: {texto[:100]}{'...' if len(texto) > 100 else ''}")
        
        scores = evaluar_postulacion(texto)
        print(f"Creatividad: {scores['creatividad']}")
        print(f"Claridad: {scores['claridad']}")
        print(f"Compromiso: {scores['compromiso']}")
        print(f"Score Total: {scores['score_total']}")

async def test_scoring_service():
    """Prueba el servicio de scoring con la base de datos"""
    print("\n=== Prueba del Servicio de Scoring ===")
    
    try:
        # Procesar todas las postulaciones
        await procesar_postulaciones()
        print("✅ Servicio de scoring funcionando correctamente")
        
    except Exception as e:
        print(f"❌ Error en el servicio de scoring: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Función principal para ejecutar todas las pruebas"""
    print("Iniciando pruebas del sistema de scoring...")
    
    # Prueba del motor de scoring
    await test_score_engine()
    
    # Prueba del servicio de scoring
    await test_scoring_service()
    
    print("\n=== Pruebas completadas ===")

if __name__ == "__main__":
    asyncio.run(main()) 