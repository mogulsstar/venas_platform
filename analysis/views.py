"""
Views for the analysis app.
"""

import os
import time
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    AnalysisTemplate, DataSource, AnalysisTask, AnalysisTaskDataSource,
    AnalysisReport, DataCleaningRule, ValidationRule, Visualization
)
from .serializers import (
    AnalysisTemplateSerializer, DataSourceSerializer, AnalysisTaskSerializer,
    AnalysisTaskDataSourceSerializer, AnalysisReportSerializer,
    DataCleaningRuleSerializer, ValidationRuleSerializer, VisualizationSerializer
)
from .tasks import run_analysis_task
from regulations.permissions import IsAnalystOrHigher
from users.permissions import IsAdminUser


class AnalysisTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing analysis templates.
    """
    
    queryset = AnalysisTemplate.objects.all().order_by('name')
    serializer_class = AnalysisTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_global', 'created_by']
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
    
    def get_queryset(self):
        """
        Return the queryset filtered by the user's permissions.
        """
        user = self.request.user
        
        # Admins and managers can see all templates
        if user.is_admin or user.is_manager:
            return AnalysisTemplate.objects.all().order_by('name')
        
        # Other users can only see global templates or templates they created
        return AnalysisTemplate.objects.filter(
            models.Q(is_global=True) | models.Q(created_by=user)
        ).order_by('name')
    
    def perform_create(self, serializer):
        """
        Set the created_by field to the current user.
        """
        serializer.save(created_by=self.request.user)


class DataSourceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing data sources.
    """
    
    queryset = DataSource.objects.all().order_by('-created_at')
    serializer_class = DataSourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['source_type', 'file_format', 'created_by']
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


class AnalysisTaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing analysis tasks.
    """
    
    queryset = AnalysisTask.objects.all().order_by('-created_at')
    serializer_class = AnalysisTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['analysis_type', 'status', 'template', 'test_case', 'project', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at', 'completed_at', 'execution_time']
    
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
    def run(self, request, pk=None):
        """
        Run the analysis task.
        """
        task = self.get_object()
        
        # Check if the task is already running or completed
        if task.status in [AnalysisTask.STATUS_PROCESSING, AnalysisTask.STATUS_COMPLETED]:
            return Response(
                {'detail': _('Task is already running or completed.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the task has a template
        if not task.template:
            return Response(
                {'detail': _('Task must have a template to run.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the task has data sources
        if task.data_sources.count() == 0:
            return Response(
                {'detail': _('Task must have at least one data source to run.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the task status
        task.status = AnalysisTask.STATUS_PROCESSING
        task.save()
        
        # Run the task asynchronously
        run_analysis_task.delay(task.id)
        
        return Response(
            {'detail': _('Task started successfully.')},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def data_sources(self, request, pk=None):
        """
        Get the data sources associated with the task.
        """
        task = self.get_object()
        task_data_sources = task.data_sources.all()
        serializer = AnalysisTaskDataSourceSerializer(task_data_sources, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reports(self, request, pk=None):
        """
        Get the reports associated with the task.
        """
        task = self.get_object()
        reports = task.reports.all()
        serializer = AnalysisReportSerializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def cleaning_rules(self, request, pk=None):
        """
        Get the cleaning rules associated with the task.
        """
        task = self.get_object()
        rules = task.cleaning_rules.all()
        serializer = DataCleaningRuleSerializer(rules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def validation_rules(self, request, pk=None):
        """
        Get the validation rules associated with the task.
        """
        task = self.get_object()
        rules = task.validation_rules.all()
        serializer = ValidationRuleSerializer(rules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def visualizations(self, request, pk=None):
        """
        Get the visualizations associated with the task.
        """
        task = self.get_object()
        visualizations = task.visualizations.all()
        serializer = VisualizationSerializer(visualizations, many=True)
        return Response(serializer.data)


class AnalysisTaskDataSourceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing analysis task data sources.
    """
    
    queryset = AnalysisTaskDataSource.objects.all().order_by('-added_at')
    serializer_class = AnalysisTaskDataSourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task', 'data_source']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAnalystOrHigher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class AnalysisReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing analysis reports.
    """
    
    queryset = AnalysisReport.objects.all().order_by('-created_at')
    serializer_class = AnalysisReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['task', 'format', 'created_by']
    search_fields = ['title', 'description']
    
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


class DataCleaningRuleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing data cleaning rules.
    """
    
    queryset = DataCleaningRule.objects.all().order_by('task', 'rule_type', 'name')
    serializer_class = DataCleaningRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['task', 'rule_type', 'created_by']
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


class ValidationRuleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing validation rules.
    """
    
    queryset = ValidationRule.objects.all().order_by('task', 'name')
    serializer_class = ValidationRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['task', 'created_by']
    search_fields = ['name', 'description', 'expression']
    
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


class VisualizationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing visualizations.
    """
    
    queryset = Visualization.objects.all().order_by('task', 'name')
    serializer_class = VisualizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['task', 'visualization_type', 'created_by']
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
