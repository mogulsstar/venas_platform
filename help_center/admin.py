"""
Admin configuration for the help_center app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    HelpCategory, HelpArticle, FAQ, UserFeedback,
    SupportRequest, SupportResponse
)


@admin.register(HelpCategory)
class HelpCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for the HelpCategory model.
    """
    
    list_display = ('name', 'order', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('order', 'name')
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(HelpArticle)
class HelpArticleAdmin(admin.ModelAdmin):
    """
    Admin configuration for the HelpArticle model.
    """
    
    list_display = ('title', 'category', 'is_published', 'is_featured', 'order', 'created_by', 'created_at')
    list_filter = ('category', 'is_published', 'is_featured', 'created_by')
    search_fields = ('title', 'content', 'keywords')
    ordering = ('category', 'order', 'title')
    date_hierarchy = 'created_at'
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'category')
        }),
        (_('Publication'), {
            'fields': ('is_published', 'is_featured', 'order')
        }),
        (_('SEO'), {
            'fields': ('slug', 'meta_description', 'keywords')
        }),
        (_('Authorship'), {
            'fields': ('created_by', 'updated_by')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """
    Admin configuration for the FAQ model.
    """
    
    list_display = ('question', 'category', 'is_published', 'order', 'created_by', 'created_at')
    list_filter = ('category', 'is_published', 'created_by')
    search_fields = ('question', 'answer')
    ordering = ('category', 'order', 'question')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('question', 'answer', 'category')
        }),
        (_('Publication'), {
            'fields': ('is_published', 'order')
        }),
        (_('Authorship'), {
            'fields': ('created_by', 'updated_by')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserFeedback model.
    """
    
    list_display = ('content_type', 'get_content_title', 'feedback_type', 'user', 'created_at')
    list_filter = ('content_type', 'feedback_type')
    search_fields = ('comment', 'email', 'user__email')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at',)
    
    def get_content_title(self, obj):
        """
        Get the title of the content.
        """
        if obj.content_type == obj.CONTENT_ARTICLE and obj.article:
            return obj.article.title
        elif obj.content_type == obj.CONTENT_FAQ and obj.faq:
            return obj.faq.question
        return None
    get_content_title.short_description = _('Content')


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    """
    Admin configuration for the SupportRequest model.
    """
    
    list_display = ('subject', 'status', 'priority', 'user', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('subject', 'description', 'user__email')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('subject', 'description')
        }),
        (_('Request Details'), {
            'fields': ('status', 'priority', 'category')
        }),
        (_('User Information'), {
            'fields': ('user',)
        }),
        (_('Assignment'), {
            'fields': ('assigned_to',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'resolved_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'resolved_at')


@admin.register(SupportResponse)
class SupportResponseAdmin(admin.ModelAdmin):
    """
    Admin configuration for the SupportResponse model.
    """
    
    list_display = ('request', 'user', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'user')
    search_fields = ('content', 'request__subject')
    ordering = ('request', 'created_at')
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at')
