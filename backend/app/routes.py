"""API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage

from app.repository.database import get_db
from app.repository import conversation as repo
from app.agent_services.agent import create_nt_agent, ConversationState
from app.schemas import (
    ConversationResponse,
    ConversationListResponse,
    ChatRequest,
    ChatResponse,
    MessageResponse,
)

router = APIRouter()
agent = create_nt_agent()


@router.get("/conversations", response_model=list[ConversationListResponse])
def list_conversations(db: Session = Depends(get_db)):
    """List all conversations."""
    convs = repo.list_all(db)
    return [
        ConversationListResponse(
            id=c.id, title=c.title, created_at=c.created_at, updated_at=c.updated_at
        )
        for c in convs
    ]


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Get conversation by ID."""
    conv = repo.get(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationResponse(
        id=conv.id, title=conv.title, created_at=conv.created_at, updated_at=conv.updated_at, messages=[]
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    """Send message and get response."""
    print("tt")
    if req.conversation_id is None:
        conv = repo.create(db, title="Conversation")
    else:
        conv = repo.get(db, req.conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # Run through agent
    state = ConversationState(messages=[HumanMessage(content=req.message)], context_id=conv.thread_id)
    config = {"configurable": {"thread_id": conv.thread_id}}
    result = await agent.ainvoke(state, config=config)

    if len(result.messages) < 2:
        raise HTTPException(status_code=500, detail="Failed to generate response")

    assistant_msg = result.messages[-1]
    if not isinstance(assistant_msg, AIMessage):
        raise HTTPException(status_code=500, detail="Invalid response type")

    return ChatResponse(
        conversation_id=conv.id,
        user_message=MessageResponse(id=0, role="user", content=req.message, created_at=None),
        assistant_message=MessageResponse(id=0, role="assistant", content=assistant_msg.content, created_at=None),
    )


@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Delete conversation."""
    if not repo.delete(db, conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"deleted": True}


@router.get("/health")
def health():
    """Health check."""
    return {"status": "ok", "version": "0.2.0"}

