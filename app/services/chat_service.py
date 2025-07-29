from sqlalchemy.orm import Session
from app.db.models import Conversation, Message
from datetime import datetime

def create_conversation(db: Session, email: str = None, started_at: datetime = None):
    conv = Conversation(
        email=email,
        started_at=started_at or datetime.utcnow()
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv

def add_message(db: Session, conv_id: int, role: str, content: str, ts: datetime = None):
    msg = Message(
        conv_id=conv_id,
        role=role,
        content=content,
        ts=ts or datetime.utcnow()
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def get_conversation(db: Session, conv_id: int):
    return (
        db.query(Conversation)
        .filter(Conversation.id == conv_id)
        .first()
    )

def get_messages_for_conversation(db: Session, conv_id: int):
    return (
        db.query(Message)
        .filter(Message.conv_id == conv_id)
        .order_by(Message.ts)
        .all()
    )
