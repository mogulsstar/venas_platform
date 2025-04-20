"""
Custom permissions for the testcases app.
"""

from rest_framework import permissions


class IsTestCaseOwnerOrReviewer(permissions.BasePermission):
    """
    Permission to only allow owners of a test case or reviewers to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the owner of the test case or a reviewer.
        """
        # Get the test case from the object
        if hasattr(obj, 'test_case'):
            test_case = obj.test_case
        else:
            test_case = obj
        
        # Check if the user is the owner or a reviewer
        is_owner = test_case.created_by == request.user
        is_reviewer = test_case.reviews.filter(reviewer=request.user).exists()
        is_admin = request.user.is_admin or request.user.is_manager
        
        return is_owner or is_reviewer or is_admin
