#!/usr/bin/env python3
"""
Script para poblar la base de datos con las FAQs de Ithaka
"""

from app.services.embedding_service import embedding_service
from app.db.config.database import get_async_session
import asyncio
import os
import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# FAQs de Ithaka
FAQS_DATA = [
    {
        "question": "¿Qué cursos electivos puedo hacer en Ithaka?",
        "answer": "Tenemos un PDF con todos los cursos electivos https://bit.ly/ElectivasIthaka. Si te interesa el paquete completo de cursos puedes dirigirte al minor de innovación y emprendimiento https://minor-innovacion-emprend-6ucsomp.gamma.site/"
    },
    {
        "question": "¿Quiero emprender como freelancer, cómo hago?",
        "answer": "Desarrolla una marca personal y trabajar desde tu profesión es posible pero es necesario saber y haber desarrollando ciertos conocimientos, habilidades y competencias. En Ithaka tenemos cursos específicos si te interesa emprender desde tu profesión."
    },
    {
        "question": "Tengo una idea que trabajé en un curso, ¿puedo presentarla?",
        "answer": "Sí, puedes presentar tu idea a través del formulario de postulación disponible en nuestro sitio web."
    },
    {
        "question": "¿Qué es el programa Fellows?",
        "answer": "Es un programa online creado por la universidad de Stanford y dictado por la universidad de Twente que te ayuda a desarrollar habilidades intraemprendedoras en tu experiencia universitaria. Es un programa que desde UCU-Ithaka seleccionamos y becamos 4 estudiantes para que se conviertan en agentes de cambio. Además los seleccionados tienen la posibilidad de asistir al evento internacional de meetup de fellows un viaje en la universidad de Twente, Países Bajos durante 3 días (los pasajes son costeados por la UCU). https://programa-university-inno-k2jjjij.gamma.site/"
    },
    {
        "question": "¿Cuándo es la convocatoria para el programa Fellows?",
        "answer": "Durante marzo-abril se lanza la convocatoria para postulantes al programa, y luego de un proceso de selección de aprox. 1 mes con entrevistas grupales e individuales, se seleccionan 4 participantes."
    },
    {
        "question": "¿Buscan estudiantes con alguna carrera o perfil específico para Fellows?",
        "answer": "No, la selección no depende de lo que estudies sino de tu capacidad de liderar proyectos, tu compromiso, y de involucrarte con la universidad para conocer sus problemas y proponer soluciones."
    },
    {
        "question": "¿Ithaka es solo para emprendimientos con innovación?",
        "answer": "No, Ithaka es para desarrollar habilidades y competencias para emprender desde el punto de vista amplio, ya sea dentro de organizaciones como intraemprendedores, desarrollar un negocio tradicional, un negocio con innovación o emprender desde la profesión."
    },
    {
        "question": "¿Qué se necesita para postular una idea o emprendimiento?",
        "answer": "Buscamos personas que tengan una idea o negocio innovador o con valor diferencial. Deben postular la idea a través del formulario correspondiente y alguien del equipo se contactará para tener una primera reunión."
    },
    {
        "question": "¿Alguna actividad tiene costo?",
        "answer": "No, todas nuestras actividades (incubadora, programas) son gratuitas y abiertas a todo público. Nuestras mentorías están abiertas a la comunidad universitaria UCU y los cursos electivos son gratuitos para estudiantes UCU siempre y cuando tengas créditos disponibles para cursar más electivas."
    },
    {
        "question": "¿El Centro Ithaka es exclusivo para estudiantes y egresados UCU?",
        "answer": "No, el Centro Ithaka forma parte del ecosistema emprendedor y atiende a la comunidad universitaria UCU en general (futuros estudiantes, estudiantes, egresados, profesores y funcionarios) así como a emprendedores interesados en las actividades que ofrecemos."
    },
    {
        "question": "¿Qué ofrece el minor de emprendedurismo?",
        "answer": "Este programa de un semestre ofrece la posibilidad de especializarte en creatividad, innovación y mentalidad emprendedora así como desarrollar la capacidad de detectar problemáticas y proponer soluciones, a través de la generación de modelos de negocios innovadores y sustentables."
    },
    {
        "question": "¿Cómo me entero de las novedades y convocatorias del Centro?",
        "answer": "A través de nuestras redes sociales: Instagram, Twitter y LinkedIn o a través de nuestro newsletter."
    }
]


async def populate_faqs():
    """Pobla la base de datos con las FAQs"""
    print("🚀 Iniciando población de FAQs...")

    try:
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

        print("🎉 ¡Todas las FAQs fueron procesadas exitosamente!")

    except Exception as e:
        print(f"❌ Error durante la población: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(populate_faqs())
