"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from pydantic import ConfigDict


class MessageBase(BaseModel):
    """Base schema for messages."""
    role: str  # "user" or "assistant"
    content: str


class MessageCreate(BaseModel):
    """Schema for creating a message."""
    content: str


class MessageResponse(BaseModel):
    """Schema for message response."""
    role: str
    content: str
    
    model_config = ConfigDict(from_attributes=True)


class ConversationBase(BaseModel):
    """Base schema for conversations."""
    title: Optional[str] = None


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation."""
    pass


class ConversationResponse(ConversationBase):
    """Schema for conversation response with messages."""
    id: int
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    """Schema for listing conversations without full message history."""
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    """Schema for chat message request."""
    conversation_id: Optional[int] = None
    message: str

    @field_validator('message')
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()


class ChatResponse(BaseModel):
    """Schema for chat response with both user and assistant messages."""
    conversation_id: int
    assistant_message: MessageResponse
    
    model_config = ConfigDict(from_attributes=True)
