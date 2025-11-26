"""
Tests for user sign up functionality.
"""
import pytest
from django.urls import reverse
from rest_framework import status

from users.models import User


@pytest.mark.django_db
class TestSignUpEndpoint:
    """Tests for the signup API endpoint."""

    def test_signup_success(self, api_client):
        """Test successful user registration."""
        url = reverse('signup')
        data = {
            'email': 'newuser@example.com',
            'password': 'securepassword123',
            'username': 'newuser'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == 'newuser@example.com'
        assert response.data['username'] == 'newuser'
        assert 'id' in response.data
        assert 'date_joined' in response.data
        assert 'password' not in response.data

        # Verify user was created in database
        assert User.objects.filter(email='newuser@example.com').exists()

    def test_signup_without_username(self, api_client):
        """Test registration without optional username."""
        url = reverse('signup')
        data = {
            'email': 'noname@example.com',
            'password': 'securepassword123'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == 'noname@example.com'
        assert response.data['username'] is None

    def test_signup_duplicate_email(self, api_client, create_user):
        """Test registration with an existing email returns 409."""
        create_user(email='existing@example.com')

        url = reverse('signup')
        data = {
            'email': 'existing@example.com',
            'password': 'securepassword123'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_409_CONFLICT
        assert 'error' in response.data

    def test_signup_duplicate_username(self, api_client, create_user):
        """Test registration with an existing username returns 409."""
        create_user(email='user1@example.com', username='existinguser')

        url = reverse('signup')
        data = {
            'email': 'newuser@example.com',
            'password': 'securepassword123',
            'username': 'existinguser'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_409_CONFLICT
        assert 'error' in response.data

    def test_signup_invalid_email(self, api_client):
        """Test registration with invalid email returns 400."""
        url = reverse('signup')
        data = {
            'email': 'invalid-email',
            'password': 'securepassword123'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_signup_weak_password(self, api_client):
        """Test registration with password too short returns 400."""
        url = reverse('signup')
        data = {
            'email': 'test@example.com',
            'password': 'short'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_signup_missing_email(self, api_client):
        """Test registration without email returns 400."""
        url = reverse('signup')
        data = {
            'password': 'securepassword123'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_signup_missing_password(self, api_client):
        """Test registration without password returns 400."""
        url = reverse('signup')
        data = {
            'email': 'test@example.com'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

