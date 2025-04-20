"""
URL patterns for the dashboard app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DashboardWidgetViewSet, DashboardViewSet,
    DashboardWidgetInstanceViewSet, UserDashboardViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'widgets', DashboardWidgetViewSet)
router.register(r'', DashboardViewSet, basename='dashboard')
router.register(r'widget-instances', DashboardWidgetInstanceViewSet)
router.register(r'user-dashboards', UserDashboardViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
