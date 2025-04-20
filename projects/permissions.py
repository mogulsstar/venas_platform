"""
Custom permissions for the projects app.
"""

from rest_framework import permissions


class IsProjectMember(permissions.BasePermission):
    """
    Permission to only allow members of a project to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is a member of the project.
        """
        # Get the project from the object
        if hasattr(obj, 'project'):
            project = obj.project
        else:
            project = obj
        
        # Check if the user is a member of the project
        return project.members.filter(user=request.user).exists()


class IsProjectEditor(permissions.BasePermission):
    """
    Permission to only allow editors or owners of a project to modify it.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is an editor or owner of the project.
        """
        # Get the project from the object
        if hasattr(obj, 'project'):
            project = obj.project
        else:
            project = obj
        
        # Check if the user is an editor or owner of the project
        membership = project.members.filter(user=request.user).first()
        if not membership:
            return False
        
        return membership.role in [membership.ROLE_EDITOR, membership.ROLE_OWNER]


class IsProjectOwner(permissions.BasePermission):
    """
    Permission to only allow owners of a project to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is an owner of the project.
        """
        # Get the project from the object
        if hasattr(obj, 'project'):
            project = obj.project
        else:
            project = obj
        
        # Check if the user is an owner of the project
        membership = project.members.filter(user=request.user).first()
        if not membership:
            return False
        
        return membership.role == membership.ROLE_OWNER
