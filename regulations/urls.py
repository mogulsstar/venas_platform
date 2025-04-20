"""
URL patterns for the regulations app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CountryViewSet, RegionViewSet, RegulationCategoryViewSet,
    RegulationDocumentViewSet, RegulationSegmentViewSet,
    RegulationInterpretationViewSet, RegulationReviewViewSet,
    RegulationRelationshipViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'countries', CountryViewSet)
router.register(r'regions', RegionViewSet)
router.register(r'categories', RegulationCategoryViewSet)
router.register(r'documents', RegulationDocumentViewSet)
router.register(r'segments', RegulationSegmentViewSet)
router.register(r'interpretations', RegulationInterpretationViewSet)
router.register(r'reviews', RegulationReviewViewSet)
router.register(r'relationships', RegulationRelationshipViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
