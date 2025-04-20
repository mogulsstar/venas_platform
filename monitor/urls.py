"""
URL patterns for the monitor app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SystemMetricViewSet, SystemLogViewSet, UserRequestViewSet,
    TaskExecutionViewSet, AlertViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'metrics', SystemMetricViewSet)
router.register(r'logs', SystemLogViewSet)
router.register(r'requests', UserRequestViewSet)
router.register(r'tasks', TaskExecutionViewSet)
router.register(r'alerts', AlertViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
