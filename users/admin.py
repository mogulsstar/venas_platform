"""
Admin configuration for the users app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserActivity, UserPermission


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for the User model.
    """
    
    list_display = ('email', 'first_name', 'last_name', 'role', 'department', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'role', 'department')
    search_fields = ('email', 'first_name', 'last_name', 'department')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'profile_image')}),
        (_('Contact info'), {'fields': ('phone', 'department')}),
        (_('Permissions'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Preferences'), {'fields': ('preferred_language',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'last_activity')}),
        (_('Statistics'), {'fields': ('login_count',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_active', 'is_staff'),
        }),
    )
    
    readonly_fields = ('last_login', 'date_joined', 'last_activity', 'login_count')


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserActivity model.
    """
    
    list_display = ('user', 'action', 'action_time', 'ip_address')
    list_filter = ('action', 'action_time')
    search_fields = ('user__email', 'action', 'ip_address')
    ordering = ('-action_time',)
    
    readonly_fields = ('user', 'action', 'action_time', 'ip_address', 'user_agent', 'page')


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserPermission model.
    """
    
    list_display = ('user', 'module', 'can_view', 'can_add', 'can_edit', 'can_delete')
    list_filter = ('module', 'can_view', 'can_add', 'can_edit', 'can_delete')
    search_fields = ('user__email', 'module')
    ordering = ('user', 'module')
