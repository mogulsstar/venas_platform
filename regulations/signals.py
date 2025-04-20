"""
Signals for the regulations app.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import RegulationDocument, RegulationSegment, RegulationInterpretation, RegulationReview
