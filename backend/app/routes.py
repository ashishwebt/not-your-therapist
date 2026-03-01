"""API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.repository.database import get_db
from app.repository import conversation as repo
from app.agent_services.agent import (
    create_nt_agent,
    ConversationState,
    get_agent_thread,
    Message,
    to_human_message,
    stream_chat,
)
from app.schemas import (
    ConversationResponse,
    ConversationListResponse,
    ChatRequest,
    MessageResponse,
    ChatResponse
)
from app.sse_helper import SSEStream
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
async def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Get conversation by ID."""
    conv = repo.get(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    config = {"configurable": {"thread_id": conv.thread_id}}
    messages = await get_agent_thread(agent, config)

    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[
            MessageResponse(
                id=i,
                role=msg.role,
                content=msg.content,
                created_at=None,
            )
            for i, msg in enumerate(messages)
        ]
    )



@router.post("/chat")
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    """Send message and get streamed response."""
    if req.conversation_id is None:
        conv = repo.create(db, title="New conversation")
    else:
        conv = repo.get(db, req.conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    async def stream_generator():
        accumulated_text = ""
        async for msg in stream_chat(agent, req.message, conv.thread_id):
            accumulated_text += msg.content
            payload = ChatResponse(
                conversation_id=conv.id,
                assistant_message=MessageResponse(
                    id=0,
                    role="assistant",
                    content=msg.content,
                    created_at=None,
                ),
            )
            yield SSEStream.format(payload)

        final_payload = ChatResponse(
            conversation_id=conv.id,
            assistant_message=MessageResponse(
                id=0,
                role="assistant",
                content=accumulated_text,
                created_at=None,
            ),
        )
        yield SSEStream.done(final_payload)

    return SSEStream.response(stream_generator(), headers={"X-Conversation-Id": str(conv.id)})

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

