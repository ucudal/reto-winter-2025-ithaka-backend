import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from app.config.settings import settings

# FAQs de Ithaka basadas en los ejemplos proporcionados
ITHAKA_FAQS = [
    {
        "question": "¿Qué cursos electivos puedo hacer en Ithaka?",
        "answer": "Tenemos un PDF con todos los cursos electivos https://bit.ly/ElectivasIthaka, si te interesa el paquete completo de cursos puedes dirigirte al minor de innovación y emprendimiento https://minor-innovacion-emprend-6ucsomp.gamma.site/",
        "category": "cursos",
        "keywords": "cursos electivos minor innovación emprendimiento clases materias"
    },
    {
        "question": "¿Quiero emprender como freelancer, cómo hago?",
        "answer": "Desarrollar una marca personal y trabajar desde tu profesión es posible pero es necesario saber y haber desarrollado ciertos conocimientos, habilidades y competencias. En Ithaka tenemos cursos específicos si te interesa emprender desde tu profesión.",
        "category": "emprendimiento",
        "keywords": "freelancer marca personal profesión independiente"
    },
    {
        "question": "Tengo una idea que trabajé en un curso, ¿puedo presentarla?",
        "answer": "¡Por supuesto! Puedes presentar tu idea a través del formulario de postulación. Estamos aquí para ayudarte a desarrollar cualquier idea innovadora que tengas.",
        "category": "postulacion",
        "keywords": "idea curso presentar postular formulario"
    },
    {
        "question": "¿Qué es el programa Fellows?",
        "answer": "Es un programa online creado por la Universidad de Stanford y dictado por la Universidad de Twente que te ayuda a desarrollar habilidades intraemprendedoras en tu experiencia universitaria. Es un programa que desde UCU-Ithaka seleccionamos y becamos 4 estudiantes para que se conviertan en agentes de cambio. Además los seleccionados tienen la posibilidad de asistir al evento internacional de meetup de fellows - un viaje a la Universidad de Twente, Países Bajos durante 3 días (los pasajes son costeados por la UCU). https://programa-university-inno-k2jjjij.gamma.site/",
        "category": "fellows",
        "keywords": "fellows stanford twente intraemprendedor beca viaje holanda"
    },
    {
        "question": "¿Cuándo es la convocatoria para Fellows?",
        "answer": "Durante marzo-abril se lanza la convocatoria para postulantes al programa, y luego de un proceso de selección de aproximadamente 1 mes con entrevistas grupales e individuales, se seleccionan 4 participantes.",
        "category": "fellows",
        "keywords": "convocatoria fellows marzo abril selección entrevista"
    },
    {
        "question": "¿Buscan estudiantes con alguna carrera o perfil específico para Fellows?",
        "answer": "No, la selección no depende de lo que estudies sino de tu capacidad de liderar proyectos, tu compromiso, y de involucrarte con la universidad para conocer sus problemas y proponer soluciones.",
        "category": "fellows",
        "keywords": "carrera perfil estudiante liderazgo compromiso"
    },
    {
        "question": "¿Ithaka es solo para emprendimientos con innovación?",
        "answer": "No, Ithaka es para desarrollar habilidades y competencias para emprender desde el punto de vista amplio, ya sea dentro de organizaciones como intraemprendedores, desarrollar un negocio tradicional, un negocio con innovación o emprender desde la profesión.",
        "category": "emprendimiento",
        "keywords": "innovación tradicional intraemprendedor organizaciones profesión"
    },
    {
        "question": "¿Con qué recursos me puede ayudar Ithaka si quiero emprender?",
        "answer": "Ithaka ofrece diversos recursos como: tutoría para validar ideas, soporte para armar planes de negocio, ayuda para obtener financiamiento, capacitación, mentoría, y apoyo específico según las necesidades de tu proyecto emprendedor.",
        "category": "recursos",
        "keywords": "recursos ayuda tutoría financiamiento capacitación mentoría"
    },
    {
        "question": "¿Cómo puedo postular mi idea a Ithaka?",
        "answer": "Puedes postular completando nuestro formulario de postulación. El proceso incluye datos personales y, si tienes una idea o emprendimiento, información específica sobre tu proyecto. Te contactaremos a la brevedad para seguir el proceso.",
        "category": "postulacion",
        "keywords": "postular idea formulario proceso datos proyecto"
    },
    {
        "question": "¿Qué tipo de apoyo ofrece Ithaka?",
        "answer": "Ofrecemos múltiples tipos de apoyo: tutoría para validar ideas, soporte para planes de negocio, ayuda con financiamiento, capacitación especializada, cursos electivos, el programa Fellows, y apoyo personalizado según las necesidades específicas de cada emprendedor.",
        "category": "recursos",
        "keywords": "apoyo tutoría validación plan negocio financiamiento capacitación"
    }
]


