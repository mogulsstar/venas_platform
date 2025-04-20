"""
Serializers for the regulations app.
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import (
    Country, Region, RegulationCategory, RegulationDocument,
    RegulationSegment, RegulationInterpretation, RegulationReview,
    RegulationRelationship
)


class CountrySerializer(serializers.ModelSerializer):
    """
    Serializer for the Country model.
    """
    
    class Meta:
        model = Country
        fields = ('id', 'name', 'code', 'flag')


class RegionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Region model.
    """
    
    country_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Region
        fields = ('id', 'name', 'country', 'country_name')
    
    def get_country_name(self, obj):
        """
        Get the name of the country.
        """
        return obj.country.name


class RegulationCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the RegulationCategory model.
    """
    
    parent_name = serializers.SerializerMethodField()
    
    class Meta:
        model = RegulationCategory
        fields = ('id', 'name', 'description', 'parent', 'parent_name')
    
    def get_parent_name(self, obj):
        """
        Get the name of the parent category.
        """
        if obj.parent:
            return obj.parent.name
        return None


class RegulationDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for the RegulationDocument model.
    """
    
    country_name = serializers.SerializerMethodField()
    region_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = RegulationDocument
        fields = (
            'id', 'title', 'description', 'country', 'country_name', 'region', 'region_name',
            'category', 'category_name', 'document_number', 'version', 'publication_date',
            'effective_date', 'expiration_date', 'original_file', 'file_type',
            'status', 'created_by', 'created_by_name', 'created_at', 'updated_at',
            'published_at', 'is_processed', 'processing_errors', 'previous_version'
        )
        read_only_fields = ('created_at', 'updated_at', 'published_at', 'is_processed', 'processing_errors')
    
    def get_country_name(self, obj):
        """
        Get the name of the country.
        """
        return obj.country.name
    
    def get_region_name(self, obj):
        """
        Get the name of the region.
        """
        if obj.region:
            return obj.region.name
        return None
    
    def get_category_name(self, obj):
        """
        Get the name of the category.
        """
        if obj.category:
            return obj.category.name
        return None
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the document.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None


class RegulationSegmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the RegulationSegment model.
    """
    
    document_title = serializers.SerializerMethodField()
    parent_title = serializers.SerializerMethodField()
    
    class Meta:
        model = RegulationSegment
        fields = (
            'id', 'document', 'document_title', 'title', 'content', 'page_number',
            'order', 'is_heading', 'is_table', 'is_figure', 'section_number',
            'parent', 'parent_title', 'translations'
        )
    
    def get_document_title(self, obj):
        """
        Get the title of the document.
        """
        return obj.document.title
    
    def get_parent_title(self, obj):
        """
        Get the title of the parent segment.
        """
        if obj.parent:
            return obj.parent.title
        return None


class RegulationInterpretationSerializer(serializers.ModelSerializer):
    """
    Serializer for the RegulationInterpretation model.
    """
    
    segment_title = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = RegulationInterpretation
        fields = (
            'id', 'segment', 'segment_title', 'content', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'status', 'reviewed_by', 'reviewed_by_name',
            'reviewed_at', 'is_ai_generated', 'translations'
        )
        read_only_fields = ('created_at', 'updated_at', 'reviewed_at')
    
    def get_segment_title(self, obj):
        """
        Get the title of the segment.
        """
        return obj.segment.title or f"Segment {obj.segment.id}"
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the interpretation.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None
    
    def get_reviewed_by_name(self, obj):
        """
        Get the name of the user who reviewed the interpretation.
        """
        if obj.reviewed_by:
            return obj.reviewed_by.get_full_name() or obj.reviewed_by.email
        return None


class RegulationReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the RegulationReview model.
    """
    
    reviewer_name = serializers.SerializerMethodField()
    content_title = serializers.SerializerMethodField()
    
    class Meta:
        model = RegulationReview
        fields = (
            'id', 'content_type', 'document', 'interpretation', 'content_title',
            'reviewer', 'reviewer_name', 'status', 'comments', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def get_reviewer_name(self, obj):
        """
        Get the name of the reviewer.
        """
        return obj.reviewer.get_full_name() or obj.reviewer.email
    
    def get_content_title(self, obj):
        """
        Get the title of the reviewed content.
        """
        if obj.content_type == RegulationReview.CONTENT_DOCUMENT and obj.document:
            return obj.document.title
        elif obj.content_type == RegulationReview.CONTENT_INTERPRETATION and obj.interpretation:
            return f"Interpretation of {obj.interpretation.segment}"
        return None
    
    def validate(self, data):
        """
        Validate that either document or interpretation is set, but not both.
        """
        content_type = data.get('content_type')
        document = data.get('document')
        interpretation = data.get('interpretation')
        
        if content_type == RegulationReview.CONTENT_DOCUMENT and not document:
            raise serializers.ValidationError({'document': _('Document must be set for document reviews.')})
        elif content_type == RegulationReview.CONTENT_INTERPRETATION and not interpretation:
            raise serializers.ValidationError({'interpretation': _('Interpretation must be set for interpretation reviews.')})
        
        return data


class RegulationRelationshipSerializer(serializers.ModelSerializer):
    """
    Serializer for the RegulationRelationship model.
    """
    
    source_title = serializers.SerializerMethodField()
    target_title = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = RegulationRelationship
        fields = (
            'id', 'source', 'source_title', 'target', 'target_title',
            'relationship_type', 'description', 'created_by', 'created_by_name',
            'created_at', 'similarity_score'
        )
        read_only_fields = ('created_at',)
    
    def get_source_title(self, obj):
        """
        Get the title of the source segment.
        """
        return obj.source.title or f"Segment {obj.source.id}"
    
    def get_target_title(self, obj):
        """
        Get the title of the target segment.
        """
        return obj.target.title or f"Segment {obj.target.id}"
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the relationship.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None
