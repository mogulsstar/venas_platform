"""
Models for the testcases app.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from regulations.models import RegulationSegment, RegulationInterpretation


class TestSuite(models.Model):
    """
    Model representing a test suite, which is a collection of test clusters.
    """
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_test_suites')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('test suite')
        verbose_name_plural = _('test suites')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TestCluster(models.Model):
    """
    Model representing a test cluster, which is a collection of test cases.
    """
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    suite = models.ForeignKey(TestSuite, on_delete=models.CASCADE, related_name='clusters')
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_test_clusters')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('test cluster')
        verbose_name_plural = _('test clusters')
        ordering = ['suite', 'name']
    
    def __str__(self):
        return f"{self.suite.name} - {self.name}"


class TestCaseTemplate(models.Model):
    """
    Model representing a template for test cases.
    """
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    structure = models.JSONField(_('structure'), default=dict)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_test_case_templates')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('test case template')
        verbose_name_plural = _('test case templates')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TestCase(models.Model):
    """
    Model representing a test case.
    """
    
    # Status choices
    STATUS_DRAFT = 'draft'
    STATUS_REVIEW = 'review'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED = 'archived'
    
    STATUS_CHOICES = [
        (STATUS_DRAFT, _('Draft')),
        (STATUS_REVIEW, _('Under Review')),
        (STATUS_PUBLISHED, _('Published')),
        (STATUS_ARCHIVED, _('Archived')),
    ]
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    cluster = models.ForeignKey(TestCluster, on_delete=models.CASCADE, related_name='test_cases')
    template = models.ForeignKey(TestCaseTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='test_cases')
    
    # Content
    content = models.JSONField(_('content'), default=dict)
    
    # Related regulation
    regulation_segment = models.ForeignKey(RegulationSegment, on_delete=models.SET_NULL, null=True, blank=True, related_name='test_cases')
    regulation_interpretation = models.ForeignKey(RegulationInterpretation, on_delete=models.SET_NULL, null=True, blank=True, related_name='test_cases')
    
    # Status and workflow
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_test_cases')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    published_at = models.DateTimeField(_('published at'), null=True, blank=True)
    
    # AI-generated flag
    is_ai_generated = models.BooleanField(_('is AI generated'), default=False)
    
    # Versioning
    previous_version = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='next_versions')
    
    class Meta:
        verbose_name = _('test case')
        verbose_name_plural = _('test cases')
        ordering = ['cluster', 'name']
    
    def __str__(self):
        return f"{self.cluster} - {self.name}"
    
    @property
    def is_draft(self):
        """
        Check if the test case is in draft status.
        """
        return self.status == self.STATUS_DRAFT
    
    @property
    def is_under_review(self):
        """
        Check if the test case is under review.
        """
        return self.status == self.STATUS_REVIEW
    
    @property
    def is_published(self):
        """
        Check if the test case is published.
        """
        return self.status == self.STATUS_PUBLISHED
    
    @property
    def is_archived(self):
        """
        Check if the test case is archived.
        """
        return self.status == self.STATUS_ARCHIVED


class TestCaseReview(models.Model):
    """
    Model representing a review of a test case.
    """
    
    # Status choices
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending')),
        (STATUS_APPROVED, _('Approved')),
        (STATUS_REJECTED, _('Rejected')),
    ]
    
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='test_case_reviews')
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    comments = models.TextField(_('comments'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('test case review')
        verbose_name_plural = _('test case reviews')
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Review of {self.test_case} by {self.reviewer}"


class TestCaseAttachment(models.Model):
    """
    Model representing an attachment to a test case.
    """
    
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='attachments')
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    file = models.FileField(_('file'), upload_to='test_case_attachments/')
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_test_case_attachments')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('test case attachment')
        verbose_name_plural = _('test case attachments')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.test_case} - {self.name}"


class TestSignal(models.Model):
    """
    Model representing a signal definition for a test case.
    """
    
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='signals')
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    
    # Signal properties
    data_type = models.CharField(_('data type'), max_length=50)
    unit = models.CharField(_('unit'), max_length=50, blank=True)
    min_value = models.FloatField(_('minimum value'), null=True, blank=True)
    max_value = models.FloatField(_('maximum value'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('test signal')
        verbose_name_plural = _('test signals')
        ordering = ['test_case', 'name']
        unique_together = ('test_case', 'name')
    
    def __str__(self):
        return f"{self.test_case} - {self.name}"
