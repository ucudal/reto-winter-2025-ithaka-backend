from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, EmailStr


class ChatMessageBase(BaseModel):
    message: str
    sender: str = Field(
        default="user", description="user, assistant, or system")
    message_type: str = Field(
        default="text", description="text, system, validation_error, etc.")
    meta_data: Optional[Dict[str, Any]] = None


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageResponse(ChatMessageBase):
    id: int
    conversation_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    session_id: str
    user_id: Optional[str] = None


class ConversationResponse(BaseModel):
    id: int
    session_id: str
    user_id: Optional[str]
    status: str
    current_step: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationCreate(BaseModel):
    # Datos personales
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    document_id: Optional[str] = None
    country_city: Optional[str] = None
    campus_preference: Optional[str] = Field(
        None, description="Maldonado, Montevideo, Salto")
    ucu_relation: Optional[str] = Field(
        None, description="Estudiante, Graduado, Funcionario o Docente, etc.")
    faculty: Optional[str] = None
    how_found_ithaka: Optional[str] = None
    motivation: Optional[str] = None
    has_idea: Optional[bool] = False
    additional_comments: Optional[str] = None

    # Datos del emprendimiento
    team_composition: Optional[str] = None
    team_members_data: Optional[str] = None
    is_first_venture: Optional[bool] = None
    problem_opportunity: Optional[str] = None
    solution_clients: Optional[str] = None
    innovation_differential: Optional[str] = None
    business_model: Optional[str] = None
    project_stage: Optional[str] = None
    support_needed: Optional[str] = None
    additional_info: Optional[str] = None


class ApplicationResponse(ApplicationCreate):
    id: int
    conversation_id: int
    status: str
    completion_percentage: int
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WizardStep(BaseModel):
    step_number: int
    question: str
    field_name: str
    validation_type: str = "text"  # text, email, phone, select, etc.
    options: Optional[List[str]] = None  # Para preguntas de selección múltiple
    required: bool = True
    # Condiciones para mostrar esta pregunta
    depends_on: Optional[Dict[str, Any]] = None


class FAQEntryCreate(BaseModel):
    question: str
    answer: str
    category: Optional[str] = None
    keywords: Optional[str] = None
    priority: int = 0
    active: bool = True


class FAQEntryResponse(FAQEntryCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatbotResponse(BaseModel):
    message: str
    message_type: str = "text"
    next_step: Optional[int] = None
    validation_errors: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    meta_data: Optional[Dict[str, Any]] = None
