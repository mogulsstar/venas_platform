"""
Models for the analysis app.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from projects.models import Project
from testcases.models import TestCase


class AnalysisTemplate(models.Model):
    """
    Model representing a template for data analysis.
    """
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    
    # Template configuration
    pipeline_config = models.JSONField(_('pipeline configuration'), default=dict)
    is_global = models.BooleanField(_('is global'), default=False, help_text=_('If true, this template is available to all users'))
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_analysis_templates')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('analysis template')
        verbose_name_plural = _('analysis templates')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DataSource(models.Model):
    """
    Model representing a data source for analysis.
    """
    
    # Source type choices
    TYPE_FILE = 'file'
    TYPE_DATABASE = 'database'
    TYPE_API = 'api'
    
    TYPE_CHOICES = [
        (TYPE_FILE, _('File')),
        (TYPE_DATABASE, _('Database')),
        (TYPE_API, _('API')),
    ]
    
    # File format choices
    FORMAT_CSV = 'csv'
    FORMAT_EXCEL = 'excel'
    FORMAT_JSON = 'json'
    FORMAT_XML = 'xml'
    FORMAT_BLF = 'blf'
    FORMAT_H5 = 'h5'
    FORMAT_MDF = 'mdf'
    FORMAT_MAT = 'mat'
    
    FORMAT_CHOICES = [
        (FORMAT_CSV, _('CSV')),
        (FORMAT_EXCEL, _('Excel')),
        (FORMAT_JSON, _('JSON')),
        (FORMAT_XML, _('XML')),
        (FORMAT_BLF, _('BLF')),
        (FORMAT_H5, _('H5')),
        (FORMAT_MDF, _('MDF')),
        (FORMAT_MAT, _('MAT')),
    ]
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    
    # Source configuration
    source_type = models.CharField(_('source type'), max_length=20, choices=TYPE_CHOICES)
    file_format = models.CharField(_('file format'), max_length=20, choices=FORMAT_CHOICES, null=True, blank=True)
    file = models.FileField(_('file'), upload_to='data_sources/', null=True, blank=True)
    connection_string = models.CharField(_('connection string'), max_length=255, blank=True)
    api_url = models.URLField(_('API URL'), blank=True)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_data_sources')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('data source')
        verbose_name_plural = _('data sources')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class AnalysisTask(models.Model):
    """
    Model representing an analysis task.
    """
    
    # Analysis type choices
    TYPE_LONGITUDINAL = 'longitudinal'
    TYPE_HORIZONTAL = 'horizontal'
    
    TYPE_CHOICES = [
        (TYPE_LONGITUDINAL, _('Longitudinal')),
        (TYPE_HORIZONTAL, _('Horizontal')),
    ]
    
    # Status choices
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending')),
        (STATUS_PROCESSING, _('Processing')),
        (STATUS_COMPLETED, _('Completed')),
        (STATUS_FAILED, _('Failed')),
    ]
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    
    # Task configuration
    analysis_type = models.CharField(_('analysis type'), max_length=20, choices=TYPE_CHOICES)
    template = models.ForeignKey(AnalysisTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    test_case = models.ForeignKey(TestCase, on_delete=models.SET_NULL, null=True, blank=True, related_name='analysis_tasks')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='analysis_tasks')
    
    # Task status
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    error_message = models.TextField(_('error message'), blank=True)
    
    # Task results
    results = models.JSONField(_('results'), default=dict, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_analysis_tasks')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    
    # Performance tracking
    execution_time = models.FloatField(_('execution time'), null=True, blank=True, help_text=_('Execution time in seconds'))
    
    class Meta:
        verbose_name = _('analysis task')
        verbose_name_plural = _('analysis tasks')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class AnalysisTaskDataSource(models.Model):
    """
    Model representing a data source for an analysis task.
    """
    
    task = models.ForeignKey(AnalysisTask, on_delete=models.CASCADE, related_name='data_sources')
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='tasks')
    
    # Metadata
    added_at = models.DateTimeField(_('added at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('analysis task data source')
        verbose_name_plural = _('analysis task data sources')
        ordering = ['-added_at']
        unique_together = ('task', 'data_source')
    
    def __str__(self):
        return f"{self.task} - {self.data_source}"


class AnalysisReport(models.Model):
    """
    Model representing an analysis report.
    """
    
    # Report format choices
    FORMAT_PDF = 'pdf'
    FORMAT_EXCEL = 'excel'
    FORMAT_PPT = 'ppt'
    FORMAT_HTML = 'html'
    FORMAT_MARKDOWN = 'markdown'
    
    FORMAT_CHOICES = [
        (FORMAT_PDF, _('PDF')),
        (FORMAT_EXCEL, _('Excel')),
        (FORMAT_PPT, _('PowerPoint')),
        (FORMAT_HTML, _('HTML')),
        (FORMAT_MARKDOWN, _('Markdown')),
    ]
    
    task = models.ForeignKey(AnalysisTask, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    
    # Report content
    content = models.JSONField(_('content'), default=dict)
    format = models.CharField(_('format'), max_length=20, choices=FORMAT_CHOICES)
    file = models.FileField(_('file'), upload_to='analysis_reports/', null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_analysis_reports')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('analysis report')
        verbose_name_plural = _('analysis reports')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class DataCleaningRule(models.Model):
    """
    Model representing a data cleaning rule.
    """
    
    # Rule type choices
    TYPE_GLOBAL = 'global'
    TYPE_LOCAL = 'local'
    
    TYPE_CHOICES = [
        (TYPE_GLOBAL, _('Global')),
        (TYPE_LOCAL, _('Local')),
    ]
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    
    # Rule configuration
    rule_type = models.CharField(_('rule type'), max_length=20, choices=TYPE_CHOICES, default=TYPE_GLOBAL)
    configuration = models.JSONField(_('configuration'), default=dict)
    
    # Related objects
    task = models.ForeignKey(AnalysisTask, on_delete=models.CASCADE, related_name='cleaning_rules')
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_cleaning_rules')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('data cleaning rule')
        verbose_name_plural = _('data cleaning rules')
        ordering = ['task', 'rule_type', 'name']
    
    def __str__(self):
        return f"{self.task} - {self.name}"


class ValidationRule(models.Model):
    """
    Model representing a validation rule.
    """
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    
    # Rule configuration
    expression = models.TextField(_('expression'))
    
    # Related objects
    task = models.ForeignKey(AnalysisTask, on_delete=models.CASCADE, related_name='validation_rules')
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_validation_rules')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('validation rule')
        verbose_name_plural = _('validation rules')
        ordering = ['task', 'name']
    
    def __str__(self):
        return f"{self.task} - {self.name}"


class Visualization(models.Model):
    """
    Model representing a visualization.
    """
    
    # Visualization type choices
    TYPE_LINE = 'line'
    TYPE_BAR = 'bar'
    TYPE_SCATTER = 'scatter'
    TYPE_PIE = 'pie'
    TYPE_HEATMAP = 'heatmap'
    TYPE_BOX = 'box'
    TYPE_HISTOGRAM = 'histogram'
    
    TYPE_CHOICES = [
        (TYPE_LINE, _('Line Chart')),
        (TYPE_BAR, _('Bar Chart')),
        (TYPE_SCATTER, _('Scatter Plot')),
        (TYPE_PIE, _('Pie Chart')),
        (TYPE_HEATMAP, _('Heatmap')),
        (TYPE_BOX, _('Box Plot')),
        (TYPE_HISTOGRAM, _('Histogram')),
    ]
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    
    # Visualization configuration
    visualization_type = models.CharField(_('visualization type'), max_length=20, choices=TYPE_CHOICES)
    configuration = models.JSONField(_('configuration'), default=dict)
    
    # Related objects
    task = models.ForeignKey(AnalysisTask, on_delete=models.CASCADE, related_name='visualizations')
    
    # Visualization data
    data = models.JSONField(_('data'), default=dict)
    image = models.ImageField(_('image'), upload_to='visualizations/', null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_visualizations')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('visualization')
        verbose_name_plural = _('visualizations')
        ordering = ['task', 'name']
    
    def __str__(self):
        return f"{self.task} - {self.name}"
