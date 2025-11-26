"""
Pytest configuration and fixtures.
"""
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Return an API client for making requests."""
    return APIClient()


@pytest.fixture
def create_user(db):
    """Factory fixture to create users."""
    from users.models import User

    def _create_user(email='test@example.com', password='testpass123', username=None):
        return User.objects.create_user(
            email=email,
            password=password,
            username=username
        )
    return _create_user

