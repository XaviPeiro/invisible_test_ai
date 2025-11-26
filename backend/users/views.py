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
    GroupSerializer,
    GroupCreateSerializer,
    AddMemberSerializer,
    GroupMemberSerializer,
    ExpenseSerializer,
    ExpenseCreateSerializer,
    BalanceSummarySerializer,
)
from .services import (
    UserService,
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    InvalidEmailError,
    WeakPasswordError,
    InvalidCredentialsError,
    InvalidPasswordError,
    GroupService,
    GroupNotFoundError,
    UserNotFoundError,
    UserAlreadyMemberError,
    ExpenseService,
    ExpenseNotFoundError,
    InvalidPayerError,
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


class GroupListView(APIView):
    """API view for listing and creating groups."""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.group_service = GroupService()

    def get(self, request):
        """
        Get all groups for the current user.

        Returns:
            200: List of user's groups
        """
        groups = self.group_service.get_user_groups(request.user)
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new group.

        Request body:
            - name (required): Group name
            - description (optional): Group description

        Returns:
            201: Group created successfully
            400: Validation error
        """
        serializer = GroupCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            group = self.group_service.create_group(
                name=serializer.validated_data['name'],
                created_by=request.user,
                description=serializer.validated_data.get('description')
            )

            response_serializer = GroupSerializer(group)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class GroupDetailView(APIView):
    """API view for group details and deletion."""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.group_service = GroupService()

    def get(self, request, group_id):
        """
        Get group details.

        Returns:
            200: Group details
            404: Group not found
        """
        try:
            group = self.group_service.get_group(group_id)
            # Check if user is a member
            if request.user not in group.members.all():
                return Response(
                    {'error': 'You are not a member of this group.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = GroupSerializer(group)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except GroupNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, group_id):
        """
        Delete a group (only creator can delete).

        Returns:
            204: Group deleted successfully
            404: Group not found
            403: Permission denied
        """
        try:
            self.group_service.delete_group(group_id, request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except GroupNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


class GroupMembersView(APIView):
    """API view for managing group members."""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.group_service = GroupService()

    def get(self, request, group_id):
        """
        Get all members of a group.

        Returns:
            200: List of group members
            404: Group not found
            403: User is not a member
        """
        try:
            group = self.group_service.get_group(group_id)
            # Check if user is a member
            if request.user not in group.members.all():
                return Response(
                    {'error': 'You are not a member of this group.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            members = self.group_service.get_group_members(group_id)
            # Use GroupMembership to get joined_at
            from .models import GroupMembership
            memberships = GroupMembership.objects.filter(group=group).select_related('user')
            serializer = GroupMemberSerializer(memberships, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except GroupNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, group_id):
        """
        Add a member to a group.

        Request body:
            - user_id (required): UUID of user to add

        Returns:
            201: Member added successfully
            400: Validation error
            404: Group or user not found
            409: User already a member
            403: User is not a member of the group
        """
        serializer = AddMemberSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Check if requester is a member of the group
            group = self.group_service.get_group(group_id)
            if request.user not in group.members.all():
                return Response(
                    {'error': 'You must be a member of the group to add members.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            membership = self.group_service.add_member(
                group_id=group_id,
                user_id=str(serializer.validated_data['user_id'])
            )

            response_serializer = GroupMemberSerializer(membership)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        except GroupNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except UserNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except UserAlreadyMemberError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_409_CONFLICT
            )


class ExpenseListView(APIView):
    """API view for listing and creating expenses."""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expense_service = ExpenseService()
        self.group_service = GroupService()

    def get(self, request, group_id):
        """
        Get all expenses for a group.

        Returns:
            200: List of expenses
            404: Group not found
            403: User is not a member
        """
        try:
            # Check if user is a member of the group
            group = self.group_service.get_group(group_id)
            if request.user not in group.members.all():
                return Response(
                    {'error': 'You must be a member of the group to view expenses.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            expenses = self.expense_service.get_group_expenses(group_id)
            serializer = ExpenseSerializer(expenses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except GroupNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, group_id):
        """
        Create a new expense for a group.

        Request body:
            - amount (required): Expense amount
            - paid_by (required): UUID of user who paid
            - description (optional): Expense description

        Returns:
            201: Expense created successfully
            400: Validation error
            404: Group or user not found
            403: User is not a member or payer is not a member
        """
        serializer = ExpenseCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Check if user is a member of the group
            group = self.group_service.get_group(group_id)
            if request.user not in group.members.all():
                return Response(
                    {'error': 'You must be a member of the group to add expenses.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            expense = self.expense_service.create_expense(
                group_id=group_id,
                amount=serializer.validated_data['amount'],
                paid_by_id=str(serializer.validated_data['paid_by']),
                description=serializer.validated_data.get('description')
            )

            response_serializer = ExpenseSerializer(expense)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        except GroupNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except UserNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except InvalidPayerError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ExpenseBalanceView(APIView):
    """API view for getting balance summary."""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expense_service = ExpenseService()
        self.group_service = GroupService()

    def get(self, request, group_id):
        """
        Get balance summary for a group.

        Returns:
            200: Balance summary for all members
            404: Group not found
            403: User is not a member
        """
        try:
            # Check if user is a member of the group
            group = self.group_service.get_group(group_id)
            if request.user not in group.members.all():
                return Response(
                    {'error': 'You must be a member of the group to view balance summary.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            summary = self.expense_service.calculate_balance_summary(group_id)
            serializer = BalanceSummarySerializer(summary, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except GroupNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

