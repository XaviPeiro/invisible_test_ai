"""
Tests for user profile management functionality.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


@pytest.fixture
def authenticated_client(api_client, create_user):
    """Return an authenticated API client."""
    user = create_user(email='auth@example.com', password='testpass123')
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.mark.django_db
class TestProfileView:
    """Tests for the profile API endpoint."""

    def test_get_profile_success(self, authenticated_client):
        """Test retrieving own profile."""
        url = reverse('profile')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'auth@example.com'
        assert 'id' in response.data
        assert 'date_joined' in response.data
        assert 'password' not in response.data

    def test_get_profile_unauthorized(self, api_client):
        """Test retrieving profile without authentication returns 401."""
        url = reverse('profile')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile_email(self, authenticated_client, create_user):
        """Test updating profile email."""
        url = reverse('profile')
        data = {'email': 'newemail@example.com'}

        response = authenticated_client.put(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'newemail@example.com'
        assert User.objects.get(id=response.data['id']).email == 'newemail@example.com'

    def test_update_profile_username(self, authenticated_client):
        """Test updating profile username."""
        url = reverse('profile')
        data = {'username': 'newusername'}

        response = authenticated_client.put(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'newusername'

    def test_update_profile_both_fields(self, authenticated_client):
        """Test updating both email and username."""
        url = reverse('profile')
        data = {
            'email': 'updated@example.com',
            'username': 'updateduser'
        }

        response = authenticated_client.put(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'updated@example.com'
        assert response.data['username'] == 'updateduser'

    def test_update_profile_duplicate_email(self, authenticated_client, create_user):
        """Test updating profile with existing email returns 409."""
        create_user(email='existing@example.com')

        url = reverse('profile')
        data = {'email': 'existing@example.com'}

        response = authenticated_client.put(url, data, format='json')

        assert response.status_code == status.HTTP_409_CONFLICT
        assert 'error' in response.data

    def test_update_profile_duplicate_username(self, authenticated_client, create_user):
        """Test updating profile with existing username returns 409."""
        create_user(email='other@example.com', username='existinguser')

        url = reverse('profile')
        data = {'username': 'existinguser'}

        response = authenticated_client.put(url, data, format='json')

        assert response.status_code == status.HTTP_409_CONFLICT
        assert 'error' in response.data

    def test_update_profile_invalid_email(self, authenticated_client):
        """Test updating profile with invalid email returns 400."""
        url = reverse('profile')
        data = {'email': 'invalid-email'}

        response = authenticated_client.put(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_profile_patch_method(self, authenticated_client):
        """Test PATCH method works same as PUT."""
        url = reverse('profile')
        data = {'username': 'patcheduser'}

        response = authenticated_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'patcheduser'

    def test_update_profile_same_email(self, authenticated_client):
        """Test updating profile with same email should succeed."""
        # Get current user email
        get_response = authenticated_client.get(reverse('profile'))
        current_email = get_response.data['email']

        url = reverse('profile')
        data = {'email': current_email}

        response = authenticated_client.put(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == current_email


@pytest.mark.django_db
class TestPasswordChangeView:
    """Tests for the password change API endpoint."""

    def test_change_password_success(self, authenticated_client, create_user):
        """Test successful password change."""
        user = create_user(email='changepass@example.com', password='oldpass123')
        refresh = RefreshToken.for_user(user)
        client = authenticated_client
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = reverse('change-password')
        data = {
            'old_password': 'oldpass123',
            'new_password': 'newpass123'
        }

        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data

        # Verify password was changed
        user.refresh_from_db()
        assert user.check_password('newpass123')

    def test_change_password_wrong_old_password(self, authenticated_client, create_user):
        """Test changing password with wrong old password returns 401."""
        user = create_user(email='wrongpass@example.com', password='correctpass123')
        refresh = RefreshToken.for_user(user)
        client = authenticated_client
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = reverse('change-password')
        data = {
            'old_password': 'wrongpass',
            'new_password': 'newpass123'
        }

        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data

    def test_change_password_weak_new_password(self, authenticated_client, create_user):
        """Test changing password with weak new password returns 400."""
        user = create_user(email='weakpass@example.com', password='oldpass123')
        refresh = RefreshToken.for_user(user)
        client = authenticated_client
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = reverse('change-password')
        data = {
            'old_password': 'oldpass123',
            'new_password': 'short'
        }

        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data or 'error' in response.data

    def test_change_password_missing_fields(self, authenticated_client):
        """Test changing password with missing fields returns 400."""
        url = reverse('change-password')
        data = {'old_password': 'oldpass123'}

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data

    def test_change_password_unauthorized(self, api_client):
        """Test changing password without authentication returns 401."""
        url = reverse('change-password')
        data = {
            'old_password': 'oldpass123',
            'new_password': 'newpass123'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

