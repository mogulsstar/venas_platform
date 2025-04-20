"""
Models for the help_center app.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class HelpCategory(models.Model):
    """
    Model representing a help category.
    """
    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    icon = models.CharField(_('icon'), max_length=50, blank=True, help_text=_('CSS class for the icon'))
    order = models.PositiveIntegerField(_('order'), default=0, help_text=_('Order in which the category appears'))
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('help category')
        verbose_name_plural = _('help categories')
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class HelpArticle(models.Model):
    """
    Model representing a help article.
    """
    
    title = models.CharField(_('title'), max_length=255)
    content = models.TextField(_('content'))
    category = models.ForeignKey(HelpCategory, on_delete=models.CASCADE, related_name='articles')
    
    # Article metadata
    is_published = models.BooleanField(_('is published'), default=True)
    is_featured = models.BooleanField(_('is featured'), default=False)
    order = models.PositiveIntegerField(_('order'), default=0, help_text=_('Order in which the article appears within its category'))
    
    # SEO fields
    slug = models.SlugField(_('slug'), max_length=255, unique=True)
    meta_description = models.CharField(_('meta description'), max_length=255, blank=True)
    keywords = models.CharField(_('keywords'), max_length=255, blank=True)
    
    # Authorship
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_help_articles')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='updated_help_articles')
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('help article')
        verbose_name_plural = _('help articles')
        ordering = ['category', 'order', 'title']
    
    def __str__(self):
        return self.title


class FAQ(models.Model):
    """
    Model representing a frequently asked question.
    """
    
    question = models.CharField(_('question'), max_length=255)
    answer = models.TextField(_('answer'))
    category = models.ForeignKey(HelpCategory, on_delete=models.CASCADE, related_name='faqs')
    
    # FAQ metadata
    is_published = models.BooleanField(_('is published'), default=True)
    order = models.PositiveIntegerField(_('order'), default=0, help_text=_('Order in which the FAQ appears within its category'))
    
    # Authorship
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_faqs')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='updated_faqs')
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
        ordering = ['category', 'order', 'question']
    
    def __str__(self):
        return self.question


class UserFeedback(models.Model):
    """
    Model representing user feedback on help content.
    """
    
    # Content type choices
    CONTENT_ARTICLE = 'article'
    CONTENT_FAQ = 'faq'
    
    CONTENT_CHOICES = [
        (CONTENT_ARTICLE, _('Article')),
        (CONTENT_FAQ, _('FAQ')),
    ]
    
    # Feedback type choices
    TYPE_HELPFUL = 'helpful'
    TYPE_NOT_HELPFUL = 'not_helpful'
    TYPE_SUGGESTION = 'suggestion'
    TYPE_ERROR = 'error'
    
    TYPE_CHOICES = [
        (TYPE_HELPFUL, _('Helpful')),
        (TYPE_NOT_HELPFUL, _('Not Helpful')),
        (TYPE_SUGGESTION, _('Suggestion')),
        (TYPE_ERROR, _('Error Report')),
    ]
    
    content_type = models.CharField(_('content type'), max_length=20, choices=CONTENT_CHOICES)
    article = models.ForeignKey(HelpArticle, on_delete=models.CASCADE, null=True, blank=True, related_name='feedback')
    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE, null=True, blank=True, related_name='feedback')
    
    # Feedback details
    feedback_type = models.CharField(_('feedback type'), max_length=20, choices=TYPE_CHOICES)
    comment = models.TextField(_('comment'), blank=True)
    
    # User information
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='help_feedback')
    email = models.EmailField(_('email'), blank=True)
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('user feedback')
        verbose_name_plural = _('user feedback')
        ordering = ['-created_at']
    
    def __str__(self):
        if self.content_type == self.CONTENT_ARTICLE and self.article:
            return f"{self.get_feedback_type_display()} - {self.article.title}"
        elif self.content_type == self.CONTENT_FAQ and self.faq:
            return f"{self.get_feedback_type_display()} - {self.faq.question}"
        return f"{self.get_feedback_type_display()} - {self.created_at}"
    
    def clean(self):
        """
        Validate that either article or faq is set, but not both.
        """
        from django.core.exceptions import ValidationError
        
        if self.content_type == self.CONTENT_ARTICLE and not self.article:
            raise ValidationError(_('Article must be set for article feedback.'))
        elif self.content_type == self.CONTENT_FAQ and not self.faq:
            raise ValidationError(_('FAQ must be set for FAQ feedback.'))


class SupportRequest(models.Model):
    """
    Model representing a support request.
    """
    
    # Status choices
    STATUS_OPEN = 'open'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_RESOLVED = 'resolved'
    STATUS_CLOSED = 'closed'
    
    STATUS_CHOICES = [
        (STATUS_OPEN, _('Open')),
        (STATUS_IN_PROGRESS, _('In Progress')),
        (STATUS_RESOLVED, _('Resolved')),
        (STATUS_CLOSED, _('Closed')),
    ]
    
    # Priority choices
    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_URGENT = 'urgent'
    
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, _('Low')),
        (PRIORITY_MEDIUM, _('Medium')),
        (PRIORITY_HIGH, _('High')),
        (PRIORITY_URGENT, _('Urgent')),
    ]
    
    subject = models.CharField(_('subject'), max_length=255)
    description = models.TextField(_('description'))
    
    # Request details
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    priority = models.CharField(_('priority'), max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    category = models.ForeignKey(HelpCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='support_requests')
    
    # User information
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_requests')
    
    # Assignment
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_support_requests')
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    resolved_at = models.DateTimeField(_('resolved at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('support request')
        verbose_name_plural = _('support requests')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} - {self.get_status_display()}"


class SupportResponse(models.Model):
    """
    Model representing a response to a support request.
    """
    
    request = models.ForeignKey(SupportRequest, on_delete=models.CASCADE, related_name='responses')
    content = models.TextField(_('content'))
    
    # Response metadata
    is_internal = models.BooleanField(_('is internal'), default=False, help_text=_('If true, this response is only visible to staff'))
    
    # User information
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_responses')
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('support response')
        verbose_name_plural = _('support responses')
        ordering = ['request', 'created_at']
    
    def __str__(self):
        return f"Response to {self.request} by {self.user}"
