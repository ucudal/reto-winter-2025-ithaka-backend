from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Postulation
from app.db.config.database import get_async_session
from app.services.scoring_service import procesar_postulaciones, procesar_postulacion_especifica
from app.services.score_engine import evaluar_postulacion
from app.services.ai_score_engine import evaluar_postulacion_ai
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class ScoringRequest(BaseModel):
    texto: str
    use_ai: bool = False

class ScoringResponse(BaseModel):
    creatividad: int
    claridad: int
    compromiso: int
    score_total: float
    analisis: Optional[str] = None

class PostulationResponse(BaseModel):
    id: int
    conv_id: int
    payload_json: dict
    created_at: datetime
    creatividad: Optional[int]
    claridad: Optional[int]
    compromiso: Optional[int]
    score_total: Optional[float]

@router.post("/scoring/evaluate", response_model=ScoringResponse)
async def evaluate_text(request: ScoringRequest) -> ScoringResponse:
    """
    Evalúa un texto y retorna los scores de creatividad, claridad y compromiso.
    Puede usar motor de reglas o IA según el parámetro use_ai.
    """
    try:
        if request.use_ai:
            scores = await evaluar_postulacion_ai(request.texto)
        else:
            scores = evaluar_postulacion(request.texto)
        
        return ScoringResponse(**scores)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluando texto: {str(e)}")

@router.post("/scoring/process-all")
async def process_all_postulations(
    use_ai: bool = Query(False, description="Usar motor de IA en lugar de reglas")
):
    """
    Procesa todas las postulaciones que no tienen score asignado.
    """
    try:
        await procesar_postulaciones(use_ai=use_ai)
        return {
            "message": "Todas las postulaciones han sido procesadas exitosamente",
            "motor_utilizado": "IA" if use_ai else "Reglas"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando postulaciones: {str(e)}")

@router.post("/scoring/process/{postulation_id}")
async def process_specific_postulation(
    postulation_id: int,
    use_ai: bool = Query(False, description="Usar motor de IA en lugar de reglas")
):
    """
    Procesa una postulación específica por ID.
    """
    try:
        scores = await procesar_postulacion_especifica(postulation_id, use_ai=use_ai)
        if scores:
            return {
                "message": f"Postulación {postulation_id} procesada exitosamente",
                "motor_utilizado": "IA" if use_ai else "Reglas",
                "scores": scores
            }
        else:
            raise HTTPException(status_code=404, detail=f"Postulación {postulation_id} no encontrada")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando postulación: {str(e)}")

@router.get("/scoring/postulations", response_model=List[PostulationResponse])
async def get_postulations(
    session: AsyncSession = Depends(get_async_session)
) -> List[PostulationResponse]:
    """
    Obtiene todas las postulaciones con sus scores.
    """
    try:
        result = await session.execute(select(Postulation))
        postulations = result.scalars().all()
        
        return [
            PostulationResponse(
                id=p.id,
                conv_id=p.conv_id,
                payload_json=p.payload_json,
                created_at=p.created_at,
                creatividad=p.creatividad,
                claridad=p.claridad,
                compromiso=p.compromiso,
                score_total=p.score_total
            ) for p in postulations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo postulaciones: {str(e)}")

@router.get("/scoring/postulations/{postulation_id}", response_model=PostulationResponse)
async def get_postulation(
    postulation_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> PostulationResponse:
    """
    Obtiene una postulación específica por ID.
    """
    try:
        result = await session.execute(
            select(Postulation).where(Postulation.id == postulation_id)
        )
        postulation = result.scalar_one_or_none()
        
        if not postulation:
            raise HTTPException(status_code=404, detail=f"Postulación {postulation_id} no encontrada")
        
        return PostulationResponse(
            id=postulation.id,
            conv_id=postulation.conv_id,
            payload_json=postulation.payload_json,
            created_at=postulation.created_at,
            creatividad=postulation.creatividad,
            claridad=postulation.claridad,
            compromiso=postulation.compromiso,
            score_total=postulation.score_total
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo postulación: {str(e)}") 