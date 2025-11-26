"""
Tests for user login functionality.
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestLoginEndpoint:
    """Tests for the login API endpoint."""

    def test_login_success(self, api_client, create_user):
        """Test successful user login."""
        # Create a user first
        create_user(email='user@example.com', password='securepassword123')

        url = reverse('login')
        data = {
            'email': 'user@example.com',
            'password': 'securepassword123'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        assert response.data['user']['email'] == 'user@example.com'
        assert 'password' not in response.data['user']

    def test_login_invalid_email(self, api_client, create_user):
        """Test login with non-existent email returns 401."""
        create_user(email='user@example.com', password='securepassword123')

        url = reverse('login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'securepassword123'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data

    def test_login_invalid_password(self, api_client, create_user):
        """Test login with incorrect password returns 401."""
        create_user(email='user@example.com', password='securepassword123')

        url = reverse('login')
        data = {
            'email': 'user@example.com',
            'password': 'wrongpassword'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data

    def test_login_missing_email(self, api_client):
        """Test login without email returns 400."""
        url = reverse('login')
        data = {
            'password': 'securepassword123'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data

    def test_login_missing_password(self, api_client):
        """Test login without password returns 400."""
        url = reverse('login')
        data = {
            'email': 'user@example.com'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data

    def test_login_invalid_email_format(self, api_client):
        """Test login with invalid email format returns 400."""
        url = reverse('login')
        data = {
            'email': 'invalid-email',
            'password': 'securepassword123'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data

    def test_login_case_insensitive_email(self, api_client, create_user):
        """Test login with different case email still works."""
        create_user(email='User@Example.com', password='securepassword123')

        url = reverse('login')
        data = {
            'email': 'user@example.com',
            'password': 'securepassword123'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

