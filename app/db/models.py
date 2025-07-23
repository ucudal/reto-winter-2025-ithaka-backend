from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.config.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    # Opcional, para usuarios autenticados
    user_id = Column(String(255), index=True)
    # active, completed, abandoned
    status = Column(String(50), default="active")
    current_step = Column(Integer, default=0)  # Paso actual del wizard
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relaciones
    messages = relationship("ChatMessage", back_populates="conversation")
    applications = relationship("Application", back_populates="conversation")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey(
        "conversations.id"), nullable=False)
    message = Column(Text, nullable=False)
    sender = Column(String(50), nullable=False)  # user, assistant, system
    # text, system, validation_error, etc.
    message_type = Column(String(50), default="text")
    timestamp = Column(DateTime, default=func.now())
    # Para información adicional como step_data, validation_errors, etc.
    meta_data = Column(JSON)

    # Relaciones
    conversation = relationship("Conversation", back_populates="messages")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey(
        "conversations.id"), nullable=False)

    # Datos personales (preguntas 1-12)
    full_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    document_id = Column(String(50))
    country_city = Column(String(255))
    campus_preference = Column(String(100))  # Maldonado, Montevideo, Salto
    ucu_relation = Column(String(100))  # Estudiante, Graduado, etc.
    faculty = Column(String(255))
    how_found_ithaka = Column(String(255))
    motivation = Column(Text)
    has_idea = Column(Boolean, default=False)
    additional_comments = Column(Text)

    # Datos del emprendimiento (preguntas 13-20) - solo si has_idea = True
    team_composition = Column(Text)
    team_members_data = Column(Text)
    is_first_venture = Column(Boolean)
    problem_opportunity = Column(Text)
    solution_clients = Column(Text)
    innovation_differential = Column(Text)
    business_model = Column(Text)
    project_stage = Column(String(100))
    support_needed = Column(Text)
    additional_info = Column(Text)

    # Metadata
    status = Column(String(50), default="draft")  # draft, completed, submitted
    completion_percentage = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    submitted_at = Column(DateTime)

    # Relaciones
    conversation = relationship("Conversation", back_populates="applications")


class FAQEntry(Base):
    __tablename__ = "faq_entries"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100))  # cursos, emprendimiento, fellows, etc.
    keywords = Column(Text)  # palabras clave para búsqueda
    priority = Column(Integer, default=0)  # para ordenar resultados
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
