"""Abstract agent interface for dependency injection."""
from abc import ABC, abstractmethod
from typing import AsyncIterator
from pydantic import BaseModel


class Message(BaseModel):
    """Simple message DTO."""
    role: str  # "user" or "assistant"
    content: str


class Agent(ABC):
    """Abstract agent interface for dependency injection."""

    @abstractmethod
    async def stream_chat(
        self, message: str, thread_id: str
    ) -> AsyncIterator[Message]:
        """Stream chat messages from agent.
        
        Args:
            message: The user message
            thread_id: The conversation thread ID
            
        Yields:
            Message: Assistant messages
        """
        pass

    @abstractmethod
    async def get_thread(self, thread_id: str) -> list[Message]:
        """Retrieve conversation thread messages.
        
        Args:
            thread_id: The conversation thread ID
            
        Returns:
            List of messages in the thread
        """
        pass
