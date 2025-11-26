"""
API views for user-related operations.
"""
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from .serializers import (
    SignUpSerializer,
    LoginSerializer,
    UserSerializer,
    ProfileUpdateSerializer,
    PasswordChangeSerializer,
    LogoutSerializer,
)
from .services import (
    UserService,
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    InvalidEmailError,
    WeakPasswordError,
    InvalidCredentialsError,
    InvalidPasswordError,
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


class ProfileView(APIView):
    """API view for user profile management."""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = UserService()

    def get(self, request):
        """
        Retrieve current user's profile.

        Returns:
            200: User profile data
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """
        Update current user's profile.

        Request body:
            - email (optional): New email address
            - username (optional): New username

        Returns:
            200: Profile updated successfully
            400: Validation error
            409: Email or username already exists
        """
        serializer = ProfileUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = self.user_service.update_profile(
                user=request.user,
                email=serializer.validated_data.get('email'),
                username=serializer.validated_data.get('username')
            )

            response_serializer = UserSerializer(user)
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )

        except InvalidEmailError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except (EmailAlreadyExistsError, UsernameAlreadyExistsError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_409_CONFLICT
            )

    def patch(self, request):
        """Partial update - same as PUT."""
        return self.put(request)


class PasswordChangeView(APIView):
    """API view for changing user password."""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_service = UserService()

    def post(self, request):
        """
        Change user password.

        Request body:
            - old_password (required): Current password
            - new_password (required): New password (min 8 characters)

        Returns:
            200: Password changed successfully
            400: Validation error or weak password
            401: Invalid old password
        """
        serializer = PasswordChangeSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            self.user_service.change_password(
                user=request.user,
                old_password=serializer.validated_data['old_password'],
                new_password=serializer.validated_data['new_password']
            )

            return Response(
                {'message': 'Password changed successfully.'},
                status=status.HTTP_200_OK
            )

        except InvalidPasswordError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )

        except WeakPasswordError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    """API view for user logout."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Logout user by blacklisting both access and refresh tokens.

        Request body:
            - refresh (required): Refresh token to blacklist

        Returns:
            200: Logout successful
            400: Validation error
        """
        serializer = LogoutSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Blacklist refresh token (this also blacklists the associated access token)
            refresh_token = RefreshToken(serializer.validated_data['refresh'])
            refresh_token.blacklist()
            
            # Also blacklist the current access token if provided
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                access_token_str = auth_header.split(' ')[1]
                try:
                    # Decode access token to get jti
                    from rest_framework_simplejwt.tokens import UntypedToken
                    from rest_framework_simplejwt.exceptions import TokenError
                    from django.utils import timezone
                    from datetime import timedelta
                    
                    untyped_token = UntypedToken(access_token_str)
                    jti = untyped_token.get('jti')
                    exp = untyped_token.get('exp')
                    
                    if jti:
                        # Create or get OutstandingToken for access token and blacklist it
                        outstanding_token, created = OutstandingToken.objects.get_or_create(
                            jti=jti,
                            defaults={
                                'user': request.user,
                                'token': access_token_str,
                                'created_at': timezone.now(),
                                'expires_at': timezone.now() + timedelta(seconds=exp - int(timezone.now().timestamp())) if exp else None,
                            }
                        )
                        BlacklistedToken.objects.get_or_create(token=outstanding_token)
                except (TokenError, KeyError, Exception):
                    # Token might not have jti or is invalid, continue anyway
                    pass
                except Exception:
                    # If access token blacklisting fails, continue anyway
                    pass
            
            return Response(
                {'message': 'Successfully logged out.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'Invalid refresh token.'},
                status=status.HTTP_400_BAD_REQUEST
            )

