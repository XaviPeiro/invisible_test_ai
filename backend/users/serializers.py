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

