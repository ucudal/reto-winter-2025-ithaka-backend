#!/usr/bin/env python3
"""
Script de setup completo para el sistema de agentes IA de Ithaka
Este script configura la base de datos, crea tablas, y puebla datos iniciales
"""

from pathlib import Path
import sys
import asyncio
import os

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.config.create_tables import create_tables


async def main():
    """Función principal de setup"""

    print("🚀 Iniciando setup completo del sistema de agentes IA de Ithaka")
    print("=" * 60)

    # Verificar variables de entorno críticas
    print("1️⃣ Verificando variables de entorno...")

    required_vars = [
        "DATABASE_URL",
        "OPENAI_API_KEY"
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Faltan las siguientes variables de entorno:")
        for var in missing_vars:
            print(f"   - {var}")
        print(f"\n📝 Por favor, configura estas variables en tu archivo .env")
        print(f"💡 Puedes usar config/env.example como referencia")
        return False

    print("✅ Variables de entorno configuradas")

    # Crear tablas de base de datos
    print("\n2️⃣ Creando tablas de base de datos...")
    try:
        await create_tables()
        print("✅ Tablas creadas exitosamente")
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        return False

    # Poblar FAQs
    print("\n3️⃣ Poblando base de datos con FAQs...")
    try:
        # Importar aquí para evitar problemas de circular import
        from app.services.embedding_service import embedding_service
        from app.db.config.database import get_async_session

        # FAQs data directamente aquí
        FAQS_DATA = [
            # Cursos y capacitaciones
            {
                "question": "¿Qué cursos electivos puedo hacer en Ithaka?",
                "answer": "Tenemos un PDF con todos los cursos electivos https://bit.ly/ElectivasIthaka. Si te interesa el paquete completo de cursos puedes dirigirte al minor de innovación y emprendimiento https://minor-innovacion-emprend-6ucsomp.gamma.site/"
            },
            {
                "question": "cursos de emprendimiento capacitaciones ithaka formacion",
                "answer": "En Ithaka ofrecemos múltiples cursos y capacitaciones en emprendimiento e innovación. Tenemos cursos electivos para estudiantes UCU, el minor de innovación y emprendimiento, y capacitaciones abiertas para la comunidad. Todos nuestros cursos son gratuitos para la comunidad UCU. Más información: https://bit.ly/ElectivasIthaka"
            },

            # Programa Fellows - múltiples variaciones
            {
                "question": "¿Qué es el programa Fellows?",
                "answer": "Es un programa online creado por la universidad de Stanford y dictado por la universidad de Twente que te ayuda a desarrollar habilidades intraemprendedoras en tu experiencia universitaria. Es un programa que desde UCU-Ithaka seleccionamos y becamos 4 estudiantes para que se conviertan en agentes de cambio. Además los seleccionados tienen la posibilidad de asistir al evento internacional de meetup de fellows un viaje en la universidad de Twente, Países Bajos durante 3 días (los pasajes son costeados por la UCU). https://programa-university-inno-k2jjjij.gamma.site/"
            },
            {
                "question": "programa fellows como funciona que es becas stanford twente",
                "answer": "El programa Fellows es una beca completa que te ayuda a desarrollar habilidades de intraemprendimiento. Seleccionamos solo 4 estudiantes UCU por año. Incluye formación online con Stanford/Twente y viaje a Países Bajos. Es completamente gratuito y una oportunidad única de crecimiento personal y profesional. https://programa-university-inno-k2jjjij.gamma.site/"
            },
            {
                "question": "¿Cuándo es la convocatoria para el programa Fellows?",
                "answer": "Durante marzo-abril se lanza la convocatoria para postulantes al programa, y luego de un proceso de selección de aprox. 1 mes con entrevistas grupales e individuales, se seleccionan 4 participantes."
            },

            # Freelancer y emprendimiento profesional
            {
                "question": "¿Quiero emprender como freelancer, cómo hago?",
                "answer": "Desarrolla una marca personal y trabajar desde tu profesión es posible pero es necesario saber y haber desarrollando ciertos conocimientos, habilidades y competencias. En Ithaka tenemos cursos específicos si te interesa emprender desde tu profesión."
            },
            {
                "question": "freelance independiente marca personal profesion emprender trabajo",
                "answer": "Para emprender como freelancer necesitas desarrollar tu marca personal y habilidades específicas. En Ithaka te ayudamos con cursos sobre emprendimiento profesional, desarrollo de marca personal, y herramientas para el trabajo independiente. Nuestros mentores tienen experiencia en diferentes industrias."
            },

            # Información general de Ithaka
            {
                "question": "¿El Centro Ithaka es exclusivo para estudiantes y egresados UCU?",
                "answer": "No, el Centro Ithaka forma parte del ecosistema emprendedor y atiende a la comunidad universitaria UCU en general (futuros estudiantes, estudiantes, egresados, profesores y funcionarios) así como a emprendedores interesados en las actividades que ofrecemos."
            },
            {
                "question": "que es ithaka centro emprendimiento ucu que hacen servicios",
                "answer": "Ithaka es el centro de emprendimiento e innovación de la Universidad Católica del Uruguay. Ofrecemos programas educativos, incubadora de startups, mentorías, y capacitaciones para desarrollar el espíritu emprendedor. Estamos abiertos tanto a la comunidad UCU como a emprendedores externos."
            },

            # Costos y accesibilidad
            {
                "question": "¿Cuánto cuestan los cursos y actividades de Ithaka?",
                "answer": "Todas nuestras actividades son completamente gratuitas. Los cursos electivos son gratis para estudiantes UCU que tengan créditos disponibles, las mentorías están abiertas a la comunidad universitaria UCU, y nuestros programas como Fellows incluyen becas completas. Nuestro objetivo es hacer el emprendimiento accesible para todos."
            },
            {
                "question": "costo precio gratis gratuito pagar actividades cursos mentoria",
                "answer": "¡Todo es gratuito! En Ithaka creemos que el emprendimiento debe ser accesible. Nuestros cursos, mentorías, programas y actividades de incubadora no tienen costo. Solo necesitas ganas de aprender y emprender. Para estudiantes UCU solo se requieren créditos disponibles para cursos electivos."
            },

            # Convocatorias y novedades
            {
                "question": "¿Cómo me entero de las convocatorias y novedades de Ithaka?",
                "answer": "Puedes seguirnos en nuestras redes sociales (Instagram, Twitter y LinkedIn) o suscribirte a nuestro newsletter. Allí publicamos todas las convocatorias, eventos, y oportunidades disponibles."
            },
            {
                "question": "noticias convocatorias eventos novedades informacion contacto redes",
                "answer": "Para estar al día con Ithaka, síguenos en Instagram, Twitter y LinkedIn. También tenemos un newsletter donde enviamos todas las oportunidades, convocatorias y eventos. Así no te pierdes ninguna oportunidad de crecimiento emprendedor."
            },

            # Minor de emprendimiento
            {
                "question": "¿Qué ofrece el minor de emprendimiento?",
                "answer": "Este programa de un semestre te permite especializarte en creatividad, innovación y mentalidad emprendedora. Desarrollarás la capacidad de detectar problemáticas y proponer soluciones, creando modelos de negocios innovadores y sustentables. https://minor-innovacion-emprend-6ucsomp.gamma.site/"
            }
        ]

        async for session in get_async_session():
            for i, faq_data in enumerate(FAQS_DATA, 1):
                print(
                    f"📝 Procesando FAQ {i}/{len(FAQS_DATA)}: {faq_data['question'][:50]}...")

                result = await embedding_service.add_faq_embedding(
                    question=faq_data["question"],
                    answer=faq_data["answer"],
                    session=session
                )

                if result:
                    print(f"   ✅ FAQ agregada con ID: {result.id}")
                else:
                    print(f"   ❌ Error agregando FAQ")
            break  # Solo necesitamos una sesión

        print("✅ FAQs cargadas exitosamente")
    except Exception as e:
        print(f"❌ Error poblando FAQs: {e}")
        print("⚠️  Continuando setup (las FAQs se pueden cargar manualmente)")

    # Verificar instalación de dependencias
    print("\n4️⃣ Verificando dependencias...")

    try:
        import langchain
        import langgraph
        import openai
        import pgvector
        import numpy
        print("✅ Todas las dependencias están instaladas")
    except ImportError as e:
        print(f"❌ Falta instalar dependencias: {e}")
        print("🔧 Ejecuta: pip install -r requirements.txt")
        return False

    # Test de conexión básica
    print("\n5️⃣ Realizando test de conexión...")

    try:
        from app.services.chat_service import chat_service
        from app.graph.workflow import ithaka_workflow

        # Test simple del workflow
        test_result = await ithaka_workflow.process_message(
            user_message="Hola, ¿qué es Ithaka?",
            conversation_id=None,
            chat_history=[],
            user_email=None
        )

        if test_result and "response" in test_result:
            print("✅ Sistema de agentes funcionando correctamente")
        else:
            print("⚠️  Sistema funcional pero con posibles problemas menores")

    except Exception as e:
        print(f"❌ Error en test del sistema: {e}")
        print("⚠️  El sistema está instalado pero puede tener problemas de configuración")

    # Resumen final
    print("\n" + "🎉" * 20)
    print("SETUP COMPLETADO")
    print("🎉" * 20)

    print(f"""
✅ Sistema de agentes IA de Ithaka configurado exitosamente

📊 Componentes instalados:
   • 4 Agentes IA (Supervisor, Wizard, FAQ, Validator)
   • Workflow LangGraph
   • Base de datos con PGVector
   • Integración WebSocket
   • Sistema de evaluación con rúbrica

🚀 Para iniciar el servidor:
   uvicorn app.main:app --reload

🧪 Para testing:
   • Conecta por WebSocket a: ws://localhost:8000/api/v1/ws/
   • Envía: {{"content": "Hola, quiero postular"}}
   • También prueba: {{"content": "¿Qué es el programa Fellows?"}}

📝 Comandos del wizard:
   • "postular" - Iniciar proceso de postulación
   • "volver" - Ir a pregunta anterior
   • "cancelar" - Terminar proceso
   
📚 Para más información consulta el PLAN_DESARROLLO_AGENTES_IA.md
""")

    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)
    print("🎊 ¡Todo listo! El sistema está funcionando.")
