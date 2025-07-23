from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel

from app.services.chat_service import chat_service
from app.websockets.handlers import get_conversation_history
from app.schemas.chat_schemas import ChatMessageCreate, ChatbotResponse

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str
    context: Dict[str, Any] = {}


class ChatHistoryResponse(BaseModel):
    messages: list
    current_step: int
    application_data: Dict[str, Any]


@router.post("/message", response_model=ChatbotResponse)
async def send_message(request: ChatRequest):
    """
    Envía un mensaje al chatbot y obtiene una respuesta
    Alternativa REST al WebSocket
    """
    try:
        if not request.message.strip():
            raise HTTPException(
                status_code=400, detail="El mensaje no puede estar vacío")

        # Procesar mensaje con el servicio de IA
        response = await chat_service.process_message(
            message=request.message,
            session_id=request.session_id,
            conversation_data=request.context
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando mensaje: {str(e)}"
        )


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str):
    """
    Obtiene el historial completo de una conversación
    """
    try:
        history = await get_conversation_history(session_id)
        return ChatHistoryResponse(**history)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo historial: {str(e)}"
        )


@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Limpia el historial de una conversación (para testing)
    """
    try:
        # Implementar lógica para limpiar historial
        # Por ahora solo retornamos success
        return {"message": f"Historial de {session_id} limpiado exitosamente"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error limpiando historial: {str(e)}"
        )


@router.get("/wizard/steps")
async def get_wizard_steps():
    """
    Obtiene información sobre los pasos del wizard
    """
    from app.services.wizard_config import WIZARD_STEPS

    return {
        "total_steps": len(WIZARD_STEPS),
        "steps": [
            {
                "step_number": step.step_number,
                "question": step.question,
                "field_name": step.field_name,
                "validation_type": step.validation_type,
                "options": step.options,
                "required": step.required,
                "depends_on": step.depends_on
            }
            for step in WIZARD_STEPS
        ]
    }


@router.post("/wizard/validate")
async def validate_wizard_data(data: Dict[str, Any]):
    """
    Valida los datos del wizard sin procesar mensaje
    """
    from app.services.wizard_config import is_wizard_complete

    try:
        is_complete = is_wizard_complete(data)

        # Calcular progreso
        required_fields = ["full_name", "email", "phone", "document_id", "country_city",
                           "campus_preference", "ucu_relation", "how_found_ithaka", "motivation", "has_idea"]

        if data.get("has_idea"):
            required_fields.extend([
                "problem_opportunity", "solution_clients", "innovation_differential",
                "business_model", "project_stage", "support_needed"
            ])

        completed_fields = sum(
            1 for field in required_fields if data.get(field))
        progress_percentage = (completed_fields / len(required_fields)) * 100

        return {
            "is_complete": is_complete,
            "progress_percentage": round(progress_percentage, 1),
            "completed_fields": completed_fields,
            "total_fields": len(required_fields),
            "missing_fields": [field for field in required_fields if not data.get(field)]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error validando datos: {str(e)}"
        )
