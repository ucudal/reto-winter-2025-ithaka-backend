from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

from app.services.faq_service import faq_service
from app.schemas.chat_schemas import FAQEntryResponse

router = APIRouter()


class FAQSearchRequest(BaseModel):
    query: str
    max_results: int = 3


class FAQSearchResponse(BaseModel):
    query: str
    results: List[dict]
    total_found: int


@router.post("/search", response_model=FAQSearchResponse)
async def search_faqs(request: FAQSearchRequest):
    """
    Busca FAQs usando búsqueda semántica con ChromaDB
    """
    try:
        if not request.query.strip():
            raise HTTPException(
                status_code=400, detail="La consulta no puede estar vacía")

        results = faq_service.search_faqs(
            request.query, n_results=request.max_results)

        return FAQSearchResponse(
            query=request.query,
            results=results,
            total_found=len(results)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda de FAQs: {str(e)}"
        )


@router.get("/search/{query}")
async def search_faqs_get(
    query: str,
    max_results: int = Query(
        3, ge=1, le=10, description="Número máximo de resultados")
):
    """
    Busca FAQs usando método GET (alternativa simple)
    """
    try:
        results = faq_service.search_faqs(query, n_results=max_results)

        return {
            "query": query,
            "results": results,
            "total_found": len(results)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda de FAQs: {str(e)}"
        )


@router.get("/categories")
async def get_faq_categories():
    """
    Obtiene todas las categorías disponibles de FAQs
    """
    try:
        categories = faq_service.get_all_categories()
        return {
            "categories": categories,
            "total": len(categories)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo categorías: {str(e)}"
        )


@router.get("/category/{category}")
async def get_faqs_by_category(category: str):
    """
    Obtiene todas las FAQs de una categoría específica
    """
    try:
        faqs = faq_service.get_faqs_by_category(category)

        if not faqs:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron FAQs para la categoría '{category}'"
            )

        return {
            "category": category,
            "faqs": faqs,
            "total": len(faqs)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo FAQs de categoría: {str(e)}"
        )


@router.get("/all")
async def get_all_faqs():
    """
    Obtiene todas las FAQs disponibles agrupadas por categoría
    """
    try:
        categories = faq_service.get_all_categories()
        all_faqs = {}

        for category in categories:
            all_faqs[category] = faq_service.get_faqs_by_category(category)

        total_faqs = sum(len(faqs) for faqs in all_faqs.values())

        return {
            "faqs_by_category": all_faqs,
            "categories": categories,
            "total_faqs": total_faqs,
            "total_categories": len(categories)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo todas las FAQs: {str(e)}"
        )


@router.post("/add")
async def add_faq(
    question: str,
    answer: str,
    category: str = "general",
    keywords: str = ""
):
    """
    Agrega una nueva FAQ al sistema (para administradores)
    """
    try:
        if not question.strip() or not answer.strip():
            raise HTTPException(
                status_code=400,
                detail="La pregunta y respuesta son obligatorias"
            )

        success = faq_service.add_faq(question, answer, category, keywords)

        if success:
            return {
                "message": "FAQ agregada exitosamente",
                "question": question,
                "category": category
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Error agregando FAQ"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error agregando FAQ: {str(e)}"
        )


@router.get("/popular")
async def get_popular_faqs(limit: int = Query(5, ge=1, le=10)):
    """
    Obtiene las FAQs más relevantes/populares
    Simulado por ahora - en producción podría basarse en analytics
    """
    try:
        # Por ahora retornamos FAQs de diferentes categorías
        popular_queries = [
            "cursos electivos",
            "programa fellows",
            "emprendimiento",
            "postular idea",
            "recursos ithaka"
        ]

        popular_faqs = []
        for query in popular_queries[:limit]:
            results = faq_service.search_faqs(query, n_results=1)
            if results:
                popular_faqs.append(results[0])

        return {
            "popular_faqs": popular_faqs,
            "total": len(popular_faqs)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo FAQs populares: {str(e)}"
        )
