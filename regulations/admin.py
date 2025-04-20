"""
Admin configuration for the regulations app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    Country, Region, RegulationCategory, RegulationDocument,
    RegulationSegment, RegulationInterpretation, RegulationReview,
    RegulationRelationship
)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Country model.
    """
    
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    ordering = ('name',)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Region model.
    """
    
    list_display = ('name', 'country')
    list_filter = ('country',)
    search_fields = ('name', 'country__name')
    ordering = ('country', 'name')


@admin.register(RegulationCategory)
class RegulationCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for the RegulationCategory model.
    """
    
    list_display = ('name', 'parent')
    list_filter = ('parent',)
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(RegulationDocument)
class RegulationDocumentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the RegulationDocument model.
    """
    
    list_display = ('title', 'country', 'category', 'status', 'is_processed', 'created_at')
    list_filter = ('country', 'category', 'status', 'is_processed')
    search_fields = ('title', 'description', 'document_number')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'country', 'region', 'category')
        }),
        (_('Document Metadata'), {
            'fields': ('document_number', 'version', 'publication_date', 'effective_date', 'expiration_date')
        }),
        (_('Document File'), {
            'fields': ('original_file', 'file_type')
        }),
        (_('Status and Workflow'), {
            'fields': ('status', 'created_by', 'created_at', 'updated_at', 'published_at')
        }),
        (_('Processing'), {
            'fields': ('is_processed', 'processing_errors')
        }),
        (_('Versioning'), {
            'fields': ('previous_version',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'published_at')


@admin.register(RegulationSegment)
class RegulationSegmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the RegulationSegment model.
    """
    
    list_display = ('document', 'title', 'page_number', 'order', 'is_heading', 'is_table', 'is_figure')
    list_filter = ('document', 'is_heading', 'is_table', 'is_figure')
    search_fields = ('title', 'content', 'section_number')
    ordering = ('document', 'page_number', 'order')


@admin.register(RegulationInterpretation)
class RegulationInterpretationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the RegulationInterpretation model.
    """
    
    list_display = ('segment', 'status', 'is_ai_generated', 'created_by', 'created_at')
    list_filter = ('status', 'is_ai_generated', 'created_by')
    search_fields = ('content', 'segment__title')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at', 'reviewed_at')


@admin.register(RegulationReview)
class RegulationReviewAdmin(admin.ModelAdmin):
    """
    Admin configuration for the RegulationReview model.
    """
    
    list_display = ('get_content_display', 'reviewer', 'status', 'created_at')
    list_filter = ('content_type', 'status', 'reviewer')
    search_fields = ('comments',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_content_display(self, obj):
        """
        Get a display string for the reviewed content.
        """
        if obj.content_type == obj.CONTENT_DOCUMENT and obj.document:
            return f"Document: {obj.document.title}"
        elif obj.content_type == obj.CONTENT_INTERPRETATION and obj.interpretation:
            return f"Interpretation: {obj.interpretation.segment}"
        return "Unknown content"
    get_content_display.short_description = _('Content')


@admin.register(RegulationRelationship)
class RegulationRelationshipAdmin(admin.ModelAdmin):
    """
    Admin configuration for the RegulationRelationship model.
    """
    
    list_display = ('source', 'relationship_type', 'target', 'created_by', 'created_at')
    list_filter = ('relationship_type', 'created_by')
    search_fields = ('description', 'source__title', 'target__title')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at',)
