"""
URL patterns for the testcases app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TestSuiteViewSet, TestClusterViewSet, TestCaseTemplateViewSet,
    TestCaseViewSet, TestCaseReviewViewSet, TestCaseAttachmentViewSet,
    TestSignalViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'suites', TestSuiteViewSet)
router.register(r'clusters', TestClusterViewSet)
router.register(r'templates', TestCaseTemplateViewSet)
router.register(r'cases', TestCaseViewSet)
router.register(r'reviews', TestCaseReviewViewSet)
router.register(r'attachments', TestCaseAttachmentViewSet)
router.register(r'signals', TestSignalViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
