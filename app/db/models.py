from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from .config.database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("Message", back_populates="conversation")
    postulations = relationship("Postulation", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conv_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    ts = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")

class Postulation(Base):
    __tablename__ = "postulations"
    id = Column(Integer, primary_key=True, index=True)
    conv_id = Column(Integer, ForeignKey("conversations.id"))
    payload_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="postulations")