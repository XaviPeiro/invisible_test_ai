"""
Tests for group management functionality.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User, Group


@pytest.fixture
def authenticated_client(api_client, create_user):
    """Return an authenticated API client."""
    user = create_user(email='auth@example.com', password='testpass123')
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def another_user(create_user):
    """Create another user for testing."""
    return create_user(email='other@example.com', password='testpass123')


@pytest.mark.django_db
class TestGroupListView:
    """Tests for the group list/create API endpoint."""

    def test_create_group_success(self, authenticated_client, create_user):
        """Test successful group creation."""
        url = reverse('group-list')
        data = {
            'name': 'Test Group',
            'description': 'A test group'
        }

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Test Group'
        assert response.data['description'] == 'A test group'
        assert 'id' in response.data
        assert 'created_by' in response.data
        assert response.data['member_count'] == 1  # Creator is automatically added

        # Verify group was created
        assert Group.objects.filter(name='Test Group').exists()

    def test_create_group_without_description(self, authenticated_client):
        """Test creating group without description."""
        url = reverse('group-list')
        data = {'name': 'Simple Group'}

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Simple Group'
        assert response.data['description'] is None

    def test_create_group_missing_name(self, authenticated_client):
        """Test creating group without name returns 400."""
        url = reverse('group-list')
        data = {'description': 'No name group'}

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data

    def test_create_group_empty_name(self, authenticated_client):
        """Test creating group with empty name returns 400."""
        url = reverse('group-list')
        data = {'name': ''}

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_user_groups(self, authenticated_client, create_user):
        """Test getting user's groups."""
        user = create_user(email='groupuser@example.com', password='testpass123')
        refresh = RefreshToken.for_user(user)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create a group
        url = reverse('group-list')
        data = {'name': 'My Group'}
        authenticated_client.post(url, data, format='json')

        # Get user's groups
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'My Group'

    def test_get_user_groups_empty(self, authenticated_client):
        """Test getting groups when user has none."""
        url = reverse('group-list')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_create_group_unauthorized(self, api_client):
        """Test creating group without authentication returns 401."""
        url = reverse('group-list')
        data = {'name': 'Unauthorized Group'}

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestGroupDetailView:
    """Tests for the group detail API endpoint."""

    def test_get_group_details(self, authenticated_client, create_user):
        """Test getting group details."""
        user = create_user(email='detailuser@example.com', password='testpass123')
        refresh = RefreshToken.for_user(user)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create a group
        create_url = reverse('group-list')
        create_data = {'name': 'Detail Group', 'description': 'Group for details'}
        create_response = authenticated_client.post(create_url, create_data, format='json')
        group_id = create_response.data['id']

        # Get group details
        url = reverse('group-detail', kwargs={'group_id': group_id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Detail Group'
        assert response.data['description'] == 'Group for details'

    def test_get_group_not_found(self, authenticated_client):
        """Test getting non-existent group returns 404."""
        import uuid
        url = reverse('group-detail', kwargs={'group_id': uuid.uuid4()})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_group_not_member(self, authenticated_client, create_user, another_user):
        """Test getting group when not a member returns 403."""
        # Create group with another user
        refresh = RefreshToken.for_user(another_user)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        create_url = reverse('group-list')
        create_data = {'name': 'Other Group'}
        create_response = authenticated_client.post(create_url, create_data, format='json')
        group_id = create_response.data['id']

        # Try to access with different user
        user = create_user(email='outsider@example.com', password='testpass123')
        refresh = RefreshToken.for_user(user)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = reverse('group-detail', kwargs={'group_id': group_id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_group_success(self, authenticated_client, create_user):
        """Test successful group deletion by creator."""
        user = create_user(email='deleteuser@example.com', password='testpass123')
        refresh = RefreshToken.for_user(user)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create a group
        create_url = reverse('group-list')
        create_data = {'name': 'To Delete'}
        create_response = authenticated_client.post(create_url, create_data, format='json')
        group_id = create_response.data['id']

        # Delete group
        url = reverse('group-detail', kwargs={'group_id': group_id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Group.objects.filter(id=group_id).exists()


@pytest.mark.django_db
class TestGroupMembersView:
    """Tests for the group members API endpoint."""

    def test_get_group_members(self, authenticated_client, create_user, another_user):
        """Test getting group members."""
        user = create_user(email='memberuser@example.com', password='testpass123')
        refresh = RefreshToken.for_user(user)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create a group
        create_url = reverse('group-list')
        create_data = {'name': 'Members Group'}
        create_response = authenticated_client.post(create_url, create_data, format='json')
        group_id = create_response.data['id']

        # Add a member
        members_url = reverse('group-members', kwargs={'group_id': group_id})
        add_data = {'user_id': str(another_user.id)}
        authenticated_client.post(members_url, add_data, format='json')

        # Get members
        response = authenticated_client.get(members_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # Creator + added member

    def test_add_member_success(self, authenticated_client, create_user, another_user):
        """Test successfully adding a member to group."""
        user = create_user(email='addmember@example.com', password='testpass123')
        refresh = RefreshToken.for_user(user)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create a group
        create_url = reverse('group-list')
        create_data = {'name': 'Add Member Group'}
        create_response = authenticated_client.post(create_url, create_data, format='json')
        group_id = create_response.data['id']

        # Add member
        url = reverse('group-members', kwargs={'group_id': group_id})
        data = {'user_id': str(another_user.id)}
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert response.data['user']['id'] == str(another_user.id)

        # Verify member was added
        group = Group.objects.get(id=group_id)
        assert another_user in group.members.all()

    def test_add_member_duplicate(self, authenticated_client, create_user, another_user):
        """Test adding duplicate member returns 409."""
        user = create_user(email='duplicate@example.com', password='testpass123')
        refresh = RefreshToken.for_user(user)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create a group
        create_url = reverse('group-list')
        create_data = {'name': 'Duplicate Group'}
        create_response = authenticated_client.post(create_url, create_data, format='json')
        group_id = create_response.data['id']

        # Add member first time
        url = reverse('group-members', kwargs={'group_id': group_id})
        data = {'user_id': str(another_user.id)}
        authenticated_client.post(url, data, format='json')

        # Try to add again
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_409_CONFLICT
        assert 'error' in response.data

    def test_add_member_user_not_found(self, authenticated_client, create_user):
        """Test adding non-existent user returns 404."""
        user = create_user(email='notfound@example.com', password='testpass123')
        refresh = RefreshToken.for_user(user)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create a group
        create_url = reverse('group-list')
        create_data = {'name': 'Not Found Group'}
        create_response = authenticated_client.post(create_url, create_data, format='json')
        group_id = create_response.data['id']

        # Try to add non-existent user
        import uuid
        url = reverse('group-members', kwargs={'group_id': group_id})
        data = {'user_id': str(uuid.uuid4())}
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_member_not_group_member(self, authenticated_client, create_user, another_user):
        """Test adding member when requester is not a group member returns 403."""
        # Create group with another user
        refresh = RefreshToken.for_user(another_user)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        create_url = reverse('group-list')
        create_data = {'name': 'Restricted Group'}
        create_response = authenticated_client.post(create_url, create_data, format='json')
        group_id = create_response.data['id']

        # Try to add member with different user (not a member)
        user = create_user(email='outsider2@example.com', password='testpass123')
        refresh = RefreshToken.for_user(user)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = reverse('group-members', kwargs={'group_id': group_id})
        data = {'user_id': str(another_user.id)}
        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

