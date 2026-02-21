"""Tests for API routes."""
from unittest.mock import Mock, patch, AsyncMock
import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app.repository import conversation as repo


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_list_conversations_empty(client):
    """Test listing conversations when none exist."""
    response = client.get("/conversations")

    assert response.status_code == 200
    assert response.json() == []


def test_list_conversations(client, db_session):
    """Test listing conversations."""
    repo.create(db_session, title="Conv 1")
    repo.create(db_session, title="Conv 2")

    response = client.get("/conversations")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] in ["Conv 1", "Conv 2"]


def test_get_conversation(client, db_session):
    """Test getting a specific conversation."""
    conv = repo.create(db_session, title="Test Conv")

    response = client.get(f"/conversations/{conv.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == conv.id
    assert data["title"] == "Test Conv"
    assert "created_at" in data
    assert "updated_at" in data
    assert data["messages"] == []


def test_get_conversation_not_found(client):
    """Test getting non-existent conversation."""
    response = client.get("/conversations/9999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_conversation(client, db_session):
    """Test deleting a conversation."""
    conv = repo.create(db_session, title="To Delete")

    response = client.delete(f"/conversations/{conv.id}")

    assert response.status_code == 200
    assert response.json()["deleted"] is True

    # Verify it's actually deleted
    assert repo.get(db_session, conv.id) is None


def test_delete_conversation_not_found(client):
    """Test deleting non-existent conversation."""
    response = client.delete("/conversations/9999")

    assert response.status_code == 404


@patch("app.routes.agent")
def test_chat_with_existing_conversation(mock_agent, client, db_session):
    """Test sending a chat message to existing conversation."""
    conv = repo.create(db_session, title="Chat Conv")

    # Mock the agent response
    mock_agent.invoke.return_value.messages = [
        HumanMessage(content="Hello"),
        AIMessage(content="Hi there!")
    ]

    response = client.post("/chat", json={
        "conversation_id": conv.id,
        "message": "Hello"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"] == conv.id
    assert data["user_message"]["content"] == "Hello"
    assert data["assistant_message"]["content"] == "Hi there!"
    assert data["user_message"]["role"] == "user"
    assert data["assistant_message"]["role"] == "assistant"


@patch("app.routes.agent")
def test_chat_creates_conversation_if_null(mock_agent, client):
    """Test that chat creates conversation if conversation_id is null."""
    # Mock the agent response
    mock_agent.invoke.return_value.messages = [
        HumanMessage(content="Test message"),
        AIMessage(content="Test response")
    ]

    response = client.post("/chat", json={
        "conversation_id": None,
        "message": "Test message"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"] is not None
    assert data["user_message"]["content"] == "Test message"
    assert data["assistant_message"]["content"] == "Test response"


def test_chat_empty_message(client, db_session):
    """Test sending an empty message."""
    conv = repo.create(db_session, title="Test")

    response = client.post("/chat", json={
        "conversation_id": conv.id,
        "message": "   "
    })

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_chat_nonexistent_conversation(client):
    """Test chat with non-existent conversation."""
    response = client.post("/chat", json={
        "conversation_id": 9999,
        "message": "Hello"
    })

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@patch("app.routes.agent")
def test_chat_agent_returns_invalid_response(mock_agent, client, db_session):
    """Test handling when agent returns less than 2 messages."""
    conv = repo.create(db_session, title="Test")

    mock_agent.invoke.return_value.messages = [HumanMessage(content="Hello")]

    response = client.post("/chat", json={
        "conversation_id": conv.id,
        "message": "Hello"
    })

    assert response.status_code == 500
    assert "generate response" in response.json()["detail"].lower()


@patch("app.routes.agent")
def test_chat_agent_returns_non_ai_message(mock_agent, client, db_session):
    """Test handling when last message is not AI message."""
    conv = repo.create(db_session, title="Test")

    mock_agent.invoke.return_value.messages = [
        HumanMessage(content="Hello"),
        HumanMessage(content="Another message")
    ]

    response = client.post("/chat", json={
        "conversation_id": conv.id,
        "message": "Hello"
    })

    assert response.status_code == 500
    assert "invalid response type" in response.json()["detail"].lower()
