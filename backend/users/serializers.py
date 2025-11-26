"""
DRF Serializers for user-related operations.
"""
from rest_framework import serializers

from .models import User, Group, GroupMembership, Expense


class SignUpSerializer(serializers.Serializer):
    """Serializer for user sign up requests."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    username = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=150
    )


class LoginSerializer(serializers.Serializer):
    """Serializer for user login requests."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user responses."""

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class ProfileUpdateSerializer(serializers.Serializer):
    """Serializer for updating user profile."""

    email = serializers.EmailField(required=False)
    username = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=150
    )


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing user password."""

    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout requests."""

    refresh = serializers.CharField(required=True)


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for group responses."""

    created_by = UserSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'created_by', 'member_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_member_count(self, obj):
        """Get the number of members in the group."""
        return obj.members.count()


class GroupCreateSerializer(serializers.Serializer):
    """Serializer for creating groups."""

    name = serializers.CharField(required=True, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class AddMemberSerializer(serializers.Serializer):
    """Serializer for adding members to groups."""

    user_id = serializers.UUIDField(required=True)


class GroupMemberSerializer(serializers.ModelSerializer):
    """Serializer for group member responses."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = GroupMembership
        fields = ['user', 'joined_at']
        read_only_fields = ['user', 'joined_at']


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for expense responses."""

    paid_by = UserSerializer(read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'group', 'paid_by', 'amount', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExpenseCreateSerializer(serializers.Serializer):
    """Serializer for creating expenses."""

    amount = serializers.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=2,
        min_value=0.01
    )
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    paid_by = serializers.UUIDField(required=True)


class BalanceSummarySerializer(serializers.Serializer):
    """Serializer for balance summary responses."""

    user = UserSerializer(read_only=True)
    total_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_owed = serializers.DecimalField(max_digits=10, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=10, decimal_places=2)