class FAQService:
    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.embeddings = None
        self._initialize_chroma()
        self._initialize_faqs()

    def _initialize_chroma(self):
        """Inicializa ChromaDB"""
        try:
            # Crear directorio si no existe
            os.makedirs(settings.chroma_db_path, exist_ok=True)

            self.chroma_client = chromadb.PersistentClient(
                path=settings.chroma_db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # Crear o obtener colección
            self.collection = self.chroma_client.get_or_create_collection(
                name="ithaka_faqs",
                metadata={"hnsw:space": "cosine"}
            )

            print(f"ChromaDB inicializado en: {settings.chroma_db_path}")

        except Exception as e:
            print(f"Error inicializando ChromaDB: {e}")
            self.chroma_client = None
            self.collection = None

    def _initialize_embeddings(self):
        """Inicializa el modelo de embeddings solo si tenemos API key"""
        if settings.openai_api_key:
            try:
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=settings.openai_api_key,
                    model="text-embedding-3-small"
                )
                print("Embeddings OpenAI inicializados")
            except Exception as e:
                print(f"Error inicializando embeddings: {e}")
                self.embeddings = None
        else:
            print("API key de OpenAI no configurada, usando búsqueda básica")
            self.embeddings = None

    def _initialize_faqs(self):
        """Carga las FAQs iniciales en ChromaDB"""
        if not self.collection:
            return

        try:
            # Verificar si ya hay datos
            count = self.collection.count()
            if count > 0:
                print(f"FAQs ya cargadas: {count} documentos")
                return

            # Preparar documentos
            documents = []
            metadatas = []
            ids = []

            for i, faq in enumerate(ITHAKA_FAQS):
                # Combinar pregunta y respuesta para búsqueda más efectiva
                full_text = f"Pregunta: {faq['question']}\nRespuesta: {faq['answer']}"

                documents.append(full_text)
                metadatas.append({
                    "question": faq["question"],
                    "answer": faq["answer"],
                    "category": faq["category"],
                    "keywords": faq["keywords"]
                })
                ids.append(f"faq_{i}")

            # Agregar a ChromaDB
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            print(f"FAQs cargadas exitosamente: {len(ITHAKA_FAQS)} documentos")

        except Exception as e:
            print(f"Error cargando FAQs: {e}")

    def search_faqs(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Busca FAQs relevantes usando búsqueda semántica
        """
        if not self.collection:
            return self._fallback_search(query, n_results)

        try:
            # Buscar en ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["metadatas", "documents", "distances"]
            )

            # Formatear resultados
            formatted_results = []
            if results["metadatas"] and results["metadatas"][0]:
                for i, metadata in enumerate(results["metadatas"][0]):
                    formatted_results.append({
                        "question": metadata["question"],
                        "answer": metadata["answer"],
                        "category": metadata["category"],
                        "relevance_score": 1 - results["distances"][0][i] if results["distances"] else 0.5
                    })

            return formatted_results

        except Exception as e:
            print(f"Error en búsqueda semántica: {e}")
            return self._fallback_search(query, n_results)

    def _fallback_search(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Búsqueda de respaldo usando coincidencia de palabras clave
        """
        query_lower = query.lower()
        results = []

        for faq in ITHAKA_FAQS:
            score = 0

            # Buscar en pregunta
            if any(word in faq["question"].lower() for word in query_lower.split()):
                score += 2

            # Buscar en respuesta
            if any(word in faq["answer"].lower() for word in query_lower.split()):
                score += 1

            # Buscar en palabras clave
            if any(word in faq["keywords"].lower() for word in query_lower.split()):
                score += 1

            if score > 0:
                results.append({
                    "question": faq["question"],
                    "answer": faq["answer"],
                    "category": faq["category"],
                    "relevance_score": score / 4  # Normalizar
                })

        # Ordenar por relevancia
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:n_results]

    def get_all_categories(self) -> List[str]:
        """Retorna todas las categorías de FAQs disponibles"""
        return list(set(faq["category"] for faq in ITHAKA_FAQS))

    def get_faqs_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Retorna todas las FAQs de una categoría específica"""
        return [
            {
                "question": faq["question"],
                "answer": faq["answer"],
                "category": faq["category"],
                "keywords": faq["keywords"]
            }
            for faq in ITHAKA_FAQS
            if faq["category"] == category
        ]

    def add_faq(self, question: str, answer: str, category: str = "general", keywords: str = ""):
        """Agrega una nueva FAQ al sistema"""
        if not self.collection:
            print("ChromaDB no disponible")
            return False

        try:
            # Obtener siguiente ID
            count = self.collection.count()
            new_id = f"faq_{count}"

            # Preparar documento
            full_text = f"Pregunta: {question}\nRespuesta: {answer}"
            metadata = {
                "question": question,
                "answer": answer,
                "category": category,
                "keywords": keywords
            }

            # Agregar a ChromaDB
            self.collection.add(
                documents=[full_text],
                metadatas=[metadata],
                ids=[new_id]
            )

            print(f"FAQ agregada exitosamente: {new_id}")
            return True

        except Exception as e:
            print(f"Error agregando FAQ: {e}")
            return False


# Instancia global del servicio
faq_service = FAQService()
