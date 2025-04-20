"""
Views for the testcases app.
"""

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    TestSuite, TestCluster, TestCaseTemplate, TestCase,
    TestCaseReview, TestCaseAttachment, TestSignal
)
from .serializers import (
    TestSuiteSerializer, TestClusterSerializer, TestCaseTemplateSerializer,
    TestCaseSerializer, TestCaseReviewSerializer, TestCaseAttachmentSerializer,
    TestSignalSerializer
)
from .permissions import IsTestCaseOwnerOrReviewer
from regulations.permissions import IsAnalystOrHigher, IsManagerOrAdmin
from users.permissions import IsAdminUser


class TestSuiteViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing test suites.
    """

    queryset = TestSuite.objects.all().order_by('name')
    serializer_class = TestSuiteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

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


class TestClusterViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing test clusters.
    """

    queryset = TestCluster.objects.all().order_by('suite', 'name')
    serializer_class = TestClusterSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['suite']
    search_fields = ['name', 'description', 'suite__name']

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


class TestCaseTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing test case templates.
    """

    queryset = TestCaseTemplate.objects.all().order_by('name')
    serializer_class = TestCaseTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

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


class TestCaseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing test cases.
    """

    queryset = TestCase.objects.all().order_by('cluster', 'name')
    serializer_class = TestCaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['cluster', 'status', 'is_ai_generated', 'created_by', 'regulation_segment', 'regulation_interpretation']
    search_fields = ['name', 'description', 'cluster__name']
    ordering_fields = ['name', 'created_at', 'updated_at', 'published_at']

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
        Submit the test case for review.
        """
        test_case = self.get_object()

        # Check if the test case is in draft status
        if test_case.status != TestCase.STATUS_DRAFT:
            return Response(
                {'detail': _('Only draft test cases can be submitted for review.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the test case status
        test_case.status = TestCase.STATUS_REVIEW
        test_case.save()

        return Response(
            {'detail': _('Test case submitted for review.')},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Publish the test case.
        """
        test_case = self.get_object()

        # Check if the test case is under review
        if test_case.status != TestCase.STATUS_REVIEW:
            return Response(
                {'detail': _('Only test cases under review can be published.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the user has permission to publish
        if not (request.user.is_admin or request.user.is_manager):
            return Response(
                {'detail': _('You do not have permission to publish test cases.')},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update the test case status
        test_case.status = TestCase.STATUS_PUBLISHED
        test_case.published_at = timezone.now()
        test_case.save()

        return Response(
            {'detail': _('Test case published successfully.')},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        Archive the test case.
        """
        test_case = self.get_object()

        # Check if the test case is published
        if test_case.status != TestCase.STATUS_PUBLISHED:
            return Response(
                {'detail': _('Only published test cases can be archived.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the user has permission to archive
        if not (request.user.is_admin or request.user.is_manager):
            return Response(
                {'detail': _('You do not have permission to archive test cases.')},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update the test case status
        test_case.status = TestCase.STATUS_ARCHIVED
        test_case.save()

        return Response(
            {'detail': _('Test case archived successfully.')},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def generate_ai(self, request, pk=None):
        """
        Generate an AI test case based on the current test case template.
        """
        test_case = self.get_object()

        # Check if the test case has a template
        if not test_case.template:
            return Response(
                {'detail': _('Test case must have a template to generate AI content.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the test case has a regulation segment or interpretation
        segment_id = None
        if test_case.regulation_segment:
            segment_id = test_case.regulation_segment.id
        elif test_case.regulation_interpretation:
            segment_id = test_case.regulation_interpretation.segment.id
        else:
            return Response(
                {'detail': _('Test case must be linked to a regulation segment or interpretation.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Start the AI generation task
        from .services import generate_ai_test_case
        generate_ai_test_case.delay(test_case.id, segment_id, test_case.template.id)

        return Response(
            {'detail': _('AI test case generation started. This may take a few moments.')},
            status=status.HTTP_202_ACCEPTED
        )


class TestCaseReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing test case reviews.
    """

    queryset = TestCaseReview.objects.all().order_by('-updated_at')
    serializer_class = TestCaseReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['test_case', 'reviewer', 'status']
    search_fields = ['comments', 'test_case__name']

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


class TestCaseAttachmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing test case attachments.
    """

    queryset = TestCaseAttachment.objects.all().order_by('-created_at')
    serializer_class = TestCaseAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['test_case', 'created_by']
    search_fields = ['name', 'description', 'test_case__name']

    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsTestCaseOwnerOrReviewer]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Set the created_by field to the current user.
        """
        serializer.save(created_by=self.request.user)


class TestSignalViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing test signals.
    """

    queryset = TestSignal.objects.all().order_by('test_case', 'name')
    serializer_class = TestSignalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['test_case', 'data_type']
    search_fields = ['name', 'description', 'test_case__name']

    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsTestCaseOwnerOrReviewer]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
