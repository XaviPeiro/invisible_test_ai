"""
API views for user-related operations.
"""
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import SignUpSerializer, LoginSerializer, UserSerializer
from .services import (
    UserService,
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    InvalidEmailError,
    WeakPasswordError,
    InvalidCredentialsError,
)


class SignUpView(APIView):
    """API view for user registration."""

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = UserService()

    def post(self, request):
        """
        Register a new user.

        Request body:
            - email (required): User's email address
            - password (required): User's password (min 8 characters)
            - username (optional): User's username

        Returns:
            201: User created successfully
            400: Validation error
            409: Email or username already exists
        """
        serializer = SignUpSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = self.user_service.signup(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                username=serializer.validated_data.get('username')
            )

            response_serializer = UserSerializer(user)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        except (InvalidEmailError, WeakPasswordError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except (EmailAlreadyExistsError, UsernameAlreadyExistsError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_409_CONFLICT
            )


class LoginView(APIView):
    """API view for user authentication."""

    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = UserService()

    def post(self, request):
        """
        Authenticate a user and return JWT tokens.

        Request body:
            - email (required): User's email address
            - password (required): User's password

        Returns:
            200: Authentication successful, returns access and refresh tokens
            400: Validation error
            401: Invalid credentials
        """
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = self.user_service.login(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response(
                {
                    'access': access_token,
                    'refresh': refresh_token,
                    'user': UserSerializer(user).data
                },
                status=status.HTTP_200_OK
            )

        except InvalidCredentialsError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )

