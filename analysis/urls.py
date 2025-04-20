"""
URL patterns for the analysis app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AnalysisTemplateViewSet, DataSourceViewSet, AnalysisTaskViewSet,
    AnalysisTaskDataSourceViewSet, AnalysisReportViewSet,
    DataCleaningRuleViewSet, ValidationRuleViewSet, VisualizationViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'templates', AnalysisTemplateViewSet)
router.register(r'data-sources', DataSourceViewSet)
router.register(r'tasks', AnalysisTaskViewSet)
router.register(r'task-data-sources', AnalysisTaskDataSourceViewSet)
router.register(r'reports', AnalysisReportViewSet)
router.register(r'cleaning-rules', DataCleaningRuleViewSet)
router.register(r'validation-rules', ValidationRuleViewSet)
router.register(r'visualizations', VisualizationViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
