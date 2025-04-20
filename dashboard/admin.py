"""
Admin configuration for the dashboard app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import DashboardWidget, Dashboard, DashboardWidgetInstance, UserDashboard


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    """
    Admin configuration for the DashboardWidget model.
    """
    
    list_display = ('name', 'widget_type', 'data_source', 'refresh_interval', 'created_by', 'created_at')
    list_filter = ('widget_type', 'created_by')
    search_fields = ('name', 'description', 'data_source')
    ordering = ('name',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Dashboard model.
    """
    
    list_display = ('name', 'is_default', 'created_by', 'created_at')
    list_filter = ('is_default', 'created_by')
    search_fields = ('name', 'description')
    ordering = ('name',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DashboardWidgetInstance)
class DashboardWidgetInstanceAdmin(admin.ModelAdmin):
    """
    Admin configuration for the DashboardWidgetInstance model.
    """
    
    list_display = ('dashboard', 'widget', 'position_x', 'position_y', 'width', 'height', 'created_at')
    list_filter = ('dashboard', 'widget')
    ordering = ('dashboard', 'position_y', 'position_x')
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserDashboard)
class UserDashboardAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserDashboard model.
    """
    
    list_display = ('user', 'dashboard', 'is_favorite', 'created_at')
    list_filter = ('is_favorite', 'user', 'dashboard')
    ordering = ('user', '-is_favorite', 'dashboard')
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at', 'updated_at')
