"""
Models for the projects app.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from regulations.models import RegulationDocument, RegulationSegment, RegulationInterpretation
from testcases.models import TestCase


class ProjectType(models.Model):
    """
    Model representing a type of project.
    """
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    
    class Meta:
        verbose_name = _('project type')
        verbose_name_plural = _('project types')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Project(models.Model):
    """
    Model representing a project.
    """
    
    # Status choices
    STATUS_PLANNING = 'planning'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_ON_HOLD = 'on_hold'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_PLANNING, _('Planning')),
        (STATUS_IN_PROGRESS, _('In Progress')),
        (STATUS_COMPLETED, _('Completed')),
        (STATUS_ON_HOLD, _('On Hold')),
        (STATUS_CANCELLED, _('Cancelled')),
    ]
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    types = models.ManyToManyField(ProjectType, related_name='projects')
    
    # Parent project
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subprojects')
    
    # Status and timeline
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNING)
    start_date = models.DateField(_('start date'), null=True, blank=True)
    end_date = models.DateField(_('end date'), null=True, blank=True)
    progress = models.PositiveIntegerField(_('progress'), default=0, help_text=_('Progress in percentage (0-100)'))
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_projects')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def is_main_project(self):
        """
        Check if this is a main project (not a subproject).
        """
        return self.parent is None
    
    @property
    def is_subproject(self):
        """
        Check if this is a subproject.
        """
        return self.parent is not None


class ProjectMember(models.Model):
    """
    Model representing a member of a project.
    """
    
    # Role choices
    ROLE_OWNER = 'owner'
    ROLE_EDITOR = 'editor'
    ROLE_OBSERVER = 'observer'
    
    ROLE_CHOICES = [
        (ROLE_OWNER, _('Owner')),
        (ROLE_EDITOR, _('Editor')),
        (ROLE_OBSERVER, _('Observer')),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(_('role'), max_length=20, choices=ROLE_CHOICES, default=ROLE_OBSERVER)
    
    # Metadata
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='added_project_members')
    added_at = models.DateTimeField(_('added at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('project member')
        verbose_name_plural = _('project members')
        ordering = ['project', 'role', 'user']
        unique_together = ('project', 'user')
    
    def __str__(self):
        return f"{self.user} - {self.get_role_display()} in {self.project}"
    
    @property
    def is_owner(self):
        """
        Check if the member is an owner.
        """
        return self.role == self.ROLE_OWNER
    
    @property
    def is_editor(self):
        """
        Check if the member is an editor.
        """
        return self.role == self.ROLE_EDITOR
    
    @property
    def is_observer(self):
        """
        Check if the member is an observer.
        """
        return self.role == self.ROLE_OBSERVER


class ProjectRegulation(models.Model):
    """
    Model representing a regulation associated with a project.
    """
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='regulations')
    document = models.ForeignKey(RegulationDocument, on_delete=models.CASCADE, related_name='projects')
    segment = models.ForeignKey(RegulationSegment, on_delete=models.CASCADE, null=True, blank=True, related_name='projects')
    interpretation = models.ForeignKey(RegulationInterpretation, on_delete=models.CASCADE, null=True, blank=True, related_name='projects')
    
    # Metadata
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='added_project_regulations')
    added_at = models.DateTimeField(_('added at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('project regulation')
        verbose_name_plural = _('project regulations')
        ordering = ['project', '-added_at']
    
    def __str__(self):
        if self.segment:
            return f"{self.project} - {self.document} - Segment {self.segment.id}"
        elif self.interpretation:
            return f"{self.project} - {self.document} - Interpretation {self.interpretation.id}"
        return f"{self.project} - {self.document}"


class ProjectTestCase(models.Model):
    """
    Model representing a test case associated with a project.
    """
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='test_cases')
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='projects')
    
    # Metadata
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='added_project_test_cases')
    added_at = models.DateTimeField(_('added at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('project test case')
        verbose_name_plural = _('project test cases')
        ordering = ['project', '-added_at']
        unique_together = ('project', 'test_case')
    
    def __str__(self):
        return f"{self.project} - {self.test_case}"


class ProjectNote(models.Model):
    """
    Model representing a note associated with a project.
    """
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(_('title'), max_length=255)
    content = models.TextField(_('content'))
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_project_notes')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('project note')
        verbose_name_plural = _('project notes')
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.project} - {self.title}"


class ProjectAttachment(models.Model):
    """
    Model representing an attachment to a project.
    """
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='attachments')
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    file = models.FileField(_('file'), upload_to='project_attachments/')
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_project_attachments')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('project attachment')
        verbose_name_plural = _('project attachments')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project} - {self.name}"
