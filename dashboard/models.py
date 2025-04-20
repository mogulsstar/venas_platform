"""
Models for the dashboard app.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class DashboardWidget(models.Model):
    """
    Model representing a dashboard widget.
    """
    
    # Widget type choices
    TYPE_CHART = 'chart'
    TYPE_COUNTER = 'counter'
    TYPE_TABLE = 'table'
    TYPE_STATUS = 'status'
    
    TYPE_CHOICES = [
        (TYPE_CHART, _('Chart')),
        (TYPE_COUNTER, _('Counter')),
        (TYPE_TABLE, _('Table')),
        (TYPE_STATUS, _('Status')),
    ]
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    widget_type = models.CharField(_('widget type'), max_length=20, choices=TYPE_CHOICES)
    
    # Widget configuration
    configuration = models.JSONField(_('configuration'), default=dict)
    
    # Widget data
    data_source = models.CharField(_('data source'), max_length=255)
    refresh_interval = models.PositiveIntegerField(_('refresh interval'), default=60, help_text=_('Refresh interval in seconds'))
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_widgets')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('dashboard widget')
        verbose_name_plural = _('dashboard widgets')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Dashboard(models.Model):
    """
    Model representing a dashboard.
    """
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    
    # Dashboard configuration
    layout = models.JSONField(_('layout'), default=dict)
    is_default = models.BooleanField(_('is default'), default=False)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_dashboards')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('dashboard')
        verbose_name_plural = _('dashboards')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DashboardWidgetInstance(models.Model):
    """
    Model representing an instance of a widget on a dashboard.
    """
    
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='widget_instances')
    widget = models.ForeignKey(DashboardWidget, on_delete=models.CASCADE, related_name='instances')
    
    # Position and size
    position_x = models.PositiveIntegerField(_('position x'))
    position_y = models.PositiveIntegerField(_('position y'))
    width = models.PositiveIntegerField(_('width'))
    height = models.PositiveIntegerField(_('height'))
    
    # Instance-specific configuration
    configuration_override = models.JSONField(_('configuration override'), default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('dashboard widget instance')
        verbose_name_plural = _('dashboard widget instances')
        ordering = ['dashboard', 'position_y', 'position_x']
        unique_together = ('dashboard', 'position_x', 'position_y')
    
    def __str__(self):
        return f"{self.dashboard} - {self.widget}"


class UserDashboard(models.Model):
    """
    Model representing a user's dashboard preferences.
    """
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dashboards')
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='users')
    is_favorite = models.BooleanField(_('is favorite'), default=False)
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('user dashboard')
        verbose_name_plural = _('user dashboards')
        ordering = ['user', '-is_favorite', 'dashboard']
        unique_together = ('user', 'dashboard')
    
    def __str__(self):
        return f"{self.user} - {self.dashboard}"
