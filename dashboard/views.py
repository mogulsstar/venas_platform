"""
Views for the dashboard app.
"""

from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import DashboardWidget, Dashboard, DashboardWidgetInstance, UserDashboard
from .serializers import (
    DashboardWidgetSerializer, DashboardSerializer,
    DashboardWidgetInstanceSerializer, UserDashboardSerializer
)
from regulations.permissions import IsAnalystOrHigher
from users.permissions import IsAdminUser


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing dashboard widgets.
    """
    
    queryset = DashboardWidget.objects.all().order_by('name')
    serializer_class = DashboardWidgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['widget_type', 'created_by']
    search_fields = ['name', 'description', 'data_source']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAnalystOrHigher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Set the created_by field to the current user.
        """
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def instances(self, request, pk=None):
        """
        Get the instances of the widget.
        """
        widget = self.get_object()
        instances = widget.instances.all()
        serializer = DashboardWidgetInstanceSerializer(instances, many=True)
        return Response(serializer.data)


class DashboardViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing dashboards.
    """
    
    queryset = Dashboard.objects.all().order_by('name')
    serializer_class = DashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_default', 'created_by']
    search_fields = ['name', 'description']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAnalystOrHigher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Set the created_by field to the current user.
        """
        dashboard = serializer.save(created_by=self.request.user)
        
        # Create a user dashboard for the creator
        UserDashboard.objects.create(
            user=self.request.user,
            dashboard=dashboard,
            is_favorite=True
        )
    
    @action(detail=True, methods=['get'])
    def widget_instances(self, request, pk=None):
        """
        Get the widget instances of the dashboard.
        """
        dashboard = self.get_object()
        instances = dashboard.widget_instances.all()
        serializer = DashboardWidgetInstanceSerializer(instances, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_widget(self, request, pk=None):
        """
        Add a widget to the dashboard.
        """
        dashboard = self.get_object()
        
        # Validate the request data
        widget_id = request.data.get('widget_id')
        position_x = request.data.get('position_x')
        position_y = request.data.get('position_y')
        width = request.data.get('width')
        height = request.data.get('height')
        
        if not all([widget_id, position_x is not None, position_y is not None, width, height]):
            return Response(
                {'detail': _('widget_id, position_x, position_y, width, and height are required.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            widget = DashboardWidget.objects.get(id=widget_id)
        except DashboardWidget.DoesNotExist:
            return Response(
                {'detail': _('Widget not found.')},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if there's already a widget at the specified position
        if DashboardWidgetInstance.objects.filter(
            dashboard=dashboard,
            position_x=position_x,
            position_y=position_y
        ).exists():
            return Response(
                {'detail': _('There is already a widget at the specified position.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the widget instance
        instance = DashboardWidgetInstance.objects.create(
            dashboard=dashboard,
            widget=widget,
            position_x=position_x,
            position_y=position_y,
            width=width,
            height=height,
            configuration_override=request.data.get('configuration_override', {})
        )
        
        serializer = DashboardWidgetInstanceSerializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def remove_widget(self, request, pk=None):
        """
        Remove a widget from the dashboard.
        """
        dashboard = self.get_object()
        
        # Validate the request data
        instance_id = request.data.get('instance_id')
        
        if not instance_id:
            return Response(
                {'detail': _('instance_id is required.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            instance = DashboardWidgetInstance.objects.get(id=instance_id, dashboard=dashboard)
        except DashboardWidgetInstance.DoesNotExist:
            return Response(
                {'detail': _('Widget instance not found.')},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Delete the widget instance
        instance.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def my_dashboards(self, request):
        """
        Get the dashboards of the current user.
        """
        user_dashboards = UserDashboard.objects.filter(user=request.user)
        dashboards = [ud.dashboard for ud in user_dashboards]
        serializer = self.get_serializer(dashboards, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """
        Get the default dashboard.
        """
        # Try to find a default dashboard
        try:
            dashboard = Dashboard.objects.filter(is_default=True).first()
            if not dashboard:
                # If no default dashboard, try to find a user dashboard
                user_dashboard = UserDashboard.objects.filter(user=request.user).first()
                if user_dashboard:
                    dashboard = user_dashboard.dashboard
                else:
                    # If no user dashboard, get the first dashboard
                    dashboard = Dashboard.objects.first()
            
            if dashboard:
                serializer = self.get_serializer(dashboard)
                return Response(serializer.data)
            else:
                return Response(
                    {'detail': _('No dashboards found.')},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DashboardWidgetInstanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing dashboard widget instances.
    """
    
    queryset = DashboardWidgetInstance.objects.all().order_by('dashboard', 'position_y', 'position_x')
    serializer_class = DashboardWidgetInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dashboard', 'widget']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsAnalystOrHigher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class UserDashboardViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user dashboards.
    """
    
    queryset = UserDashboard.objects.all().order_by('user', '-is_favorite', 'dashboard')
    serializer_class = UserDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'dashboard', 'is_favorite']
    
    def get_permissions(self):
        """
        Return the appropriate permissions based on the action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Return the queryset filtered by the user's permissions.
        """
        user = self.request.user
        
        # Admins and managers can see all user dashboards
        if user.is_admin or user.is_manager:
            return UserDashboard.objects.all().order_by('user', '-is_favorite', 'dashboard')
        
        # Other users can only see their own user dashboards
        return UserDashboard.objects.filter(user=user).order_by('-is_favorite', 'dashboard')
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """
        Toggle the favorite status of a user dashboard.
        """
        user_dashboard = self.get_object()
        
        # Check if the user is the owner of the user dashboard
        if user_dashboard.user != request.user and not (request.user.is_admin or request.user.is_manager):
            return Response(
                {'detail': _('You do not have permission to modify this user dashboard.')},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Toggle the favorite status
        user_dashboard.is_favorite = not user_dashboard.is_favorite
        user_dashboard.save()
        
        serializer = self.get_serializer(user_dashboard)
        return Response(serializer.data)
