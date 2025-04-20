"""
Serializers for the projects app.
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import (
    ProjectType, Project, ProjectMember, ProjectRegulation,
    ProjectTestCase, ProjectNote, ProjectAttachment
)


class ProjectTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProjectType model.
    """
    
    class Meta:
        model = ProjectType
        fields = ('id', 'name', 'description')


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model.
    """
    
    types_info = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = (
            'id', 'name', 'description', 'types', 'types_info', 'parent', 'parent_name',
            'status', 'start_date', 'end_date', 'progress', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'member_count'
        )
        read_only_fields = ('created_at', 'updated_at', 'member_count')
    
    def get_types_info(self, obj):
        """
        Get information about the project types.
        """
        return [{'id': t.id, 'name': t.name} for t in obj.types.all()]
    
    def get_parent_name(self, obj):
        """
        Get the name of the parent project.
        """
        if obj.parent:
            return obj.parent.name
        return None
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the project.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None
    
    def get_member_count(self, obj):
        """
        Get the number of members in the project.
        """
        return obj.members.count()


class ProjectMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProjectMember model.
    """
    
    project_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    added_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectMember
        fields = (
            'id', 'project', 'project_name', 'user', 'user_name', 'user_email',
            'role', 'added_by', 'added_by_name', 'added_at'
        )
        read_only_fields = ('added_at',)
    
    def get_project_name(self, obj):
        """
        Get the name of the project.
        """
        return obj.project.name
    
    def get_user_name(self, obj):
        """
        Get the name of the user.
        """
        return obj.user.get_full_name() or obj.user.email
    
    def get_user_email(self, obj):
        """
        Get the email of the user.
        """
        return obj.user.email
    
    def get_added_by_name(self, obj):
        """
        Get the name of the user who added the member.
        """
        if obj.added_by:
            return obj.added_by.get_full_name() or obj.added_by.email
        return None


class ProjectRegulationSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProjectRegulation model.
    """
    
    project_name = serializers.SerializerMethodField()
    document_title = serializers.SerializerMethodField()
    segment_title = serializers.SerializerMethodField()
    interpretation_content = serializers.SerializerMethodField()
    added_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectRegulation
        fields = (
            'id', 'project', 'project_name', 'document', 'document_title',
            'segment', 'segment_title', 'interpretation', 'interpretation_content',
            'added_by', 'added_by_name', 'added_at'
        )
        read_only_fields = ('added_at',)
    
    def get_project_name(self, obj):
        """
        Get the name of the project.
        """
        return obj.project.name
    
    def get_document_title(self, obj):
        """
        Get the title of the document.
        """
        return obj.document.title
    
    def get_segment_title(self, obj):
        """
        Get the title of the segment.
        """
        if obj.segment:
            return obj.segment.title or f"Segment {obj.segment.id}"
        return None
    
    def get_interpretation_content(self, obj):
        """
        Get a preview of the interpretation content.
        """
        if obj.interpretation:
            content = obj.interpretation.content
            return content[:100] + '...' if len(content) > 100 else content
        return None
    
    def get_added_by_name(self, obj):
        """
        Get the name of the user who added the regulation.
        """
        if obj.added_by:
            return obj.added_by.get_full_name() or obj.added_by.email
        return None


class ProjectTestCaseSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProjectTestCase model.
    """
    
    project_name = serializers.SerializerMethodField()
    test_case_name = serializers.SerializerMethodField()
    test_case_status = serializers.SerializerMethodField()
    added_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectTestCase
        fields = (
            'id', 'project', 'project_name', 'test_case', 'test_case_name',
            'test_case_status', 'added_by', 'added_by_name', 'added_at'
        )
        read_only_fields = ('added_at',)
    
    def get_project_name(self, obj):
        """
        Get the name of the project.
        """
        return obj.project.name
    
    def get_test_case_name(self, obj):
        """
        Get the name of the test case.
        """
        return obj.test_case.name
    
    def get_test_case_status(self, obj):
        """
        Get the status of the test case.
        """
        return obj.test_case.get_status_display()
    
    def get_added_by_name(self, obj):
        """
        Get the name of the user who added the test case.
        """
        if obj.added_by:
            return obj.added_by.get_full_name() or obj.added_by.email
        return None


class ProjectNoteSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProjectNote model.
    """
    
    project_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectNote
        fields = (
            'id', 'project', 'project_name', 'title', 'content',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def get_project_name(self, obj):
        """
        Get the name of the project.
        """
        return obj.project.name
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the note.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None


class ProjectAttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProjectAttachment model.
    """
    
    project_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectAttachment
        fields = (
            'id', 'project', 'project_name', 'name', 'description', 'file',
            'created_by', 'created_by_name', 'created_at'
        )
        read_only_fields = ('created_at',)
    
    def get_project_name(self, obj):
        """
        Get the name of the project.
        """
        return obj.project.name
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the attachment.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None
