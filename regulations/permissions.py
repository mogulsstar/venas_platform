"""
Custom permissions for the regulations app.
"""

from rest_framework import permissions


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
