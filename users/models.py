"""
User models for the VENAS platform.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom user manager for the VENAS platform.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        
        Parameters
        ----------
        email : str
            User email address
        password : str, optional
            User password
        **extra_fields : dict
            Additional fields for the user
            
        Returns
        -------
        User
            Created user instance
            
        Raises
        ------
        ValueError
            If email is not provided
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        
        Parameters
        ----------
        email : str
            User email address
        password : str, optional
            User password
        **extra_fields : dict
            Additional fields for the user
            
        Returns
        -------
        User
            Created superuser instance
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model for the VENAS platform.
    """
    
    # User roles
    ROLE_ADMIN = 'admin'
    ROLE_MANAGER = 'manager'
    ROLE_ANALYST = 'analyst'
    ROLE_VIEWER = 'viewer'
    
    ROLE_CHOICES = [
        (ROLE_ADMIN, _('Administrator')),
        (ROLE_MANAGER, _('Manager')),
        (ROLE_ANALYST, _('Analyst')),
        (ROLE_VIEWER, _('Viewer')),
    ]
    
    # Override username field to use email
    username = models.CharField(max_length=150, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    
    # Additional fields
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_VIEWER)
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    preferred_language = models.CharField(max_length=10, choices=[
        ('en', _('English')),
        ('zh-hans', _('Chinese')),
        ('de', _('German')),
    ], default='en')
    
    # Activity tracking
    last_activity = models.DateTimeField(null=True, blank=True)
    login_count = models.PositiveIntegerField(default=0)
    
    # Set email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    # Use custom manager
    objects = UserManager()
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    @property
    def is_admin(self):
        """Check if user is an administrator."""
        return self.role == self.ROLE_ADMIN
    
    @property
    def is_manager(self):
        """Check if user is a manager."""
        return self.role == self.ROLE_MANAGER
    
    @property
    def is_analyst(self):
        """Check if user is an analyst."""
        return self.role == self.ROLE_ANALYST
    
    @property
    def is_viewer(self):
        """Check if user is a viewer."""
        return self.role == self.ROLE_VIEWER


class UserActivity(models.Model):
    """
    Model to track user activity on the platform.
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=255)
    action_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    page = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = _('user activity')
        verbose_name_plural = _('user activities')
        ordering = ['-action_time']
    
    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.action_time}"


class UserPermission(models.Model):
    """
    Model to store custom user permissions.
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_permissions')
    module = models.CharField(max_length=100)
    can_view = models.BooleanField(default=False)
    can_add = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _('user permission')
        verbose_name_plural = _('user permissions')
        unique_together = ('user', 'module')
    
    def __str__(self):
        return f"{self.user.email} - {self.module}"
