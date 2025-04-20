"""
Custom permissions for the users app.
"""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission to only allow administrators to access.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user is an administrator.
        """
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Permission to only allow users to access their own resources or administrators to access any.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is accessing their own resource or is an administrator.
        """
        return request.user and request.user.is_authenticated and (obj.id == request.user.id or request.user.is_admin)


class IsManagerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow managers or administrators to access.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user is a manager or administrator.
        """
        return request.user and request.user.is_authenticated and (request.user.is_manager or request.user.is_admin)


class IsAnalystOrHigher(permissions.BasePermission):
    """
    Permission to only allow analysts, managers, or administrators to access.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user is an analyst, manager, or administrator.
        """
        return request.user and request.user.is_authenticated and (
            request.user.is_analyst or request.user.is_manager or request.user.is_admin
        )
