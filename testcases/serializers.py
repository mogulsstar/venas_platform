"""
Serializers for the testcases app.
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import (
    TestSuite, TestCluster, TestCaseTemplate, TestCase,
    TestCaseReview, TestCaseAttachment, TestSignal
)


class TestSuiteSerializer(serializers.ModelSerializer):
    """
    Serializer for the TestSuite model.
    """
    
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TestSuite
        fields = ('id', 'name', 'description', 'created_by', 'created_by_name', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the test suite.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None


class TestClusterSerializer(serializers.ModelSerializer):
    """
    Serializer for the TestCluster model.
    """
    
    suite_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TestCluster
        fields = ('id', 'name', 'description', 'suite', 'suite_name', 'created_by', 'created_by_name', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def get_suite_name(self, obj):
        """
        Get the name of the test suite.
        """
        return obj.suite.name
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the test cluster.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None


class TestCaseTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for the TestCaseTemplate model.
    """
    
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TestCaseTemplate
        fields = ('id', 'name', 'description', 'structure', 'created_by', 'created_by_name', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the template.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None


class TestCaseSerializer(serializers.ModelSerializer):
    """
    Serializer for the TestCase model.
    """
    
    cluster_name = serializers.SerializerMethodField()
    template_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    regulation_info = serializers.SerializerMethodField()
    
    class Meta:
        model = TestCase
        fields = (
            'id', 'name', 'description', 'cluster', 'cluster_name', 'template', 'template_name',
            'content', 'regulation_segment', 'regulation_interpretation', 'regulation_info',
            'status', 'created_by', 'created_by_name', 'created_at', 'updated_at',
            'published_at', 'is_ai_generated', 'previous_version'
        )
        read_only_fields = ('created_at', 'updated_at', 'published_at')
    
    def get_cluster_name(self, obj):
        """
        Get the name of the test cluster.
        """
        return obj.cluster.name
    
    def get_template_name(self, obj):
        """
        Get the name of the template.
        """
        if obj.template:
            return obj.template.name
        return None
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the test case.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None
    
    def get_regulation_info(self, obj):
        """
        Get information about the related regulation.
        """
        if obj.regulation_segment:
            return {
                'type': 'segment',
                'id': obj.regulation_segment.id,
                'title': obj.regulation_segment.title or f"Segment {obj.regulation_segment.id}",
                'document': obj.regulation_segment.document.title
            }
        elif obj.regulation_interpretation:
            return {
                'type': 'interpretation',
                'id': obj.regulation_interpretation.id,
                'segment': obj.regulation_interpretation.segment.title or f"Segment {obj.regulation_interpretation.segment.id}",
                'document': obj.regulation_interpretation.segment.document.title
            }
        return None


class TestCaseReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the TestCaseReview model.
    """
    
    test_case_name = serializers.SerializerMethodField()
    reviewer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TestCaseReview
        fields = ('id', 'test_case', 'test_case_name', 'reviewer', 'reviewer_name', 'status', 'comments', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def get_test_case_name(self, obj):
        """
        Get the name of the test case.
        """
        return obj.test_case.name
    
    def get_reviewer_name(self, obj):
        """
        Get the name of the reviewer.
        """
        return obj.reviewer.get_full_name() or obj.reviewer.email


class TestCaseAttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the TestCaseAttachment model.
    """
    
    test_case_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TestCaseAttachment
        fields = ('id', 'test_case', 'test_case_name', 'name', 'description', 'file', 'created_by', 'created_by_name', 'created_at')
        read_only_fields = ('created_at',)
    
    def get_test_case_name(self, obj):
        """
        Get the name of the test case.
        """
        return obj.test_case.name
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the attachment.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None


class TestSignalSerializer(serializers.ModelSerializer):
    """
    Serializer for the TestSignal model.
    """
    
    test_case_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TestSignal
        fields = ('id', 'test_case', 'test_case_name', 'name', 'description', 'data_type', 'unit', 'min_value', 'max_value')
    
    def get_test_case_name(self, obj):
        """
        Get the name of the test case.
        """
        return obj.test_case.name
