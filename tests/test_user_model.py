import pytest
from models.user import User
from models.database import db


def test_user_has_ministry_field(app):
    """Test that User model has ministry field"""
    user = User(
        email="test@example.com",
        full_name="Test User",
        language="fr",
        role="user"
    )
    # Check that ministry attribute exists
    assert hasattr(user, 'ministry')


def test_user_ministry_nullable(app):
    """Test that ministry field is nullable"""
    user = User(
        email="test@example.com",
        full_name="Test User",
        language="fr",
        role="user",
        ministry=None
    )
    assert user.ministry is None


def test_user_ministry_can_be_set(app):
    """Test that ministry field can be set"""
    user = User(
        email="test@example.com",
        full_name="Test User",
        language="fr",
        role="user",
        ministry="Ministry of Health"
    )
    assert user.ministry == "Ministry of Health"


def test_user_ministry_varchar_255(app):
    """Test that ministry field can store strings up to 255 characters"""
    long_ministry = "A" * 255
    user = User(
        email="test@example.com",
        full_name="Test User",
        language="fr",
        role="user",
        ministry=long_ministry
    )
    assert user.ministry == long_ministry
