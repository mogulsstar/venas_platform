"""
Views for the monitor app.
"""

import os
import psutil
import platform
from datetime import timedelta
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Avg, Max, Min
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import SystemMetric, SystemLog, UserRequest, TaskExecution, Alert
from .serializers import (
    SystemMetricSerializer, SystemLogSerializer, UserRequestSerializer,
    TaskExecutionSerializer, AlertSerializer
)
from regulations.permissions import IsManagerOrAdmin
from users.permissions import IsAdminUser


class SystemMetricViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing system metrics.
    """
    
    queryset = SystemMetric.objects.all().order_by('-timestamp')
    serializer_class = SystemMetricSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['metric_type', 'name']
    ordering_fields = ['timestamp', 'value']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Get the current system metrics.
        """
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_total = memory.total / (1024 * 1024 * 1024)  # GB
            memory_used = memory.used / (1024 * 1024 * 1024)  # GB
            memory_percent = memory.percent
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_total = disk.total / (1024 * 1024 * 1024)  # GB
            disk_used = disk.used / (1024 * 1024 * 1024)  # GB
            disk_percent = disk.percent
            
            # Network metrics
            net_io = psutil.net_io_counters()
            
            # System info
            boot_time = psutil.boot_time()
            uptime = timezone.now().timestamp() - boot_time
            
            # User metrics
            active_users = request.user.__class__.objects.filter(
                last_activity__gte=timezone.now() - timedelta(minutes=15)
            ).count()
            
            # Task metrics
            pending_tasks = TaskExecution.objects.filter(status=TaskExecution.STATUS_PENDING).count()
            running_tasks = TaskExecution.objects.filter(status=TaskExecution.STATUS_RUNNING).count()
            
            # Alert metrics
            active_alerts = Alert.objects.filter(status=Alert.STATUS_ACTIVE).count()
            
            return Response({
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count
                },
                'memory': {
                    'total': memory_total,
                    'used': memory_used,
                    'percent': memory_percent
                },
                'disk': {
                    'total': disk_total,
                    'used': disk_used,
                    'percent': disk_percent
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv
                },
                'system': {
                    'uptime': uptime,
                    'platform': platform.platform()
                },
                'users': {
                    'active': active_users
                },
                'tasks': {
                    'pending': pending_tasks,
                    'running': running_tasks
                },
                'alerts': {
                    'active': active_alerts
                }
            })
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Get the historical system metrics.
        """
        metric_type = request.query_params.get('metric_type')
        name = request.query_params.get('name')
        days = request.query_params.get('days', 7)
        
        try:
            days = int(days)
        except ValueError:
            days = 7
        
        start_date = timezone.now() - timedelta(days=days)
        
        queryset = self.get_queryset().filter(timestamp__gte=start_date)
        
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        
        if name:
            queryset = queryset.filter(name=name)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SystemLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing system logs.
    """
    
    queryset = SystemLog.objects.all().order_by('-timestamp')
    serializer_class = SystemLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['level', 'source']
    search_fields = ['message', 'source']
    ordering_fields = ['timestamp', 'level']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        return [permission() for permission in permission_classes]


class UserRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user requests.
    """
    
    queryset = UserRequest.objects.all().order_by('-timestamp')
    serializer_class = UserRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'method', 'status_code']
    search_fields = ['path', 'ip_address', 'user_agent']
    ordering_fields = ['timestamp', 'response_time']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get statistics about user requests.
        """
        days = request.query_params.get('days', 7)
        
        try:
            days = int(days)
        except ValueError:
            days = 7
        
        start_date = timezone.now() - timedelta(days=days)
        
        # Get the queryset
        queryset = self.get_queryset().filter(timestamp__gte=start_date)
        
        # Calculate statistics
        total_requests = queryset.count()
        avg_response_time = queryset.aggregate(avg=Avg('response_time'))['avg'] or 0
        max_response_time = queryset.aggregate(max=Max('response_time'))['max'] or 0
        
        # Group by status code
        status_codes = queryset.values('status_code').annotate(count=Count('id')).order_by('-count')
        
        # Group by path
        paths = queryset.values('path').annotate(count=Count('id')).order_by('-count')[:10]
        
        # Group by user
        users = queryset.values('user__email').annotate(count=Count('id')).order_by('-count')[:10]
        
        return Response({
            'total_requests': total_requests,
            'avg_response_time': avg_response_time,
            'max_response_time': max_response_time,
            'status_codes': status_codes,
            'paths': paths,
            'users': users
        })


class TaskExecutionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing task executions.
    """
    
    queryset = TaskExecution.objects.all().order_by('-created_at')
    serializer_class = TaskExecutionSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['task_type', 'status', 'user']
    search_fields = ['task_id', 'error_message']
    ordering_fields = ['created_at', 'updated_at', 'completed_at', 'execution_time']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get statistics about task executions.
        """
        days = request.query_params.get('days', 7)
        
        try:
            days = int(days)
        except ValueError:
            days = 7
        
        start_date = timezone.now() - timedelta(days=days)
        
        # Get the queryset
        queryset = self.get_queryset().filter(created_at__gte=start_date)
        
        # Calculate statistics
        total_tasks = queryset.count()
        completed_tasks = queryset.filter(status=TaskExecution.STATUS_COMPLETED).count()
        failed_tasks = queryset.filter(status=TaskExecution.STATUS_FAILED).count()
        avg_execution_time = queryset.filter(execution_time__isnull=False).aggregate(avg=Avg('execution_time'))['avg'] or 0
        
        # Group by task type
        task_types = queryset.values('task_type').annotate(count=Count('id')).order_by('-count')
        
        # Group by user
        users = queryset.values('user__email').annotate(count=Count('id')).order_by('-count')[:10]
        
        return Response({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'avg_execution_time': avg_execution_time,
            'task_types': task_types,
            'users': users
        })


class AlertViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing alerts.
    """
    
    queryset = Alert.objects.all().order_by('-created_at')
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['level', 'status', 'source']
    search_fields = ['title', 'message', 'source']
    ordering_fields = ['created_at', 'updated_at', 'acknowledged_at', 'resolved_at']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """
        Acknowledge an alert.
        """
        alert = self.get_object()
        
        # Check if the alert is already acknowledged or resolved
        if alert.status != Alert.STATUS_ACTIVE:
            return Response(
                {'detail': _('Alert is already acknowledged or resolved.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the alert
        alert.status = Alert.STATUS_ACKNOWLEDGED
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Resolve an alert.
        """
        alert = self.get_object()
        
        # Check if the alert is already resolved
        if alert.status == Alert.STATUS_RESOLVED:
            return Response(
                {'detail': _('Alert is already resolved.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the alert
        alert.status = Alert.STATUS_RESOLVED
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
