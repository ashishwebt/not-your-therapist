"""Tests for Pydantic schemas."""
from datetime import datetime
import pytest
from pydantic import ValidationError

from app.schemas import (
    MessageResponse,
    ConversationResponse,
    ConversationListResponse,
    ChatRequest,
    ChatResponse,
    ConversationCreate,
)


class TestMessageResponse:
    """Test MessageResponse schema."""

    def test_valid_message(self):
        """Test creating a valid message response."""
        msg = MessageResponse(
            id=1,
            role="user",
            content="Hello",
            created_at=datetime.now()
        )

        assert msg.id == 1
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_without_created_at(self):
        """Test message without created_at (optional field)."""
        msg = MessageResponse(
            id=1,
            role="assistant",
            content="Hi there"
        )

        assert msg.created_at is None

    def test_invalid_message_missing_required_field(self):
        """Test validation fails with missing required field."""
        with pytest.raises(ValidationError) as exc_info:
            MessageResponse(id=1, role="user")

        assert "content" in str(exc_info.value)


class TestConversationResponse:
    """Test ConversationResponse schema."""

    def test_valid_conversation(self):
        """Test creating a valid conversation response."""
        now = datetime.now()
        conv = ConversationResponse(
            id=1,
            title="Test",
            created_at=now,
            updated_at=now,
            messages=[]
        )

        assert conv.id == 1
        assert conv.title == "Test"
        assert conv.messages == []

    def test_conversation_with_messages(self):
        """Test conversation with multiple messages."""
        now = datetime.now()
        messages = [
            MessageResponse(id=1, role="user", content="Hi"),
            MessageResponse(id=2, role="assistant", content="Hello")
        ]
        conv = ConversationResponse(
            id=1,
            title="Chat",
            created_at=now,
            updated_at=now,
            messages=messages
        )

        assert len(conv.messages) == 2

    def test_conversation_optional_title(self):
        """Test conversation with optional title."""
        now = datetime.now()
        conv = ConversationResponse(
            id=1,
            created_at=now,
            updated_at=now
        )

        assert conv.title is None


class TestConversationListResponse:
    """Test ConversationListResponse schema."""

    def test_valid_list_response(self):
        """Test creating a valid list response."""
        now = datetime.now()
        conv = ConversationListResponse(
            id=1,
            title="Test",
            created_at=now,
            updated_at=now
        )

        assert conv.id == 1
        assert conv.title == "Test"

    def test_list_response_with_message_count(self):
        """Test list response with message count."""
        now = datetime.now()
        conv = ConversationListResponse(
            id=1,
            title="Test",
            created_at=now,
            updated_at=now,
            message_count=5
        )

        assert conv.message_count == 5


class TestChatRequest:
    """Test ChatRequest schema."""

    def test_valid_chat_request(self):
        """Test creating a valid chat request."""
        req = ChatRequest(
            conversation_id=1,
            message="Hello"
        )

        assert req.conversation_id == 1
        assert req.message == "Hello"

    def test_chat_request_with_null_conversation_id(self):
        """Test chat request with null conversation_id."""
        req = ChatRequest(
            conversation_id=None,
            message="Start new conversation"
        )

        assert req.conversation_id is None
        assert req.message == "Start new conversation"

    def test_chat_request_without_conversation_id(self):
        """Test chat request without providing conversation_id."""
        req = ChatRequest(message="Just message")

        assert req.conversation_id is None

    def test_invalid_chat_request_missing_message(self):
        """Test validation fails without message."""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(conversation_id=1)

        assert "message" in str(exc_info.value)

    def test_empty_message_validation(self):
        """Test that empty message is technically valid (route validates)."""
        req = ChatRequest(
            conversation_id=1,
            message=""
        )

        assert req.message == ""


class TestChatResponse:
    """Test ChatResponse schema."""

    def test_valid_chat_response(self):
        """Test creating a valid chat response."""
        resp = ChatResponse(
            conversation_id=1,
            user_message=MessageResponse(
                id=1,
                role="user",
                content="Hi"
            ),
            assistant_message=MessageResponse(
                id=2,
                role="assistant",
                content="Hello"
            )
        )

        assert resp.conversation_id == 1
        assert resp.user_message.content == "Hi"
        assert resp.assistant_message.content == "Hello"

    def test_invalid_chat_response_missing_messages(self):
        """Test validation fails without messages."""
        with pytest.raises(ValidationError) as exc_info:
            ChatResponse(conversation_id=1)

        error_str = str(exc_info.value)
        assert "user_message" in error_str or "assistant_message" in error_str


class TestConversationCreate:
    """Test ConversationCreate schema."""

    def test_valid_create_with_title(self):
        """Test creating conversation with title."""
        conv = ConversationCreate(title="My Chat")

        assert conv.title == "My Chat"

    def test_create_without_title(self):
        """Test creating conversation without title."""
        conv = ConversationCreate()

        assert conv.title is None
