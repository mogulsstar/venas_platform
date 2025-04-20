"""
URL patterns for the users app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserViewSet, UserActivityViewSet, UserPermissionViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'activities', UserActivityViewSet, basename='user-activity')
router.register(r'permissions', UserPermissionViewSet, basename='user-permission')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
