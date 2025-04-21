"""
Views for the analysis app.
"""

import os
import time
import pandas as pd
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
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
from .utils.cache import memoize, disk_cache
from .utils.query_optimization import optimize_queryset, log_queries
from .utils.pagination import paginate_queryset, paginate_dataframe, PaginatedResponse
from .utils.parsers.factory import ParserFactory
from .utils.visualization.factory import VisualizationFactory
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

    @log_queries
    def get_queryset(self):
        """
        Return the queryset filtered by the user's permissions.
        """
        user = self.request.user

        # Admins and managers can see all templates
        if user.is_admin or user.is_manager:
            queryset = AnalysisTemplate.objects.all()
        else:
            # Other users can only see global templates or templates they created
            queryset = AnalysisTemplate.objects.filter(
                models.Q(is_global=True) | models.Q(created_by=user)
            )

        # Optimize queryset
        queryset = optimize_queryset(
            queryset,
            select_related=['created_by'],
            annotations={
                'tasks_count': models.Count('tasks', distinct=True)
            }
        ).order_by('name')

        return queryset

    def perform_create(self, serializer):
        """
        Set the created_by field to the current user.
        """
        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        List all templates with pagination.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Get pagination parameters
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        try:
            page = int(page)
            page_size = int(page_size)
        except ValueError:
            page = 1
            page_size = 10

        # Paginate queryset
        paginated = paginate_queryset(queryset, page, page_size)

        # Serialize data
        serializer = self.get_serializer(paginated.items, many=True)

        # Return paginated response
        return Response({
            'results': serializer.data,
            'pagination': {
                'page': paginated.page,
                'page_size': paginated.page_size,
                'total': paginated.total,
                'total_pages': paginated.total_pages,
                'has_next': paginated.page < paginated.total_pages,
                'has_prev': paginated.page > 1
            }
        })

    @action(detail=True, methods=['get'])
    @memoize(timeout=3600)  # Cache for 1 hour
    def tasks(self, request, pk=None):
        """
        Get the tasks associated with the template.
        """
        template = self.get_object()
        tasks = template.tasks.all()

        # Get pagination parameters
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        try:
            page = int(page)
            page_size = int(page_size)
        except ValueError:
            page = 1
            page_size = 10

        # Paginate queryset
        paginated = paginate_queryset(tasks, page, page_size)

        # Serialize data
        serializer = AnalysisTaskSerializer(paginated.items, many=True)

        # Return paginated response
        return Response({
            'results': serializer.data,
            'pagination': {
                'page': paginated.page,
                'page_size': paginated.page_size,
                'total': paginated.total,
                'total_pages': paginated.total_pages,
                'has_next': paginated.page < paginated.total_pages,
                'has_prev': paginated.page > 1
            }
        })


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

    @log_queries
    def get_queryset(self):
        """
        Return the queryset with optimizations.
        """
        queryset = DataSource.objects.all()

        # Optimize queryset
        queryset = optimize_queryset(
            queryset,
            select_related=['created_by'],
            annotations={
                'tasks_count': models.Count('task_data_sources', distinct=True)
            }
        ).order_by('-created_at')

        return queryset

    def perform_create(self, serializer):
        """
        Set the created_by field to the current user.
        """
        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        List all data sources with pagination.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Get pagination parameters
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        try:
            page = int(page)
            page_size = int(page_size)
        except ValueError:
            page = 1
            page_size = 10

        # Paginate queryset
        paginated = paginate_queryset(queryset, page, page_size)

        # Serialize data
        serializer = self.get_serializer(paginated.items, many=True)

        # Return paginated response
        return Response({
            'results': serializer.data,
            'pagination': {
                'page': paginated.page,
                'page_size': paginated.page_size,
                'total': paginated.total,
                'total_pages': paginated.total_pages,
                'has_next': paginated.page < paginated.total_pages,
                'has_prev': paginated.page > 1
            }
        })

    @action(detail=True, methods=['get'])
    @disk_cache(timeout=3600)  # Cache for 1 hour
    def preview(self, request, pk=None):
        """
        Get a preview of the data source.
        """
        data_source = self.get_object()

        try:
            # Create parser based on file format
            if data_source.file_path and os.path.exists(data_source.file_path):
                parser = ParserFactory.get_parser(data_source.file_path)
                preview_data = parser.get_preview(rows=10)
                metadata = parser.get_metadata()

                return Response({
                    'preview': preview_data.to_dict('records'),
                    'columns': list(preview_data.columns),
                    'metadata': metadata
                })
            else:
                return Response(
                    {'detail': _('Data source file not found.')},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


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

    @log_queries
    def get_queryset(self):
        """
        Return the queryset with optimizations.
        """
        queryset = AnalysisTask.objects.all()

        # Optimize queryset
        queryset = optimize_queryset(
            queryset,
            select_related=['created_by', 'template', 'test_case', 'project'],
            prefetch_related=['data_sources', 'reports', 'cleaning_rules', 'validation_rules', 'visualizations'],
            annotations={
                'data_sources_count': models.Count('data_sources', distinct=True),
                'reports_count': models.Count('reports', distinct=True),
                'cleaning_rules_count': models.Count('cleaning_rules', distinct=True),
                'validation_rules_count': models.Count('validation_rules', distinct=True),
                'visualizations_count': models.Count('visualizations', distinct=True)
            }
        ).order_by('-created_at')

        return queryset

    def perform_create(self, serializer):
        """
        Set the created_by field to the current user.
        """
        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        List all tasks with pagination.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Get pagination parameters
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        try:
            page = int(page)
            page_size = int(page_size)
        except ValueError:
            page = 1
            page_size = 10

        # Paginate queryset
        paginated = paginate_queryset(queryset, page, page_size)

        # Serialize data
        serializer = self.get_serializer(paginated.items, many=True)

        # Return paginated response
        return Response({
            'results': serializer.data,
            'pagination': {
                'page': paginated.page,
                'page_size': paginated.page_size,
                'total': paginated.total,
                'total_pages': paginated.total_pages,
                'has_next': paginated.page < paginated.total_pages,
                'has_prev': paginated.page > 1
            }
        })

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

    @log_queries
    def get_queryset(self):
        """
        Return the queryset with optimizations.
        """
        queryset = Visualization.objects.all()

        # Optimize queryset
        queryset = optimize_queryset(
            queryset,
            select_related=['created_by', 'task'],
        ).order_by('task', 'name')

        return queryset

    def perform_create(self, serializer):
        """
        Set the created_by field to the current user.
        """
        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        List all visualizations with pagination.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Get pagination parameters
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        try:
            page = int(page)
            page_size = int(page_size)
        except ValueError:
            page = 1
            page_size = 10

        # Paginate queryset
        paginated = paginate_queryset(queryset, page, page_size)

        # Serialize data
        serializer = self.get_serializer(paginated.items, many=True)

        # Return paginated response
        return Response({
            'results': serializer.data,
            'pagination': {
                'page': paginated.page,
                'page_size': paginated.page_size,
                'total': paginated.total,
                'total_pages': paginated.total_pages,
                'has_next': paginated.page < paginated.total_pages,
                'has_prev': paginated.page > 1
            }
        })

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate a visualization based on data and configuration.
        """
        # Get data and configuration from request
        data = request.data.get('data')
        config = request.data.get('configuration', {})
        viz_type = request.data.get('visualization_type')
        task_id = request.data.get('task')

        if not data or not viz_type:
            return Response(
                {'detail': _('Data and visualization_type are required.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Convert data to DataFrame if it's not already
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame.from_dict(data)
            else:
                return Response(
                    {'detail': _('Invalid data format. Expected list or dict.')},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create visualization
            visualization = VisualizationFactory.create(viz_type, **config)

            # Generate visualization data
            viz_data = visualization.generate(df)

            # If task_id is provided, save the visualization
            if task_id:
                try:
                    task = AnalysisTask.objects.get(pk=task_id)

                    # Create visualization object
                    viz_obj = Visualization.objects.create(
                        name=config.get('title', f'{viz_type.capitalize()} Visualization'),
                        description=config.get('description', ''),
                        visualization_type=viz_type,
                        configuration=config,
                        data=viz_data,
                        task=task,
                        created_by=request.user
                    )

                    # Return the created visualization
                    serializer = self.get_serializer(viz_obj)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except AnalysisTask.DoesNotExist:
                    # Just return the visualization data without saving
                    pass

            # Return the visualization data
            return Response(viz_data)

        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
