"""Agent for therapist conversation using LangGraph."""
from typing import Any, Callable, Awaitable
from langchain.chat_models import init_chat_model
from langchain.agents import AgentState, create_agent
from langgraph.graph.state import CompiledStateGraph
from dataclasses import dataclass
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite
from langchain.messages import AIMessage, HumanMessage, get_text_from_content

from pathlib import Path
# Therapist system prompt
SYSTEM_PROMPT = """You are a supportive and empathetic virtual therapist.
Your goal is to listen carefully, ask thoughtful questions, and provide emotional support.
Be warm, non-judgmental, and help users explore their feelings and thoughts.
Keep responses concise but meaningful (2-3 sentences usually works best)."""


@dataclass
class ConversationContext:
    context_id: str
    message_id: str
    files: list[str] = []



class ConversationState(AgentState):
    files: list[str] = []




def _create_database_connection(db_path: str):
    """Create a database connection for agent checkpoints.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        An aiosqlite connection
    """
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return aiosqlite.connect(db_path)

async def iterate_agent_stream(
    agent: CompiledStateGraph[Any, ConversationContext, Any, Any],
    context_id: str,
    message_id: str,
    query: str,
    on_message: Callable[[str], Awaitable[None]],
) -> None:
    """Iterate `agent.astream` and call `on_message(text)` for each AI message chunk."""
    context = ConversationContext(context_id=context_id, message_id=message_id, files=files)
    text_blocks = []

    if len(text_blocks) > 0:
        message = [HumanMessage(content=query, content_blocks=text_blocks)]
    else:
        message = [HumanMessage(content=query)]

    accumulated_text = ""
    async for token, metadata in agent.astream(
        {"messages": message},
        {"configurable": {"thread_id": context_id}},
        context=context,
        stream_mode="messages",
    ):
        if isinstance(token, AIMessage) and token.content:
            text = get_text_from_content(token.content)
            accumulated_text += text
            await on_message(accumulated_text)

def create_nt_agent(
    model_obj=None,
    checkpointer=None,
    system_prompt: str = SYSTEM_PROMPT,
    model: str = "qwen2.5-coder:1.5b",
    model_provider: str = "ollama",
    db_path: str = "./data/agent_checkpoints.db",
) -> CompiledStateGraph[Any, ConversationContext, Any, Any]:
    """Factory creating a configured LangChain agent.

    Args:
        model_obj: Optional pre-configured chat model. If None, creates a new one.
        checkpointer: Optional pre-configured checkpointer. If None, creates a new one.
        system_prompt: System prompt for the agent
        model: Model name (used if model_obj is None)
        model_provider: Model provider (used if model_obj is None)
        db_path: Path to database file (used if checkpointer is None)

    Returns:
        A compiled LangGraph agent
    """
    if model_obj is None:
        model_obj = init_chat_model(model=model, model_provider=model_provider)

    if checkpointer is None:
        conn = _create_database_connection(db_path)
        checkpointer = AsyncSqliteSaver(conn)

    return create_agent(
        model=model_obj,
        state_schema=ConversationState,
        checkpointer=checkpointer,
        context_schema=ConversationContext,
        system_prompt=system_prompt,
    )

