"""
Views for the regulations app.
"""

import os
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings

from .models import (
    Country, Region, RegulationCategory, RegulationDocument,
    RegulationSegment, RegulationInterpretation, RegulationReview,
    RegulationRelationship
)
from .serializers import (
    CountrySerializer, RegionSerializer, RegulationCategorySerializer,
    RegulationDocumentSerializer, RegulationSegmentSerializer,
    RegulationInterpretationSerializer, RegulationReviewSerializer,
    RegulationRelationshipSerializer
)
from .permissions import IsManagerOrAdmin, IsAnalystOrHigher
from .tasks import process_regulation_document, batch_process_regulation_documents, translate_regulation_document
from users.permissions import IsAdminUser


class CountryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing countries.
    """

    queryset = Country.objects.all().order_by('name')
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']

    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class RegionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing regions.
    """

    queryset = Region.objects.all().order_by('country', 'name')
    serializer_class = RegionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['country']
    search_fields = ['name', 'country__name']

    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class RegulationCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing regulation categories.
    """

    queryset = RegulationCategory.objects.all().order_by('name')
    serializer_class = RegulationCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['parent']
    search_fields = ['name', 'description']

    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class RegulationDocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing regulation documents.
    """

    queryset = RegulationDocument.objects.all().order_by('-updated_at')
    serializer_class = RegulationDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country', 'region', 'category', 'status', 'is_processed']
    search_fields = ['title', 'description', 'document_number']
    ordering_fields = ['title', 'publication_date', 'effective_date', 'created_at', 'updated_at']

    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAnalystOrHigher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Set the created_by field to the current user.
        """
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """
        Process the regulation document to extract segments.
        """
        document = self.get_object()

        # Check if the document is already processed
        if document.is_processed:
            return Response(
                {'detail': _('Document is already processed.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the document is a PDF
        if document.file_extension != '.pdf':
            return Response(
                {'detail': _('Only PDF documents can be processed.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Start the processing task
        process_regulation_document.delay(document.id)

        return Response(
            {'detail': _('Document processing started.')},
            status=status.HTTP_202_ACCEPTED
        )

    @action(detail=False, methods=['post'])
    def batch_process(self, request):
        """
        Process multiple regulation documents to extract segments.
        """
        document_ids = request.data.get('document_ids', [])

        if not document_ids:
            return Response(
                {'detail': _('No document IDs provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if all documents exist and are PDFs
        documents = RegulationDocument.objects.filter(id__in=document_ids)

        if len(documents) != len(document_ids):
            return Response(
                {'detail': _('One or more documents not found.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Filter out already processed documents
        unprocessed_ids = [doc.id for doc in documents if not doc.is_processed and doc.file_extension == '.pdf']

        if not unprocessed_ids:
            return Response(
                {'detail': _('No unprocessed PDF documents found.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Start the batch processing task
        batch_process_regulation_documents.delay(unprocessed_ids)

        return Response(
            {
                'detail': _('Batch processing started.'),
                'processing_count': len(unprocessed_ids),
                'skipped_count': len(document_ids) - len(unprocessed_ids)
            },
            status=status.HTTP_202_ACCEPTED
        )

    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, pk=None):
        """
        Submit the document for review.
        """
        document = self.get_object()

        # Check if the document is in draft status
        if document.status != RegulationDocument.STATUS_DRAFT:
            return Response(
                {'detail': _('Only draft documents can be submitted for review.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the document status
        document.status = RegulationDocument.STATUS_REVIEW
        document.save()

        return Response(
            {'detail': _('Document submitted for review.')},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Publish the document.
        """
        document = self.get_object()

        # Check if the document is under review
        if document.status != RegulationDocument.STATUS_REVIEW:
            return Response(
                {'detail': _('Only documents under review can be published.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the user has permission to publish
        if not (request.user.is_admin or request.user.is_manager):
            return Response(
                {'detail': _('You do not have permission to publish documents.')},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update the document status
        document.status = RegulationDocument.STATUS_PUBLISHED
        document.published_at = timezone.now()
        document.save()

        return Response(
            {'detail': _('Document published successfully.')},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        Archive the document.
        """
        document = self.get_object()

        # Check if the document is published
        if document.status != RegulationDocument.STATUS_PUBLISHED:
            return Response(
                {'detail': _('Only published documents can be archived.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the user has permission to archive
        if not (request.user.is_admin or request.user.is_manager):
            return Response(
                {'detail': _('You do not have permission to archive documents.')},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update the document status
        document.status = RegulationDocument.STATUS_ARCHIVED
        document.save()

        return Response(
            {'detail': _('Document archived successfully.')},
            status=status.HTTP_200_OK
        )


class RegulationSegmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing regulation segments.
    """

    queryset = RegulationSegment.objects.all().order_by('document', 'page_number', 'order')
    serializer_class = RegulationSegmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['document', 'page_number', 'is_heading', 'is_table', 'is_figure', 'parent']
    search_fields = ['title', 'content', 'section_number']

    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAnalystOrHigher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'])
    def translate(self, request, pk=None):
        """
        Translate the segment content to the specified language.
        """
        segment = self.get_object()
        language = request.data.get('language')

        if not language:
            return Response(
                {'detail': _('Language is required.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the language is supported
        supported_languages = [lang[0] for lang in settings.LANGUAGES]
        if language not in supported_languages:
            return Response(
                {'detail': _('Unsupported language. Supported languages are: {}').format(', '.join(supported_languages))},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the segment already has a translation for this language
        if segment.translations and language in segment.translations:
            return Response(
                {'detail': _('Segment already has a translation for this language.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the document's language
        document_language = segment.document.language or 'en'

        # Start the translation task
        from .services import TranslationService
        service = TranslationService()

        try:
            # Translate the segment
            translated_title = service.translate_text(segment.title or '', document_language, language)
            translated_content = service.translate_text(segment.content, document_language, language)

            # Update the segment's translations
            translations = segment.translations or {}
            translations[language] = {
                'title': translated_title,
                'content': translated_content,
                'is_verified': False  # Needs human verification
            }

            segment.translations = translations
            segment.save()

            return Response(
                {'detail': _('Segment translated successfully.')},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def batch_translate(self, request):
        """
        Translate multiple segments to the specified language.
        """
        segment_ids = request.data.get('segment_ids', [])
        language = request.data.get('language')

        if not segment_ids:
            return Response(
                {'detail': _('No segment IDs provided.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not language:
            return Response(
                {'detail': _('Language is required.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the language is supported
        supported_languages = [lang[0] for lang in settings.LANGUAGES]
        if language not in supported_languages:
            return Response(
                {'detail': _('Unsupported language. Supported languages are: {}').format(', '.join(supported_languages))},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if all segments exist
        segments = RegulationSegment.objects.filter(id__in=segment_ids)

        if len(segments) != len(segment_ids):
            return Response(
                {'detail': _('One or more segments not found.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Group segments by document
        document_segments = {}
        for segment in segments:
            if segment.document_id not in document_segments:
                document_segments[segment.document_id] = []
            document_segments[segment.document_id].append(segment.id)

        # Start translation tasks for each document
        for document_id, segment_ids in document_segments.items():
            translate_regulation_document.delay(document_id, language)

        return Response(
            {
                'detail': _('Batch translation started.'),
                'document_count': len(document_segments),
                'segment_count': len(segment_ids)
            },
            status=status.HTTP_202_ACCEPTED
        )


class RegulationInterpretationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing regulation interpretations.
    """

    queryset = RegulationInterpretation.objects.all().order_by('-updated_at')
    serializer_class = RegulationInterpretationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['segment', 'status', 'is_ai_generated', 'created_by']
    search_fields = ['content']

    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAnalystOrHigher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Set the created_by field to the current user.
        """
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, pk=None):
        """
        Submit the interpretation for review.
        """
        interpretation = self.get_object()

        # Check if the interpretation is in draft status
        if interpretation.status != RegulationInterpretation.STATUS_DRAFT:
            return Response(
                {'detail': _('Only draft interpretations can be submitted for review.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the interpretation status
        interpretation.status = RegulationInterpretation.STATUS_REVIEW
        interpretation.save()

        return Response(
            {'detail': _('Interpretation submitted for review.')},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Publish the interpretation.
        """
        interpretation = self.get_object()

        # Check if the interpretation is under review
        if interpretation.status != RegulationInterpretation.STATUS_REVIEW:
            return Response(
                {'detail': _('Only interpretations under review can be published.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the user has permission to publish
        if not (request.user.is_admin or request.user.is_manager):
            return Response(
                {'detail': _('You do not have permission to publish interpretations.')},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update the interpretation status
        interpretation.status = RegulationInterpretation.STATUS_PUBLISHED
        interpretation.reviewed_by = request.user
        interpretation.reviewed_at = timezone.now()
        interpretation.save()

        return Response(
            {'detail': _('Interpretation published successfully.')},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def generate_ai(self, request, pk=None):
        """
        Generate an AI interpretation for the segment.
        """
        segment = self.get_object().segment

        # TODO: Implement AI interpretation generation
        # This would typically call an AI service

        # For now, just return a placeholder response
        return Response(
            {'detail': _('AI interpretation generation will be implemented in a future update.')},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )


class RegulationReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing regulation reviews.
    """

    queryset = RegulationReview.objects.all().order_by('-updated_at')
    serializer_class = RegulationReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['content_type', 'document', 'interpretation', 'reviewer', 'status']
    search_fields = ['comments']

    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAnalystOrHigher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Set the reviewer field to the current user.
        """
        serializer.save(reviewer=self.request.user)


class RegulationRelationshipViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing regulation relationships.
    """

    queryset = RegulationRelationship.objects.all().order_by('-created_at')
    serializer_class = RegulationRelationshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['source', 'target', 'relationship_type', 'created_by']
    search_fields = ['description']

    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAnalystOrHigher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Set the created_by field to the current user.
        """
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def find_similar(self, request):
        """
        Find segments similar to the specified segment.
        """
        segment_id = request.query_params.get('segment_id')

        if not segment_id:
            return Response(
                {'detail': _('Segment ID is required.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            segment = RegulationSegment.objects.get(id=segment_id)
        except RegulationSegment.DoesNotExist:
            return Response(
                {'detail': _('Segment not found.')},
                status=status.HTTP_404_NOT_FOUND
            )

        # TODO: Implement similarity search logic
        # This would typically use a text similarity algorithm

        # For now, just return a placeholder response
        return Response(
            {'detail': _('Similarity search will be implemented in a future update.')},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
