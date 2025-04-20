"""
Serializers for the help_center app.
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import (
    HelpCategory, HelpArticle, FAQ, UserFeedback,
    SupportRequest, SupportResponse
)


class HelpCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the HelpCategory model.
    """
    
    article_count = serializers.SerializerMethodField()
    faq_count = serializers.SerializerMethodField()
    
    class Meta:
        model = HelpCategory
        fields = ('id', 'name', 'description', 'icon', 'order', 'created_at', 'updated_at', 'article_count', 'faq_count')
        read_only_fields = ('created_at', 'updated_at')
    
    def get_article_count(self, obj):
        """
        Get the number of published articles in the category.
        """
        return obj.articles.filter(is_published=True).count()
    
    def get_faq_count(self, obj):
        """
        Get the number of published FAQs in the category.
        """
        return obj.faqs.filter(is_published=True).count()


class HelpArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for the HelpArticle model.
    """
    
    category_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = HelpArticle
        fields = (
            'id', 'title', 'content', 'category', 'category_name', 'is_published',
            'is_featured', 'order', 'slug', 'meta_description', 'keywords',
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def get_category_name(self, obj):
        """
        Get the name of the category.
        """
        return obj.category.name
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the article.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None
    
    def get_updated_by_name(self, obj):
        """
        Get the name of the user who last updated the article.
        """
        if obj.updated_by:
            return obj.updated_by.get_full_name() or obj.updated_by.email
        return None


class FAQSerializer(serializers.ModelSerializer):
    """
    Serializer for the FAQ model.
    """
    
    category_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FAQ
        fields = (
            'id', 'question', 'answer', 'category', 'category_name', 'is_published',
            'order', 'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def get_category_name(self, obj):
        """
        Get the name of the category.
        """
        return obj.category.name
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the FAQ.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None
    
    def get_updated_by_name(self, obj):
        """
        Get the name of the user who last updated the FAQ.
        """
        if obj.updated_by:
            return obj.updated_by.get_full_name() or obj.updated_by.email
        return None


class UserFeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserFeedback model.
    """
    
    content_title = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserFeedback
        fields = (
            'id', 'content_type', 'article', 'faq', 'content_title',
            'feedback_type', 'comment', 'user', 'user_name', 'email', 'created_at'
        )
        read_only_fields = ('created_at',)
    
    def get_content_title(self, obj):
        """
        Get the title of the content.
        """
        if obj.content_type == UserFeedback.CONTENT_ARTICLE and obj.article:
            return obj.article.title
        elif obj.content_type == UserFeedback.CONTENT_FAQ and obj.faq:
            return obj.faq.question
        return None
    
    def get_user_name(self, obj):
        """
        Get the name of the user.
        """
        if obj.user:
            return obj.user.get_full_name() or obj.user.email
        return None
    
    def validate(self, data):
        """
        Validate that either article or faq is set, but not both.
        """
        content_type = data.get('content_type')
        article = data.get('article')
        faq = data.get('faq')
        
        if content_type == UserFeedback.CONTENT_ARTICLE and not article:
            raise serializers.ValidationError({'article': _('Article must be set for article feedback.')})
        elif content_type == UserFeedback.CONTENT_FAQ and not faq:
            raise serializers.ValidationError({'faq': _('FAQ must be set for FAQ feedback.')})
        
        return data


class SupportRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for the SupportRequest model.
    """
    
    user_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    response_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportRequest
        fields = (
            'id', 'subject', 'description', 'status', 'priority', 'category',
            'category_name', 'user', 'user_name', 'assigned_to', 'assigned_to_name',
            'created_at', 'updated_at', 'resolved_at', 'response_count'
        )
        read_only_fields = ('created_at', 'updated_at', 'resolved_at')
    
    def get_user_name(self, obj):
        """
        Get the name of the user.
        """
        return obj.user.get_full_name() or obj.user.email
    
    def get_assigned_to_name(self, obj):
        """
        Get the name of the assigned user.
        """
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.email
        return None
    
    def get_category_name(self, obj):
        """
        Get the name of the category.
        """
        if obj.category:
            return obj.category.name
        return None
    
    def get_response_count(self, obj):
        """
        Get the number of responses to the request.
        """
        return obj.responses.count()


class SupportResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for the SupportResponse model.
    """
    
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportResponse
        fields = ('id', 'request', 'content', 'is_internal', 'user', 'user_name', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def get_user_name(self, obj):
        """
        Get the name of the user.
        """
        return obj.user.get_full_name() or obj.user.email
