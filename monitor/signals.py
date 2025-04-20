"""
Signals for the monitor app.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import SystemMetric, SystemLog, UserRequest, TaskExecution, Alert
