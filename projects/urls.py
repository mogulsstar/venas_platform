"""
URL patterns for the projects app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProjectTypeViewSet, ProjectViewSet, ProjectMemberViewSet,
    ProjectRegulationViewSet, ProjectTestCaseViewSet,
    ProjectNoteViewSet, ProjectAttachmentViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'types', ProjectTypeViewSet)
router.register(r'', ProjectViewSet, basename='project')
router.register(r'members', ProjectMemberViewSet)
router.register(r'regulations', ProjectRegulationViewSet)
router.register(r'test-cases', ProjectTestCaseViewSet)
router.register(r'notes', ProjectNoteViewSet)
router.register(r'attachments', ProjectAttachmentViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
