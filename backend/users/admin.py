from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Group, GroupMembership


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom User model."""

    list_display = ('email', 'username', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Admin configuration for the Group model."""

    list_display = ('name', 'created_by', 'member_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')

    def member_count(self, obj):
        """Display member count."""
        return obj.members.count()
    member_count.short_description = 'Members'


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    """Admin configuration for the GroupMembership model."""

    list_display = ('group', 'user', 'joined_at')
    list_filter = ('joined_at',)
    search_fields = ('group__name', 'user__email')
    readonly_fields = ('joined_at',)

