"""
Models for the monitor app.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class SystemMetric(models.Model):
    """
    Model representing a system metric.
    """
    
    # Metric type choices
    TYPE_CPU = 'cpu'
    TYPE_MEMORY = 'memory'
    TYPE_DISK = 'disk'
    TYPE_NETWORK = 'network'
    TYPE_USERS = 'users'
    TYPE_REQUESTS = 'requests'
    TYPE_TASKS = 'tasks'
    
    TYPE_CHOICES = [
        (TYPE_CPU, _('CPU')),
        (TYPE_MEMORY, _('Memory')),
        (TYPE_DISK, _('Disk')),
        (TYPE_NETWORK, _('Network')),
        (TYPE_USERS, _('Users')),
        (TYPE_REQUESTS, _('Requests')),
        (TYPE_TASKS, _('Tasks')),
    ]
    
    metric_type = models.CharField(_('metric type'), max_length=20, choices=TYPE_CHOICES)
    name = models.CharField(_('name'), max_length=255)
    value = models.FloatField(_('value'))
    unit = models.CharField(_('unit'), max_length=50, blank=True)
    
    # Metadata
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('system metric')
        verbose_name_plural = _('system metrics')
        ordering = ['-timestamp', 'metric_type', 'name']
    
    def __str__(self):
        return f"{self.get_metric_type_display()} - {self.name}: {self.value} {self.unit}"


class SystemLog(models.Model):
    """
    Model representing a system log entry.
    """
    
    # Log level choices
    LEVEL_DEBUG = 'debug'
    LEVEL_INFO = 'info'
    LEVEL_WARNING = 'warning'
    LEVEL_ERROR = 'error'
    LEVEL_CRITICAL = 'critical'
    
    LEVEL_CHOICES = [
        (LEVEL_DEBUG, _('Debug')),
        (LEVEL_INFO, _('Info')),
        (LEVEL_WARNING, _('Warning')),
        (LEVEL_ERROR, _('Error')),
        (LEVEL_CRITICAL, _('Critical')),
    ]
    
    level = models.CharField(_('level'), max_length=20, choices=LEVEL_CHOICES)
    message = models.TextField(_('message'))
    source = models.CharField(_('source'), max_length=255)
    
    # Metadata
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('system log')
        verbose_name_plural = _('system logs')
        ordering = ['-timestamp', 'level']
    
    def __str__(self):
        return f"{self.get_level_display()} - {self.source}: {self.message[:50]}..."


class UserRequest(models.Model):
    """
    Model representing a user request.
    """
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='requests')
    path = models.CharField(_('path'), max_length=255)
    method = models.CharField(_('method'), max_length=10)
    status_code = models.PositiveIntegerField(_('status code'))
    
    # Request details
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    
    # Performance metrics
    response_time = models.FloatField(_('response time'), help_text=_('Response time in seconds'))
    
    # Metadata
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('user request')
        verbose_name_plural = _('user requests')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code} - {self.response_time:.2f}s"


class TaskExecution(models.Model):
    """
    Model representing a task execution.
    """
    
    # Task type choices
    TYPE_ANALYSIS = 'analysis'
    TYPE_PDF_PROCESSING = 'pdf_processing'
    TYPE_TRANSLATION = 'translation'
    TYPE_AI_GENERATION = 'ai_generation'
    
    TYPE_CHOICES = [
        (TYPE_ANALYSIS, _('Analysis')),
        (TYPE_PDF_PROCESSING, _('PDF Processing')),
        (TYPE_TRANSLATION, _('Translation')),
        (TYPE_AI_GENERATION, _('AI Generation')),
    ]
    
    # Status choices
    STATUS_PENDING = 'pending'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending')),
        (STATUS_RUNNING, _('Running')),
        (STATUS_COMPLETED, _('Completed')),
        (STATUS_FAILED, _('Failed')),
    ]
    
    task_type = models.CharField(_('task type'), max_length=20, choices=TYPE_CHOICES)
    task_id = models.CharField(_('task ID'), max_length=255)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES)
    
    # Task details
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='task_executions')
    parameters = models.JSONField(_('parameters'), default=dict, blank=True)
    result = models.JSONField(_('result'), default=dict, blank=True)
    error_message = models.TextField(_('error message'), blank=True)
    
    # Performance metrics
    execution_time = models.FloatField(_('execution time'), null=True, blank=True, help_text=_('Execution time in seconds'))
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('task execution')
        verbose_name_plural = _('task executions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_task_type_display()} - {self.task_id} - {self.get_status_display()}"


class Alert(models.Model):
    """
    Model representing a system alert.
    """
    
    # Alert level choices
    LEVEL_INFO = 'info'
    LEVEL_WARNING = 'warning'
    LEVEL_ERROR = 'error'
    LEVEL_CRITICAL = 'critical'
    
    LEVEL_CHOICES = [
        (LEVEL_INFO, _('Info')),
        (LEVEL_WARNING, _('Warning')),
        (LEVEL_ERROR, _('Error')),
        (LEVEL_CRITICAL, _('Critical')),
    ]
    
    # Alert status choices
    STATUS_ACTIVE = 'active'
    STATUS_ACKNOWLEDGED = 'acknowledged'
    STATUS_RESOLVED = 'resolved'
    
    STATUS_CHOICES = [
        (STATUS_ACTIVE, _('Active')),
        (STATUS_ACKNOWLEDGED, _('Acknowledged')),
        (STATUS_RESOLVED, _('Resolved')),
    ]
    
    level = models.CharField(_('level'), max_length=20, choices=LEVEL_CHOICES)
    title = models.CharField(_('title'), max_length=255)
    message = models.TextField(_('message'))
    source = models.CharField(_('source'), max_length=255)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    
    # Alert details
    acknowledged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(_('acknowledged at'), null=True, blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')
    resolved_at = models.DateTimeField(_('resolved at'), null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('alert')
        verbose_name_plural = _('alerts')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_level_display()} - {self.title}"
