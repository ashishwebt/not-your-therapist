"""Agent for therapist conversation using LangGraph."""
from typing import Any
from langchain.chat_models import init_chat_model
from langchain.agents import AgentState, create_agent
from langchain.messages import HumanMessage, AIMessage
from langgraph.graph.state import CompiledStateGraph
from dataclasses import dataclass, field
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite
from langchain_core.runnables import RunnableConfig
from pathlib import Path
from app.agent_services.base import Agent, Message



SYSTEM_PROMPT = """You are a supportive and empathetic virtual therapist.
Your goal is to listen carefully, ask thoughtful questions, and provide emotional support.
Be warm, non-judgmental, and help users explore their feelings and thoughts.
Keep responses concise but meaningful (2-3 sentences usually works best)."""


@dataclass
class ConversationContext:
    context_id: str
    message_id: str
    files: list[str] = field(default_factory=list)

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

def to_human_message(msg: Message) -> HumanMessage:
    """Convert Message DTO to LangChain HumanMessage."""
    return HumanMessage(content=msg.content)




class LangChainAgent(Agent):
    """LangChain agent implementation of the Agent interface."""

    def __init__(self, agent: CompiledStateGraph):
        self.agent = agent

    async def stream_chat(self, message: str, thread_id: str):
        """Stream chat messages from agent."""
        state = ConversationState(
            messages=[to_human_message(Message(role="user", content=message))],
            context_id=thread_id
        )
        config = {"configurable": {"thread_id": thread_id}}

        async for token, metadata in self.agent.astream(state, config, stream_mode="messages"):
            if isinstance(token, AIMessage) and isinstance(token.content, str) and token.content:
                yield Message(role="assistant", content=token.content)

    async def get_thread(self, thread_id: str) -> list[Message]:
        """Retrieve conversation thread messages."""
        config = {"configurable": {"thread_id": thread_id}}

        state = await self.agent.aget_state(config)
        messages = state.values.get("messages", [])
        
        result = []
        for msg in messages:
            if isinstance(msg, AIMessage):
                result.append(Message(role="assistant", content=msg.content))
            elif isinstance(msg, HumanMessage):
                result.append(Message(role="user", content=msg.content))
        
        return result

    
def create_nt_agent(
    model_obj=None,
    checkpointer=None,
    system_prompt: str = SYSTEM_PROMPT,
    model: str = "qwen2.5-coder:1.5b",
    model_provider: str = "ollama",
    db_path: str = "./data/agent_checkpoints.db",
) -> LangChainAgent:
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

    langchain_agent =create_agent(
        model=model_obj,
        state_schema=ConversationState,
        checkpointer=checkpointer,
        context_schema=ConversationContext,
        system_prompt=system_prompt,
    )
    return LangChainAgent(langchain_agent)