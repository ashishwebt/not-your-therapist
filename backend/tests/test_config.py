import pytest
from pydantic import ValidationError


def test_settings_require_database_url():
    """Settings should fail fast when DATABASE_URL is missing."""
    from app.config import Settings

    with pytest.raises(ValidationError):
        Settings(_env_file=None, DATABASE_URL=None)
