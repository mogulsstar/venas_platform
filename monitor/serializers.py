"""
Serializers for the monitor app.
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import SystemMetric, SystemLog, UserRequest, TaskExecution, Alert


class SystemMetricSerializer(serializers.ModelSerializer):
    """
    Serializer for the SystemMetric model.
    """
    
    metric_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemMetric
        fields = ('id', 'metric_type', 'metric_type_display', 'name', 'value', 'unit', 'timestamp')
        read_only_fields = ('timestamp',)
    
    def get_metric_type_display(self, obj):
        """
        Get the display value of the metric type.
        """
        return obj.get_metric_type_display()


class SystemLogSerializer(serializers.ModelSerializer):
    """
    Serializer for the SystemLog model.
    """
    
    level_display = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemLog
        fields = ('id', 'level', 'level_display', 'message', 'source', 'timestamp')
        read_only_fields = ('timestamp',)
    
    def get_level_display(self, obj):
        """
        Get the display value of the log level.
        """
        return obj.get_level_display()


class UserRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserRequest model.
    """
    
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserRequest
        fields = (
            'id', 'user', 'user_name', 'path', 'method', 'status_code',
            'ip_address', 'user_agent', 'response_time', 'timestamp'
        )
        read_only_fields = ('timestamp',)
    
    def get_user_name(self, obj):
        """
        Get the name of the user.
        """
        if obj.user:
            return obj.user.get_full_name() or obj.user.email
        return None


class TaskExecutionSerializer(serializers.ModelSerializer):
    """
    Serializer for the TaskExecution model.
    """
    
    task_type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskExecution
        fields = (
            'id', 'task_type', 'task_type_display', 'task_id', 'status', 'status_display',
            'user', 'user_name', 'parameters', 'result', 'error_message',
            'execution_time', 'created_at', 'updated_at', 'completed_at'
        )
        read_only_fields = ('created_at', 'updated_at', 'completed_at')
    
    def get_task_type_display(self, obj):
        """
        Get the display value of the task type.
        """
        return obj.get_task_type_display()
    
    def get_status_display(self, obj):
        """
        Get the display value of the status.
        """
        return obj.get_status_display()
    
    def get_user_name(self, obj):
        """
        Get the name of the user.
        """
        if obj.user:
            return obj.user.get_full_name() or obj.user.email
        return None


class AlertSerializer(serializers.ModelSerializer):
    """
    Serializer for the Alert model.
    """
    
    level_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    acknowledged_by_name = serializers.SerializerMethodField()
    resolved_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = (
            'id', 'level', 'level_display', 'title', 'message', 'source',
            'status', 'status_display', 'acknowledged_by', 'acknowledged_by_name',
            'acknowledged_at', 'resolved_by', 'resolved_by_name', 'resolved_at',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def get_level_display(self, obj):
        """
        Get the display value of the alert level.
        """
        return obj.get_level_display()
    
    def get_status_display(self, obj):
        """
        Get the display value of the alert status.
        """
        return obj.get_status_display()
    
    def get_acknowledged_by_name(self, obj):
        """
        Get the name of the user who acknowledged the alert.
        """
        if obj.acknowledged_by:
            return obj.acknowledged_by.get_full_name() or obj.acknowledged_by.email
        return None
    
    def get_resolved_by_name(self, obj):
        """
        Get the name of the user who resolved the alert.
        """
        if obj.resolved_by:
            return obj.resolved_by.get_full_name() or obj.resolved_by.email
        return None
