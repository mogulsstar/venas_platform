"""
Admin configuration for the monitor app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import SystemMetric, SystemLog, UserRequest, TaskExecution, Alert


@admin.register(SystemMetric)
class SystemMetricAdmin(admin.ModelAdmin):
    """
    Admin configuration for the SystemMetric model.
    """
    
    list_display = ('metric_type', 'name', 'value', 'unit', 'timestamp')
    list_filter = ('metric_type', 'name')
    search_fields = ('name',)
    ordering = ('-timestamp', 'metric_type', 'name')
    date_hierarchy = 'timestamp'
    
    readonly_fields = ('timestamp',)


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    """
    Admin configuration for the SystemLog model.
    """
    
    list_display = ('level', 'source', 'message', 'timestamp')
    list_filter = ('level', 'source')
    search_fields = ('message', 'source')
    ordering = ('-timestamp', 'level')
    date_hierarchy = 'timestamp'
    
    readonly_fields = ('timestamp',)


@admin.register(UserRequest)
class UserRequestAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserRequest model.
    """
    
    list_display = ('user', 'method', 'path', 'status_code', 'response_time', 'ip_address', 'timestamp')
    list_filter = ('method', 'status_code', 'user')
    search_fields = ('path', 'ip_address', 'user_agent')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    readonly_fields = ('timestamp',)


@admin.register(TaskExecution)
class TaskExecutionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the TaskExecution model.
    """
    
    list_display = ('task_type', 'task_id', 'status', 'user', 'execution_time', 'created_at', 'completed_at')
    list_filter = ('task_type', 'status', 'user')
    search_fields = ('task_id', 'error_message')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('task_type', 'task_id', 'status', 'user')
        }),
        (_('Task Details'), {
            'fields': ('parameters', 'result', 'error_message')
        }),
        (_('Performance'), {
            'fields': ('execution_time',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'completed_at')


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Alert model.
    """
    
    list_display = ('level', 'title', 'source', 'status', 'created_at', 'acknowledged_by', 'resolved_by')
    list_filter = ('level', 'status', 'source')
    search_fields = ('title', 'message', 'source')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('level', 'title', 'message', 'source', 'status')
        }),
        (_('Acknowledgement'), {
            'fields': ('acknowledged_by', 'acknowledged_at')
        }),
        (_('Resolution'), {
            'fields': ('resolved_by', 'resolved_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
