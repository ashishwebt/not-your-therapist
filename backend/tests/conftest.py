"""Test configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from main import app
from app.repository.database import Base, get_db
from app.repository import conversation as repo


@pytest.fixture
def db_session():
    """Create an in-memory test database session."""
    # Use in-memory SQLite for fast tests
    database_url = "sqlite:///:memory:"

    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)

    session = SessionLocal()
    yield session

    session.close()


@pytest.fixture
def client(db_session):
    """Create a test client with test database."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
