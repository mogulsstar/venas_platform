"""
Admin configuration for the testcases app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    TestSuite, TestCluster, TestCaseTemplate, TestCase,
    TestCaseReview, TestCaseAttachment, TestSignal
)


@admin.register(TestSuite)
class TestSuiteAdmin(admin.ModelAdmin):
    """
    Admin configuration for the TestSuite model.
    """
    
    list_display = ('name', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TestCluster)
class TestClusterAdmin(admin.ModelAdmin):
    """
    Admin configuration for the TestCluster model.
    """
    
    list_display = ('name', 'suite', 'created_by', 'created_at')
    list_filter = ('suite',)
    search_fields = ('name', 'description', 'suite__name')
    ordering = ('suite', 'name')
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TestCaseTemplate)
class TestCaseTemplateAdmin(admin.ModelAdmin):
    """
    Admin configuration for the TestCaseTemplate model.
    """
    
    list_display = ('name', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    """
    Admin configuration for the TestCase model.
    """
    
    list_display = ('name', 'cluster', 'status', 'is_ai_generated', 'created_by', 'created_at')
    list_filter = ('cluster', 'status', 'is_ai_generated')
    search_fields = ('name', 'description', 'cluster__name')
    ordering = ('cluster', 'name')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'cluster', 'template')
        }),
        (_('Content'), {
            'fields': ('content',)
        }),
        (_('Related Regulation'), {
            'fields': ('regulation_segment', 'regulation_interpretation')
        }),
        (_('Status and Workflow'), {
            'fields': ('status', 'created_by', 'created_at', 'updated_at', 'published_at')
        }),
        (_('AI Generation'), {
            'fields': ('is_ai_generated',)
        }),
        (_('Versioning'), {
            'fields': ('previous_version',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'published_at')


@admin.register(TestCaseReview)
class TestCaseReviewAdmin(admin.ModelAdmin):
    """
    Admin configuration for the TestCaseReview model.
    """
    
    list_display = ('test_case', 'reviewer', 'status', 'created_at')
    list_filter = ('status', 'reviewer')
    search_fields = ('comments', 'test_case__name')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TestCaseAttachment)
class TestCaseAttachmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the TestCaseAttachment model.
    """
    
    list_display = ('name', 'test_case', 'created_by', 'created_at')
    list_filter = ('created_by',)
    search_fields = ('name', 'description', 'test_case__name')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at',)


@admin.register(TestSignal)
class TestSignalAdmin(admin.ModelAdmin):
    """
    Admin configuration for the TestSignal model.
    """
    
    list_display = ('name', 'test_case', 'data_type', 'unit')
    list_filter = ('data_type',)
    search_fields = ('name', 'description', 'test_case__name')
    ordering = ('test_case', 'name')
