"""Dependency injection for FastAPI."""
from functools import lru_cache
from app.agent_services.base import Agent
from app.agent_services.agent import create_nt_agent


@lru_cache(maxsize=1)
def get_agent() -> Agent:
    """Get or create the agent singleton.
    
    Uses LRU cache to ensure only one instance is created.
    This can be easily swapped with another implementation by modifying
    this single function.
    
    Returns:
        An Agent implementation instance
    """
    return create_nt_agent()
