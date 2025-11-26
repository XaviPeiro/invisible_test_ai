"""
Tests for expense management functionality.
"""
import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User, Group, Expense


@pytest.fixture
def authenticated_client(api_client, create_user):
    """Return an authenticated API client."""
    user = create_user(email='auth@example.com', password='testpass123')
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def group_with_members(create_user):
    """Create a group with multiple members."""
    creator = create_user(email='creator@example.com', password='testpass123')
    member1 = create_user(email='member1@example.com', password='testpass123')
    member2 = create_user(email='member2@example.com', password='testpass123')

    group = Group.objects.create(name='Test Group', created_by=creator)
    group.members.add(creator, member1, member2)
    return group, creator, member1, member2


@pytest.mark.django_db
class TestExpenseListView:
    """Tests for the expense list/create API endpoint."""

    def test_create_expense_success(self, authenticated_client, group_with_members):
        """Test successful expense creation."""
        group, creator, member1, member2 = group_with_members
        refresh = RefreshToken.for_user(creator)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = reverse('expense-list', kwargs={'group_id': group.id})
        data = {
            'amount': '100.00',
            'paid_by': str(creator.id),
            'description': 'Dinner expense'
        }

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['amount'] == '100.00'
        assert response.data['description'] == 'Dinner expense'
        assert response.data['paid_by']['id'] == str(creator.id)
        assert 'id' in response.data

        # Verify expense was created
        assert Expense.objects.filter(group=group, paid_by=creator).exists()

    def test_create_expense_without_description(self, authenticated_client, group_with_members):
        """Test creating expense without description."""
        group, creator, member1, member2 = group_with_members
        refresh = RefreshToken.for_user(creator)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = reverse('expense-list', kwargs={'group_id': group.id})
        data = {
            'amount': '50.00',
            'paid_by': str(creator.id)
        }

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['amount'] == '50.00'
        assert response.data['description'] is None

    def test_create_expense_missing_amount(self, authenticated_client, group_with_members):
        """Test creating expense without amount returns 400."""
        group, creator, member1, member2 = group_with_members
        refresh = RefreshToken.for_user(creator)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = reverse('expense-list', kwargs={'group_id': group.id})
        data = {'paid_by': str(creator.id)}

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data

    def test_create_expense_invalid_amount(self, authenticated_client, group_with_members):
        """Test creating expense with invalid amount returns 400."""
        group, creator, member1, member2 = group_with_members
        refresh = RefreshToken.for_user(creator)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = reverse('expense-list', kwargs={'group_id': group.id})
        data = {
            'amount': '0.00',
            'paid_by': str(creator.id)
        }

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_expense_non_member_payer(self, authenticated_client, group_with_members, create_user):
        """Test creating expense with non-member payer returns 400."""
        group, creator, member1, member2 = group_with_members
        non_member = create_user(email='nonmember@example.com', password='testpass123')
        refresh = RefreshToken.for_user(creator)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = reverse('expense-list', kwargs={'group_id': group.id})
        data = {
            'amount': '100.00',
            'paid_by': str(non_member.id)
        }

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_create_expense_not_group_member(self, authenticated_client, group_with_members, create_user):
        """Test creating expense when requester is not a group member returns 403."""
        group, creator, member1, member2 = group_with_members
        outsider = create_user(email='outsider@example.com', password='testpass123')
        refresh = RefreshToken.for_user(outsider)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = reverse('expense-list', kwargs={'group_id': group.id})
        data = {
            'amount': '100.00',
            'paid_by': str(creator.id)
        }

        response = authenticated_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_expenses(self, authenticated_client, group_with_members):
        """Test getting expense history."""
        group, creator, member1, member2 = group_with_members
        refresh = RefreshToken.for_user(creator)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create some expenses
        Expense.objects.create(group=group, paid_by=creator, amount=Decimal('100.00'), description='Expense 1')
        Expense.objects.create(group=group, paid_by=member1, amount=Decimal('50.00'), description='Expense 2')

        url = reverse('expense-list', kwargs={'group_id': group.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert response.data[0]['amount'] == '50.00'  # Most recent first
        assert response.data[1]['amount'] == '100.00'

    def test_get_expenses_empty(self, authenticated_client, group_with_members):
        """Test getting expenses when group has none."""
        group, creator, member1, member2 = group_with_members
        refresh = RefreshToken.for_user(creator)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = reverse('expense-list', kwargs={'group_id': group.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_get_expenses_not_group_member(self, authenticated_client, group_with_members, create_user):
        """Test getting expenses when not a group member returns 403."""
        group, creator, member1, member2 = group_with_members
        outsider = create_user(email='outsider2@example.com', password='testpass123')
        refresh = RefreshToken.for_user(outsider)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = reverse('expense-list', kwargs={'group_id': group.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestExpenseBalanceView:
    """Tests for the expense balance summary API endpoint."""

    def test_get_balance_summary(self, authenticated_client, group_with_members):
        """Test getting balance summary."""
        group, creator, member1, member2 = group_with_members
        refresh = RefreshToken.for_user(creator)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create expenses
        # Creator pays $100, Member1 pays $50
        # Total: $150, equal share per person: $50
        Expense.objects.create(group=group, paid_by=creator, amount=Decimal('100.00'))
        Expense.objects.create(group=group, paid_by=member1, amount=Decimal('50.00'))

        url = reverse('expense-balance', kwargs={'group_id': group.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3  # 3 members

        # Find creator's balance
        creator_balance = next(b for b in response.data if b['user']['id'] == str(creator.id))
        assert creator_balance['total_paid'] == '100.00'
        assert creator_balance['total_owed'] == '50.00'  # Equal share
        assert creator_balance['net_balance'] == '50.00'  # Paid 100, owes 50, net +50

        # Find member1's balance
        member1_balance = next(b for b in response.data if b['user']['id'] == str(member1.id))
        assert member1_balance['total_paid'] == '50.00'
        assert member1_balance['total_owed'] == '50.00'  # Equal share
        assert member1_balance['net_balance'] == '0.00'  # Paid 50, owes 50, net 0

        # Find member2's balance
        member2_balance = next(b for b in response.data if b['user']['id'] == str(member2.id))
        assert member2_balance['total_paid'] == '0.00'
        assert member2_balance['total_owed'] == '50.00'  # Equal share
        assert member2_balance['net_balance'] == '-50.00'  # Paid 0, owes 50, net -50

    def test_get_balance_summary_empty_group(self, authenticated_client, group_with_members):
        """Test getting balance summary when group has no expenses."""
        group, creator, member1, member2 = group_with_members
        refresh = RefreshToken.for_user(creator)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = reverse('expense-balance', kwargs={'group_id': group.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3  # 3 members

        # All balances should be zero
        for balance in response.data:
            assert balance['total_paid'] == '0.00'
            assert balance['total_owed'] == '0.00'
            assert balance['net_balance'] == '0.00'

    def test_get_balance_summary_not_group_member(self, authenticated_client, group_with_members, create_user):
        """Test getting balance summary when not a group member returns 403."""
        group, creator, member1, member2 = group_with_members
        outsider = create_user(email='outsider3@example.com', password='testpass123')
        refresh = RefreshToken.for_user(outsider)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        url = reverse('expense-balance', kwargs={'group_id': group.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_balance_summary_equal_shares(self, authenticated_client, group_with_members):
        """Test balance calculation with equal shares."""
        group, creator, member1, member2 = group_with_members
        refresh = RefreshToken.for_user(creator)
        authenticated_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create expense: $90 total, 3 members, each owes $30
        Expense.objects.create(group=group, paid_by=creator, amount=Decimal('90.00'))

        url = reverse('expense-balance', kwargs={'group_id': group.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Creator paid $90, owes $30, net +$60
        creator_balance = next(b for b in response.data if b['user']['id'] == str(creator.id))
        assert creator_balance['total_paid'] == '90.00'
        assert creator_balance['total_owed'] == '30.00'
        assert creator_balance['net_balance'] == '60.00'

        # Other members owe $30 each
        for member in [member1, member2]:
            member_balance = next(b for b in response.data if b['user']['id'] == str(member.id))
            assert member_balance['total_paid'] == '0.00'
            assert member_balance['total_owed'] == '30.00'
            assert member_balance['net_balance'] == '-30.00'

