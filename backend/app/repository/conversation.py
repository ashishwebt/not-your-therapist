"""Conversation model and repository operations."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, desc
from sqlalchemy.orm import Session
from app.repository.database import Base


class Conversation(Base):
    """Conversation metadata model."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), default="New Conversation")
    thread_id = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Repository functions - just query helpers
def create(db: Session, title: str = None, thread_id: str = None) -> Conversation:
    """Create new conversation."""
    import uuid
    conv = Conversation(title=title or "New Conversation", thread_id=thread_id or str(uuid.uuid4()))
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def get(db: Session, conversation_id: int) -> Conversation | None:
    """Get conversation by ID."""
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def list_all(db: Session, skip: int = 0, limit: int = 100) -> list[Conversation]:
    """List all conversations."""
    return db.query(Conversation).order_by(desc(Conversation.updated_at)).offset(skip).limit(limit).all()


def delete(db: Session, conversation_id: int) -> bool:
    """Delete conversation."""
    conv = get(db, conversation_id)
    if not conv:
        return False
    db.delete(conv)
    db.commit()
    return True
