"""
Celery tasks for the regulations app.
"""

import os
import logging
from celery import shared_task
from django.conf import settings
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


@shared_task
def process_regulation_document(document_id):
    """
    Process a regulation document to extract segments.

    Parameters
    ----------
    document_id : int
        The ID of the document to process
    """
    from .services import process_pdf_document

    # Use the PDF processor service to process the document
    return process_pdf_document(document_id)


@shared_task
def batch_process_regulation_documents(document_ids):
    """
    Process multiple regulation documents to extract segments.

    Parameters
    ----------
    document_ids : list
        List of document IDs to process
    """
    from .services import batch_process_pdf_documents

    # Use the PDF processor service to process the documents
    return batch_process_pdf_documents(document_ids)


@shared_task
def translate_regulation_document(document_id, target_lang):
    """
    Translate a regulation document to the target language.

    Parameters
    ----------
    document_id : int
        The ID of the document to translate
    target_lang : str
        The target language code (e.g., 'en', 'zh', 'de')
    """
    from .services import translate_document

    # Use the translation service to translate the document
    return translate_document(document_id, target_lang)
