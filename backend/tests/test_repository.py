"""Tests for conversation repository."""
import pytest
from app.repository import conversation as repo
from app.repository.conversation import Conversation


def test_create_conversation(db_session):
    """Test creating a conversation."""
    conv = repo.create(db_session, title="Test Conversation")

    assert conv.id is not None
    assert conv.title == "Test Conversation"
    assert conv.thread_id is not None
    assert conv.created_at is not None
    assert conv.updated_at is not None


def test_create_conversation_default_title(db_session):
    """Test creating a conversation with default title."""
    conv = repo.create(db_session)

    assert conv.title == "New Conversation"


def test_create_conversation_with_thread_id(db_session):
    """Test creating a conversation with specific thread_id."""
    thread_id = "custom-thread-123"
    conv = repo.create(db_session, title="Test", thread_id=thread_id)

    assert conv.thread_id == thread_id


def test_get_conversation(db_session):
    """Test retrieving a conversation by ID."""
    created = repo.create(db_session, title="Retrieve Test")
    retrieved = repo.get(db_session, created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.title == "Retrieve Test"


def test_get_conversation_not_found(db_session):
    """Test retrieving non-existent conversation."""
    result = repo.get(db_session, 9999)

    assert result is None


def test_list_all_conversations(db_session):
    """Test listing all conversations."""
    repo.create(db_session, title="Conv 1")
    repo.create(db_session, title="Conv 2")
    repo.create(db_session, title="Conv 3")

    convs = repo.list_all(db_session)

    assert len(convs) == 3
    assert all(isinstance(c, Conversation) for c in convs)


def test_list_all_empty(db_session):
    """Test listing with no conversations."""
    convs = repo.list_all(db_session)

    assert convs == []


def test_list_all_pagination(db_session):
    """Test pagination in list_all."""
    for i in range(5):
        repo.create(db_session, title=f"Conv {i}")

    convs = repo.list_all(db_session, skip=0, limit=2)

    assert len(convs) == 2


def test_list_all_ordered_by_updated_at(db_session):
    """Test that conversations are ordered by updated_at desc."""
    conv1 = repo.create(db_session, title="Conv 1")
    conv2 = repo.create(db_session, title="Conv 2")
    conv3 = repo.create(db_session, title="Conv 3")

    convs = repo.list_all(db_session)

    # Should be in reverse order (most recent first)
    assert convs[0].id == conv3.id
    assert convs[1].id == conv2.id
    assert convs[2].id == conv1.id


def test_delete_conversation(db_session):
    """Test deleting a conversation."""
    conv = repo.create(db_session, title="To Delete")

    result = repo.delete(db_session, conv.id)

    assert result is True
    assert repo.get(db_session, conv.id) is None


def test_delete_conversation_not_found(db_session):
    """Test deleting non-existent conversation."""
    result = repo.delete(db_session, 9999)

    assert result is False


def test_thread_id_uniqueness(db_session):
    """Test that thread_id is unique."""
    thread_id = "unique-thread"
    repo.create(db_session, thread_id=thread_id)

    with pytest.raises(Exception):  # SQLAlchemy integrity error
        repo.create(db_session, thread_id=thread_id)
        db_session.commit()
