"""
DRF Serializers for user-related operations.
"""
from rest_framework import serializers

from .models import User


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

