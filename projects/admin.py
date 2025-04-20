"""
Admin configuration for the projects app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    ProjectType, Project, ProjectMember, ProjectRegulation,
    ProjectTestCase, ProjectNote, ProjectAttachment
)


@admin.register(ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ProjectType model.
    """
    
    list_display = ('name',)
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Project model.
    """
    
    list_display = ('name', 'status', 'progress', 'start_date', 'end_date', 'created_by', 'created_at')
    list_filter = ('status', 'types', 'created_by')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'types', 'parent')
        }),
        (_('Status and Timeline'), {
            'fields': ('status', 'start_date', 'end_date', 'progress')
        }),
        (_('Metadata'), {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('types',)


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ProjectMember model.
    """
    
    list_display = ('user', 'project', 'role', 'added_by', 'added_at')
    list_filter = ('role', 'project')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'project__name')
    ordering = ('project', 'role', 'user')
    date_hierarchy = 'added_at'
    
    readonly_fields = ('added_at',)


@admin.register(ProjectRegulation)
class ProjectRegulationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ProjectRegulation model.
    """
    
    list_display = ('project', 'document', 'segment', 'interpretation', 'added_by', 'added_at')
    list_filter = ('project', 'document')
    search_fields = ('project__name', 'document__title')
    ordering = ('project', '-added_at')
    date_hierarchy = 'added_at'
    
    readonly_fields = ('added_at',)


@admin.register(ProjectTestCase)
class ProjectTestCaseAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ProjectTestCase model.
    """
    
    list_display = ('project', 'test_case', 'added_by', 'added_at')
    list_filter = ('project',)
    search_fields = ('project__name', 'test_case__name')
    ordering = ('project', '-added_at')
    date_hierarchy = 'added_at'
    
    readonly_fields = ('added_at',)


@admin.register(ProjectNote)
class ProjectNoteAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ProjectNote model.
    """
    
    list_display = ('title', 'project', 'created_by', 'created_at', 'updated_at')
    list_filter = ('project', 'created_by')
    search_fields = ('title', 'content', 'project__name')
    ordering = ('-updated_at',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProjectAttachment)
class ProjectAttachmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ProjectAttachment model.
    """
    
    list_display = ('name', 'project', 'created_by', 'created_at')
    list_filter = ('project', 'created_by')
    search_fields = ('name', 'description', 'project__name')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at',)
