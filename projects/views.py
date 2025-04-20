"""
Views for the projects app.
"""

from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    ProjectType, Project, ProjectMember, ProjectRegulation,
    ProjectTestCase, ProjectNote, ProjectAttachment
)
from .serializers import (
    ProjectTypeSerializer, ProjectSerializer, ProjectMemberSerializer,
    ProjectRegulationSerializer, ProjectTestCaseSerializer,
    ProjectNoteSerializer, ProjectAttachmentSerializer
)
from .permissions import IsProjectOwner, IsProjectMember, IsProjectEditor
from regulations.permissions import IsManagerOrAdmin
from users.permissions import IsAdminUser


class ProjectTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing project types.
    """
    
    queryset = ProjectType.objects.all().order_by('name')
    serializer_class = ProjectTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing projects.
    """
    
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'types', 'parent', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at', 'start_date', 'end_date', 'progress']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, IsProjectEditor]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, IsProjectOwner]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Return the queryset filtered by the user's permissions.
        """
        user = self.request.user
        
        # Admins and managers can see all projects
        if user.is_admin or user.is_manager:
            return Project.objects.all().order_by('-created_at')
        
        # Other users can only see projects they are members of
        return Project.objects.filter(members__user=user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """
        Set the created_by field to the current user and add the user as an owner.
        """
        project = serializer.save(created_by=self.request.user)
        
        # Add the creator as an owner
        ProjectMember.objects.create(
            project=project,
            user=self.request.user,
            role=ProjectMember.ROLE_OWNER,
            added_by=self.request.user
        )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """
        Get the members of the project.
        """
        project = self.get_object()
        members = project.members.all()
        serializer = ProjectMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def regulations(self, request, pk=None):
        """
        Get the regulations associated with the project.
        """
        project = self.get_object()
        regulations = project.regulations.all()
        serializer = ProjectRegulationSerializer(regulations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def test_cases(self, request, pk=None):
        """
        Get the test cases associated with the project.
        """
        project = self.get_object()
        test_cases = project.test_cases.all()
        serializer = ProjectTestCaseSerializer(test_cases, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        """
        Get the notes associated with the project.
        """
        project = self.get_object()
        notes = project.notes.all()
        serializer = ProjectNoteSerializer(notes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def attachments(self, request, pk=None):
        """
        Get the attachments associated with the project.
        """
        project = self.get_object()
        attachments = project.attachments.all()
        serializer = ProjectAttachmentSerializer(attachments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update the status of the project.
        """
        project = self.get_object()
        status_value = request.data.get('status')
        
        if not status_value:
            return Response(
                {'detail': _('Status is required.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if status_value not in dict(Project.STATUS_CHOICES):
            return Response(
                {'detail': _('Invalid status.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project.status = status_value
        project.save()
        
        return Response(
            {'detail': _('Project status updated successfully.')},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """
        Update the progress of the project.
        """
        project = self.get_object()
        progress = request.data.get('progress')
        
        if progress is None:
            return Response(
                {'detail': _('Progress is required.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            progress = int(progress)
        except ValueError:
            return Response(
                {'detail': _('Progress must be an integer.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if progress < 0 or progress > 100:
            return Response(
                {'detail': _('Progress must be between 0 and 100.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project.progress = progress
        project.save()
        
        return Response(
            {'detail': _('Project progress updated successfully.')},
            status=status.HTTP_200_OK
        )


class ProjectMemberViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing project members.
    """
    
    queryset = ProjectMember.objects.all().order_by('project', 'role', 'user')
    serializer_class = ProjectMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['project', 'user', 'role']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'project__name']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsProjectOwner]
        else:
            permission_classes = [permissions.IsAuthenticated, IsProjectMember]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Set the added_by field to the current user.
        """
        serializer.save(added_by=self.request.user)


class ProjectRegulationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing project regulations.
    """
    
    queryset = ProjectRegulation.objects.all().order_by('project', '-added_at')
    serializer_class = ProjectRegulationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['project', 'document', 'segment', 'interpretation']
    search_fields = ['document__title', 'project__name']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsProjectEditor]
        else:
            permission_classes = [permissions.IsAuthenticated, IsProjectMember]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Set the added_by field to the current user.
        """
        serializer.save(added_by=self.request.user)


class ProjectTestCaseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing project test cases.
    """
    
    queryset = ProjectTestCase.objects.all().order_by('project', '-added_at')
    serializer_class = ProjectTestCaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['project', 'test_case']
    search_fields = ['test_case__name', 'project__name']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsProjectEditor]
        else:
            permission_classes = [permissions.IsAuthenticated, IsProjectMember]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Set the added_by field to the current user.
        """
        serializer.save(added_by=self.request.user)


class ProjectNoteViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing project notes.
    """
    
    queryset = ProjectNote.objects.all().order_by('-updated_at')
    serializer_class = ProjectNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['project', 'created_by']
    search_fields = ['title', 'content', 'project__name']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsProjectEditor]
        else:
            permission_classes = [permissions.IsAuthenticated, IsProjectMember]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Set the created_by field to the current user.
        """
        serializer.save(created_by=self.request.user)


class ProjectAttachmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing project attachments.
    """
    
    queryset = ProjectAttachment.objects.all().order_by('-created_at')
    serializer_class = ProjectAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['project', 'created_by']
    search_fields = ['name', 'description', 'project__name']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsProjectEditor]
        else:
            permission_classes = [permissions.IsAuthenticated, IsProjectMember]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Set the created_by field to the current user.
        """
        serializer.save(created_by=self.request.user)
