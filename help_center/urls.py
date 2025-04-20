"""
URL patterns for the help_center app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    HelpCategoryViewSet, HelpArticleViewSet, FAQViewSet,
    UserFeedbackViewSet, SupportRequestViewSet, SupportResponseViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'categories', HelpCategoryViewSet)
router.register(r'articles', HelpArticleViewSet)
router.register(r'faqs', FAQViewSet)
router.register(r'feedback', UserFeedbackViewSet)
router.register(r'support', SupportRequestViewSet)
router.register(r'responses', SupportResponseViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
