"""
Serializers for the dashboard app.
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import DashboardWidget, Dashboard, DashboardWidgetInstance, UserDashboard


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """
    Serializer for the DashboardWidget model.
    """
    
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DashboardWidget
        fields = (
            'id', 'name', 'description', 'widget_type', 'configuration',
            'data_source', 'refresh_interval', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the widget.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None


class DashboardWidgetInstanceSerializer(serializers.ModelSerializer):
    """
    Serializer for the DashboardWidgetInstance model.
    """
    
    widget_name = serializers.SerializerMethodField()
    widget_type = serializers.SerializerMethodField()
    
    class Meta:
        model = DashboardWidgetInstance
        fields = (
            'id', 'dashboard', 'widget', 'widget_name', 'widget_type',
            'position_x', 'position_y', 'width', 'height',
            'configuration_override', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def get_widget_name(self, obj):
        """
        Get the name of the widget.
        """
        return obj.widget.name
    
    def get_widget_type(self, obj):
        """
        Get the type of the widget.
        """
        return obj.widget.widget_type


class DashboardSerializer(serializers.ModelSerializer):
    """
    Serializer for the Dashboard model.
    """
    
    created_by_name = serializers.SerializerMethodField()
    widget_instances = DashboardWidgetInstanceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Dashboard
        fields = (
            'id', 'name', 'description', 'layout', 'is_default',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'widget_instances'
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def get_created_by_name(self, obj):
        """
        Get the name of the user who created the dashboard.
        """
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None


class UserDashboardSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserDashboard model.
    """
    
    dashboard_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserDashboard
        fields = (
            'id', 'user', 'user_name', 'dashboard', 'dashboard_name',
            'is_favorite', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def get_dashboard_name(self, obj):
        """
        Get the name of the dashboard.
        """
        return obj.dashboard.name
    
    def get_user_name(self, obj):
        """
        Get the name of the user.
        """
        return obj.user.get_full_name() or obj.user.email
