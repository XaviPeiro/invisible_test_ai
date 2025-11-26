"""
Business logic layer for user-related operations.
"""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError

User = get_user_model()


class UserServiceError(Exception):
    """Base exception for user service errors."""
    pass


class EmailAlreadyExistsError(UserServiceError):
    """Raised when attempting to register with an existing email."""
    pass


class UsernameAlreadyExistsError(UserServiceError):
    """Raised when attempting to register with an existing username."""
    pass


class InvalidEmailError(UserServiceError):
    """Raised when email format is invalid."""
    pass


class WeakPasswordError(UserServiceError):
    """Raised when password does not meet requirements."""
    pass


class InvalidCredentialsError(UserServiceError):
    """Raised when email or password is incorrect."""
    pass


class UserService:
    """Service class for user-related business logic."""

    MIN_PASSWORD_LENGTH = 8

    def signup(self, email: str, password: str, username: str = None) -> User:
        """
        Register a new user.

        Args:
            email: User's email address (required)
            password: User's password (required)
            username: User's username (optional)

        Returns:
            The created User instance

        Raises:
            InvalidEmailError: If email format is invalid
            WeakPasswordError: If password doesn't meet requirements
            EmailAlreadyExistsError: If email is already registered
            UsernameAlreadyExistsError: If username is already taken
        """
        # Validate email format
        self._validate_email(email)

        # Validate password strength
        self._validate_password(password)

        # Check for existing email
        if self._email_exists(email):
            raise EmailAlreadyExistsError('A user with this email already exists.')

        # Check for existing username if provided
        if username and self._username_exists(username):
            raise UsernameAlreadyExistsError('A user with this username already exists.')

        # Create user
        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                username=username
            )
            return user
        except IntegrityError as e:
            # Handle race condition where user was created between check and create
            if 'email' in str(e).lower():
                raise EmailAlreadyExistsError('A user with this email already exists.')
            if 'username' in str(e).lower():
                raise UsernameAlreadyExistsError('A user with this username already exists.')
            raise

    def _validate_email(self, email: str) -> None:
        """Validate email format."""
        try:
            validate_email(email)
        except ValidationError:
            raise InvalidEmailError('Invalid email format.')

    def _validate_password(self, password: str) -> None:
        """Validate password meets minimum requirements."""
        if not password or len(password) < self.MIN_PASSWORD_LENGTH:
            raise WeakPasswordError(
                f'Password must be at least {self.MIN_PASSWORD_LENGTH} characters long.'
            )

    def _email_exists(self, email: str) -> bool:
        """Check if email is already registered."""
        return User.objects.filter(email__iexact=email).exists()

    def _username_exists(self, username: str) -> bool:
        """Check if username is already taken."""
        return User.objects.filter(username__iexact=username).exists()

    def login(self, email: str, password: str) -> User:
        """
        Authenticate a user with email and password.

        Args:
            email: User's email address
            password: User's password

        Returns:
            The authenticated User instance

        Raises:
            InvalidCredentialsError: If email or password is incorrect
        """
        # Normalize email (case-insensitive lookup)
        normalized_email = User.objects.normalize_email(email)
        
        # Try to get user by email (case-insensitive)
        try:
            user = User.objects.get(email__iexact=normalized_email)
        except User.DoesNotExist:
            raise InvalidCredentialsError('Invalid email or password.')

        # Check password
        if not user.check_password(password):
            raise InvalidCredentialsError('Invalid email or password.')

        if not user.is_active:
            raise InvalidCredentialsError('User account is disabled.')

        return user

