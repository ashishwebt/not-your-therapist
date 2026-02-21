"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class MessageBase(BaseModel):
    """Base schema for messages."""
    role: str  # "user" or "assistant"
    content: str


class MessageCreate(BaseModel):
    """Schema for creating a message."""
    content: str


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: int
    role: str
    content: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


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
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Schema for listing conversations without full message history."""
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Schema for chat message request."""
    conversation_id: Optional[int] = None
    message: str


class ChatResponse(BaseModel):
    """Schema for chat response with both user and assistant messages."""
    conversation_id: int
    user_message: MessageResponse
    assistant_message: MessageResponse

    class Config:
        from_attributes = True
