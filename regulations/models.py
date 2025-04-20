"""
Models for the regulations app.
"""

import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Country(models.Model):
    """
    Model representing a country.
    """
    
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=10, unique=True)
    flag = models.ImageField(_('flag'), upload_to='country_flags/', blank=True, null=True)
    
    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('countries')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Region(models.Model):
    """
    Model representing a region within a country.
    """
    
    name = models.CharField(_('name'), max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='regions')
    
    class Meta:
        verbose_name = _('region')
        verbose_name_plural = _('regions')
        ordering = ['country', 'name']
        unique_together = ('name', 'country')
    
    def __str__(self):
        return f"{self.name} ({self.country.name})"


class RegulationCategory(models.Model):
    """
    Model representing a category of regulations.
    """
    
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    class Meta:
        verbose_name = _('regulation category')
        verbose_name_plural = _('regulation categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class RegulationDocument(models.Model):
    """
    Model representing a regulation document.
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
    
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='regulations')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True, related_name='regulations')
    category = models.ForeignKey(RegulationCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='regulations')
    
    # Document metadata
    document_number = models.CharField(_('document number'), max_length=100, blank=True)
    version = models.CharField(_('version'), max_length=50, blank=True)
    publication_date = models.DateField(_('publication date'), null=True, blank=True)
    effective_date = models.DateField(_('effective date'), null=True, blank=True)
    expiration_date = models.DateField(_('expiration date'), null=True, blank=True)
    
    # Document file
    original_file = models.FileField(_('original file'), upload_to='regulation_documents/')
    file_type = models.CharField(_('file type'), max_length=10, default='pdf')
    
    # Status and workflow
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_regulations')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    published_at = models.DateTimeField(_('published at'), null=True, blank=True)
    
    # Segmentation and processing status
    is_processed = models.BooleanField(_('is processed'), default=False)
    processing_errors = models.TextField(_('processing errors'), blank=True)
    
    # Versioning
    previous_version = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='next_versions')
    
    class Meta:
        verbose_name = _('regulation document')
        verbose_name_plural = _('regulation documents')
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.title
    
    @property
    def file_extension(self):
        """
        Get the file extension of the original file.
        """
        _, extension = os.path.splitext(self.original_file.name)
        return extension.lower()
    
    @property
    def is_draft(self):
        """
        Check if the document is in draft status.
        """
        return self.status == self.STATUS_DRAFT
    
    @property
    def is_under_review(self):
        """
        Check if the document is under review.
        """
        return self.status == self.STATUS_REVIEW
    
    @property
    def is_published(self):
        """
        Check if the document is published.
        """
        return self.status == self.STATUS_PUBLISHED
    
    @property
    def is_archived(self):
        """
        Check if the document is archived.
        """
        return self.status == self.STATUS_ARCHIVED


class RegulationSegment(models.Model):
    """
    Model representing a segment of a regulation document.
    """
    
    document = models.ForeignKey(RegulationDocument, on_delete=models.CASCADE, related_name='segments')
    title = models.CharField(_('title'), max_length=255, blank=True)
    content = models.TextField(_('content'))
    
    # Segment position in document
    page_number = models.PositiveIntegerField(_('page number'))
    order = models.PositiveIntegerField(_('order'))
    
    # Segment type
    is_heading = models.BooleanField(_('is heading'), default=False)
    is_table = models.BooleanField(_('is table'), default=False)
    is_figure = models.BooleanField(_('is figure'), default=False)
    
    # Segment metadata
    section_number = models.CharField(_('section number'), max_length=50, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    # Translations
    translations = models.JSONField(_('translations'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('regulation segment')
        verbose_name_plural = _('regulation segments')
        ordering = ['document', 'page_number', 'order']
        unique_together = ('document', 'page_number', 'order')
    
    def __str__(self):
        return f"{self.document.title} - Page {self.page_number} - {self.title or 'Segment'}"
    
    def get_translation(self, language_code):
        """
        Get the translation for the specified language code.
        
        Parameters
        ----------
        language_code : str
            The language code to get the translation for
            
        Returns
        -------
        str
            The translated content or None if not available
        """
        return self.translations.get(language_code)


class RegulationInterpretation(models.Model):
    """
    Model representing an interpretation of a regulation segment.
    """
    
    # Status choices
    STATUS_DRAFT = 'draft'
    STATUS_REVIEW = 'review'
    STATUS_PUBLISHED = 'published'
    
    STATUS_CHOICES = [
        (STATUS_DRAFT, _('Draft')),
        (STATUS_REVIEW, _('Under Review')),
        (STATUS_PUBLISHED, _('Published')),
    ]
    
    segment = models.ForeignKey(RegulationSegment, on_delete=models.CASCADE, related_name='interpretations')
    content = models.TextField(_('content'))
    
    # Interpretation metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_interpretations')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    # Status and workflow
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_interpretations')
    reviewed_at = models.DateTimeField(_('reviewed at'), null=True, blank=True)
    
    # AI-generated flag
    is_ai_generated = models.BooleanField(_('is AI generated'), default=False)
    
    # Translations
    translations = models.JSONField(_('translations'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('regulation interpretation')
        verbose_name_plural = _('regulation interpretations')
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Interpretation of {self.segment}"
    
    def get_translation(self, language_code):
        """
        Get the translation for the specified language code.
        
        Parameters
        ----------
        language_code : str
            The language code to get the translation for
            
        Returns
        -------
        str
            The translated content or None if not available
        """
        return self.translations.get(language_code)


class RegulationReview(models.Model):
    """
    Model representing a review of a regulation document or interpretation.
    """
    
    # Content type choices
    CONTENT_DOCUMENT = 'document'
    CONTENT_INTERPRETATION = 'interpretation'
    
    CONTENT_CHOICES = [
        (CONTENT_DOCUMENT, _('Document')),
        (CONTENT_INTERPRETATION, _('Interpretation')),
    ]
    
    # Status choices
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending')),
        (STATUS_APPROVED, _('Approved')),
        (STATUS_REJECTED, _('Rejected')),
    ]
    
    content_type = models.CharField(_('content type'), max_length=20, choices=CONTENT_CHOICES)
    document = models.ForeignKey(RegulationDocument, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    interpretation = models.ForeignKey(RegulationInterpretation, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    
    # Review metadata
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='regulation_reviews')
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    comments = models.TextField(_('comments'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('regulation review')
        verbose_name_plural = _('regulation reviews')
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.content_type == self.CONTENT_DOCUMENT:
            return f"Review of document: {self.document}"
        else:
            return f"Review of interpretation: {self.interpretation}"
    
    def clean(self):
        """
        Validate that either document or interpretation is set, but not both.
        """
        from django.core.exceptions import ValidationError
        
        if self.content_type == self.CONTENT_DOCUMENT and not self.document:
            raise ValidationError(_('Document must be set for document reviews.'))
        elif self.content_type == self.CONTENT_INTERPRETATION and not self.interpretation:
            raise ValidationError(_('Interpretation must be set for interpretation reviews.'))


class RegulationRelationship(models.Model):
    """
    Model representing a relationship between regulation segments.
    """
    
    # Relationship type choices
    TYPE_SIMILAR = 'similar'
    TYPE_REFERENCES = 'references'
    TYPE_SUPERSEDES = 'supersedes'
    TYPE_IMPLEMENTS = 'implements'
    
    TYPE_CHOICES = [
        (TYPE_SIMILAR, _('Similar')),
        (TYPE_REFERENCES, _('References')),
        (TYPE_SUPERSEDES, _('Supersedes')),
        (TYPE_IMPLEMENTS, _('Implements')),
    ]
    
    source = models.ForeignKey(RegulationSegment, on_delete=models.CASCADE, related_name='outgoing_relationships')
    target = models.ForeignKey(RegulationSegment, on_delete=models.CASCADE, related_name='incoming_relationships')
    relationship_type = models.CharField(_('relationship type'), max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(_('description'), blank=True)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_relationships')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    # Similarity score (for similar relationships)
    similarity_score = models.FloatField(_('similarity score'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('regulation relationship')
        verbose_name_plural = _('regulation relationships')
        ordering = ['-created_at']
        unique_together = ('source', 'target', 'relationship_type')
    
    def __str__(self):
        return f"{self.source} {self.get_relationship_type_display()} {self.target}"
