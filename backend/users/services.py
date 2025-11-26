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


class InvalidPasswordError(UserServiceError):
    """Raised when old password is incorrect."""
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

    def update_profile(self, user: User, email: str = None, username: str = None) -> User:
        """
        Update user profile information.

        Args:
            user: The User instance to update
            email: New email address (optional)
            username: New username (optional)

        Returns:
            The updated User instance

        Raises:
            InvalidEmailError: If email format is invalid
            EmailAlreadyExistsError: If email is already registered by another user
            UsernameAlreadyExistsError: If username is already taken by another user
        """
        # Validate email if provided
        if email is not None:
            self._validate_email(email)
            # Check if email is already taken by another user
            if self._email_exists(email) and user.email.lower() != email.lower():
                raise EmailAlreadyExistsError('A user with this email already exists.')
            user.email = email

        # Check username if provided
        if username is not None:
            # Check if username is already taken by another user
            if username and self._username_exists(username):
                existing_user = User.objects.filter(username__iexact=username).first()
                if existing_user and existing_user.id != user.id:
                    raise UsernameAlreadyExistsError('A user with this username already exists.')
            user.username = username

        user.save()
        return user

    def change_password(self, user: User, old_password: str, new_password: str) -> None:
        """
        Change user password.

        Args:
            user: The User instance
            old_password: Current password
            new_password: New password

        Raises:
            InvalidPasswordError: If old password is incorrect
            WeakPasswordError: If new password doesn't meet requirements
        """
        # Verify old password
        if not user.check_password(old_password):
            raise InvalidPasswordError('Current password is incorrect.')

        # Validate new password
        self._validate_password(new_password)

        # Set new password
        user.set_password(new_password)
        user.save()


class GroupServiceError(UserServiceError):
    """Base exception for group service errors."""
    pass


class GroupNotFoundError(GroupServiceError):
    """Raised when group is not found."""
    pass


class UserNotFoundError(GroupServiceError):
    """Raised when user is not found."""
    pass


class UserAlreadyMemberError(GroupServiceError):
    """Raised when user is already a member of the group."""
    pass


class GroupService:
    """Service class for group-related business logic."""

    def create_group(self, name: str, created_by: User, description: str = None):
        """
        Create a new group.

        Args:
            name: Group name (required)
            created_by: User creating the group (required)
            description: Group description (optional)

        Returns:
            The created Group instance

        Raises:
            ValueError: If name is empty
        """
        from .models import Group

        if not name or not name.strip():
            raise ValueError('Group name is required.')

        group = Group.objects.create(
            name=name.strip(),
            description=description.strip() if description else None,
            created_by=created_by
        )
        # Add creator as a member
        group.members.add(created_by)
        return group

    def add_member(self, group_id: str, user_id: str):
        """
        Add a user to a group.

        Args:
            group_id: UUID of the group
            user_id: UUID of the user to add

        Returns:
            The GroupMembership instance

        Raises:
            GroupNotFoundError: If group doesn't exist
            UserNotFoundError: If user doesn't exist
            UserAlreadyMemberError: If user is already a member
        """
        from .models import Group, GroupMembership

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise GroupNotFoundError('Group not found.')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise UserNotFoundError('User not found.')

        # Check if user is already a member
        if GroupMembership.objects.filter(group=group, user=user).exists():
            raise UserAlreadyMemberError('User is already a member of this group.')

        membership = GroupMembership.objects.create(group=group, user=user)
        return membership

    def get_user_groups(self, user: User):
        """
        Get all groups for a user.

        Args:
            user: User instance

        Returns:
            QuerySet of Group instances
        """
        from .models import Group

        return Group.objects.filter(members=user).distinct()

    def get_group_members(self, group_id: str):
        """
        Get all members of a group.

        Args:
            group_id: UUID of the group

        Returns:
            QuerySet of User instances

        Raises:
            GroupNotFoundError: If group doesn't exist
        """
        from .models import Group

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise GroupNotFoundError('Group not found.')

        return group.members.all()

    def get_group(self, group_id: str):
        """
        Get a group by ID.

        Args:
            group_id: UUID of the group

        Returns:
            Group instance

        Raises:
            GroupNotFoundError: If group doesn't exist
        """
        from .models import Group

        try:
            return Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise GroupNotFoundError('Group not found.')

    def delete_group(self, group_id: str, user: User):
        """
        Delete a group (only if user is the creator).

        Args:
            group_id: UUID of the group
            user: User attempting to delete

        Raises:
            GroupNotFoundError: If group doesn't exist
            PermissionError: If user is not the creator
        """
        from .models import Group

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise GroupNotFoundError('Group not found.')

        if group.created_by != user:
            raise PermissionError('Only the group creator can delete the group.')

        group.delete()

