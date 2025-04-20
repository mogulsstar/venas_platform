"""
Serializers for the analysis app.
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import (
    AnalysisTemplate, DataSource, AnalysisTask, AnalysisTaskDataSource,
    AnalysisReport, DataCleaningRule, ValidationRule, Visualization
)


class AnalysisTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for the AnalysisTemplate model.
    """
    
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalysisTemplate
        fields = ('id', 'name', 'description', 'pipeline_config', 'is_global', 'created_by', 'created_by_name', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the template.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None


class DataSourceSerializer(serializers.ModelSerializer):
    """
    Serializer for the DataSource model.
    """
    
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DataSource
        fields = (
            'id', 'name', 'description', 'source_type', 'file_format', 'file',
            'connection_string', 'api_url', 'created_by', 'created_by_name', 'created_at'
        )
        read_only_fields = ('created_at',)
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the data source.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None


class AnalysisTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the AnalysisTask model.
    """
    
    template_name = serializers.SerializerMethodField()
    test_case_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    data_sources_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalysisTask
        fields = (
            'id', 'name', 'description', 'analysis_type', 'template', 'template_name',
            'test_case', 'test_case_name', 'project', 'project_name', 'status',
            'error_message', 'results', 'created_by', 'created_by_name', 'created_at',
            'updated_at', 'completed_at', 'execution_time', 'data_sources_count'
        )
        read_only_fields = ('created_at', 'updated_at', 'completed_at', 'execution_time', 'data_sources_count')
    
    def get_template_name(self, obj):
        """
        Get the name of the template.
        """
        if obj.template:
            return obj.template.name
        return None
    
    def get_test_case_name(self, obj):
        """
        Get the name of the test case.
        """
        if obj.test_case:
            return obj.test_case.name
        return None
    
    def get_project_name(self, obj):
        """
        Get the name of the project.
        """
        if obj.project:
            return obj.project.name
        return None
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the task.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None
    
    def get_data_sources_count(self, obj):
        """
        Get the number of data sources associated with the task.
        """
        return obj.data_sources.count()


class AnalysisTaskDataSourceSerializer(serializers.ModelSerializer):
    """
    Serializer for the AnalysisTaskDataSource model.
    """
    
    task_name = serializers.SerializerMethodField()
    data_source_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalysisTaskDataSource
        fields = ('id', 'task', 'task_name', 'data_source', 'data_source_name', 'added_at')
        read_only_fields = ('added_at',)
    
    def get_task_name(self, obj):
        """
        Get the name of the task.
        """
        return obj.task.name
    
    def get_data_source_name(self, obj):
        """
        Get the name of the data source.
        """
        return obj.data_source.name


class AnalysisReportSerializer(serializers.ModelSerializer):
    """
    Serializer for the AnalysisReport model.
    """
    
    task_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalysisReport
        fields = (
            'id', 'task', 'task_name', 'title', 'description', 'content',
            'format', 'file', 'created_by', 'created_by_name', 'created_at'
        )
        read_only_fields = ('created_at',)
    
    def get_task_name(self, obj):
        """
        Get the name of the task.
        """
        return obj.task.name
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the report.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None


class DataCleaningRuleSerializer(serializers.ModelSerializer):
    """
    Serializer for the DataCleaningRule model.
    """
    
    task_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DataCleaningRule
        fields = (
            'id', 'name', 'description', 'rule_type', 'configuration',
            'task', 'task_name', 'created_by', 'created_by_name', 'created_at'
        )
        read_only_fields = ('created_at',)
    
    def get_task_name(self, obj):
        """
        Get the name of the task.
        """
        return obj.task.name
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the rule.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None


class ValidationRuleSerializer(serializers.ModelSerializer):
    """
    Serializer for the ValidationRule model.
    """
    
    task_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ValidationRule
        fields = (
            'id', 'name', 'description', 'expression', 'task',
            'task_name', 'created_by', 'created_by_name', 'created_at'
        )
        read_only_fields = ('created_at',)
    
    def get_task_name(self, obj):
        """
        Get the name of the task.
        """
        return obj.task.name
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the rule.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None


class VisualizationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Visualization model.
    """
    
    task_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Visualization
        fields = (
            'id', 'name', 'description', 'visualization_type', 'configuration',
            'task', 'task_name', 'data', 'image', 'created_by', 'created_by_name', 'created_at'
        )
        read_only_fields = ('created_at',)
    
    def get_task_name(self, obj):
        """
        Get the name of the task.
        """
        return obj.task.name
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the visualization.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None
