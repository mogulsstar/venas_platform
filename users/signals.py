"""
Signals for the users app.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import User, UserActivity


@receiver(post_save, sender=User)
def create_user_activity(sender, instance, created, **kwargs):
    """
    Create a user activity record when a user is created.
    """
    if created:
        UserActivity.objects.create(
            user=instance,
            action='user_created',
            action_time=timezone.now()
        )
