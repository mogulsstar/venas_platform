"""
Admin configuration for the analysis app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    AnalysisTemplate, DataSource, AnalysisTask, AnalysisTaskDataSource,
    AnalysisReport, DataCleaningRule, ValidationRule, Visualization
)


@admin.register(AnalysisTemplate)
class AnalysisTemplateAdmin(admin.ModelAdmin):
    """
    Admin configuration for the AnalysisTemplate model.
    """
    
    list_display = ('name', 'is_global', 'created_by', 'created_at')
    list_filter = ('is_global', 'created_by')
    search_fields = ('name', 'description')
    ordering = ('name',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    """
    Admin configuration for the DataSource model.
    """
    
    list_display = ('name', 'source_type', 'file_format', 'created_by', 'created_at')
    list_filter = ('source_type', 'file_format', 'created_by')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at',)


@admin.register(AnalysisTask)
class AnalysisTaskAdmin(admin.ModelAdmin):
    """
    Admin configuration for the AnalysisTask model.
    """
    
    list_display = ('name', 'analysis_type', 'status', 'template', 'test_case', 'project', 'created_by', 'created_at')
    list_filter = ('analysis_type', 'status', 'template', 'created_by')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'analysis_type', 'template', 'test_case', 'project')
        }),
        (_('Status'), {
            'fields': ('status', 'error_message')
        }),
        (_('Results'), {
            'fields': ('results',)
        }),
        (_('Metadata'), {
            'fields': ('created_by', 'created_at', 'updated_at', 'completed_at', 'execution_time')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'completed_at', 'execution_time')


@admin.register(AnalysisTaskDataSource)
class AnalysisTaskDataSourceAdmin(admin.ModelAdmin):
    """
    Admin configuration for the AnalysisTaskDataSource model.
    """
    
    list_display = ('task', 'data_source', 'added_at')
    list_filter = ('task', 'data_source')
    ordering = ('-added_at',)
    date_hierarchy = 'added_at'
    
    readonly_fields = ('added_at',)


@admin.register(AnalysisReport)
class AnalysisReportAdmin(admin.ModelAdmin):
    """
    Admin configuration for the AnalysisReport model.
    """
    
    list_display = ('title', 'task', 'format', 'created_by', 'created_at')
    list_filter = ('format', 'created_by')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at',)


@admin.register(DataCleaningRule)
class DataCleaningRuleAdmin(admin.ModelAdmin):
    """
    Admin configuration for the DataCleaningRule model.
    """
    
    list_display = ('name', 'rule_type', 'task', 'created_by', 'created_at')
    list_filter = ('rule_type', 'task', 'created_by')
    search_fields = ('name', 'description')
    ordering = ('task', 'rule_type', 'name')
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at',)


@admin.register(ValidationRule)
class ValidationRuleAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ValidationRule model.
    """
    
    list_display = ('name', 'task', 'created_by', 'created_at')
    list_filter = ('task', 'created_by')
    search_fields = ('name', 'description', 'expression')
    ordering = ('task', 'name')
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at',)


@admin.register(Visualization)
class VisualizationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Visualization model.
    """
    
    list_display = ('name', 'visualization_type', 'task', 'created_by', 'created_at')
    list_filter = ('visualization_type', 'task', 'created_by')
    search_fields = ('name', 'description')
    ordering = ('task', 'name')
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at',)
