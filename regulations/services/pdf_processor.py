"""
PDF processing service for regulations.
"""

import os
import pdfplumber
import re
import uuid
import json
from typing import Dict, List, Tuple, Any, Optional
import logging
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from celery import shared_task

from regulations.models import RegulationDocument, RegulationSegment

logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    Service for processing PDF documents.
    
    This class provides methods for extracting text from PDFs,
    segmenting the content into meaningful sections, and
    storing the results in the database.
    """
    
    def __init__(self, storage_path=None, temp_path=None):
        """
        Initialize the PDF processor.
        
        Parameters
        ----------
        storage_path : str, optional
            Path to store processed PDFs
        temp_path : str, optional
            Path for temporary files during processing
        """
        self.storage_path = storage_path or settings.PDF_STORAGE_PATH
        self.temp_path = temp_path or settings.PDF_TEMP_PATH
        
        # Create directories if they don't exist
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(self.temp_path, exist_ok=True)
    
    def extract_text(self, pdf_file_path: str) -> Dict[int, str]:
        """
        Extract text from a PDF file.
        
        Parameters
        ----------
        pdf_file_path : str
            Path to the PDF file
            
        Returns
        -------
        Dict[int, str]
            Dictionary mapping page numbers to extracted text
        """
        extracted_text = {}
        
        try:
            with pdfplumber.open(pdf_file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        extracted_text[i + 1] = text  # 1-based page numbering
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_file_path}: {str(e)}")
            raise
        
        return extracted_text
    
    def segment_content(self, text_by_page: Dict[int, str]) -> List[Dict[str, Any]]:
        """
        Segment PDF content into meaningful sections.
        
        Parameters
        ----------
        text_by_page : Dict[int, str]
            Dictionary mapping page numbers to extracted text
            
        Returns
        -------
        List[Dict[str, Any]]
            List of segments with metadata
        """
        segments = []
        
        # Combine all text for initial processing
        all_text = "\n\n".join([f"--- Page {page} ---\n{text}" for page, text in sorted(text_by_page.items())])
        
        # Pattern for identifying potential section headers
        # This is a simplified approach - in a real system, you might use NLP or more complex rules
        header_pattern = re.compile(r'^(\d+\.[\d\.]*\s+[A-Z][^.!?]*|[A-Z][^.!?]*:)', re.MULTILINE)
        
        # Find all potential section headers
        headers = list(header_pattern.finditer(all_text))
        
        # Process each section
        for i in range(len(headers)):
            start = headers[i].start()
            end = headers[i+1].start() if i < len(headers) - 1 else len(all_text)
            
            section_text = all_text[start:end].strip()
            header_text = headers[i].group(0).strip()
            content_text = section_text[len(header_text):].strip()
            
            # Determine which pages this section spans
            section_start_pos = start
            section_end_pos = end
            pages = []
            
            current_pos = 0
            for page, text in sorted(text_by_page.items()):
                page_text = f"--- Page {page} ---\n{text}"
                page_start = current_pos
                page_end = current_pos + len(page_text)
                
                # Check if this page overlaps with the section
                if section_start_pos <= page_end and section_end_pos >= page_start:
                    pages.append(page)
                
                current_pos = page_end + 2  # +2 for the "\n\n" we added between pages
            
            # Create segment
            segment = {
                'id': str(uuid.uuid4()),
                'title': header_text,
                'content': content_text,
                'pages': pages,
                'type': self._determine_segment_type(header_text, content_text),
                'metadata': {
                    'word_count': len(content_text.split()),
                    'character_count': len(content_text)
                }
            }
            
            segments.append(segment)
        
        return segments
    
    def _determine_segment_type(self, header: str, content: str) -> str:
        """
        Determine the type of segment based on its content.
        
        Parameters
        ----------
        header : str
            Section header text
        content : str
            Section content text
            
        Returns
        -------
        str
            Segment type (e.g., 'definition', 'requirement', 'procedure', etc.)
        """
        # This is a simplified approach - in a real system, you might use ML classification
        lower_header = header.lower()
        lower_content = content.lower()
        
        if 'definition' in lower_header or 'terminology' in lower_header:
            return 'definition'
        elif 'requirement' in lower_header or 'shall' in lower_content:
            return 'requirement'
        elif 'procedure' in lower_header or 'steps' in lower_header:
            return 'procedure'
        elif 'note' in lower_header or 'example' in lower_header:
            return 'informative'
        else:
            return 'general'
    
    def process_document(self, document_id: int) -> bool:
        """
        Process a regulation document that has been uploaded.
        
        Parameters
        ----------
        document_id : int
            ID of the RegulationDocument to process
            
        Returns
        -------
        bool
            True if processing was successful, False otherwise
        """
        try:
            # Get the document
            document = RegulationDocument.objects.get(id=document_id)
            
            # Get the file path
            file_path = document.file.path
            
            # Extract text
            text_by_page = self.extract_text(file_path)
            
            # Segment content
            segments = self.segment_content(text_by_page)
            
            # Store segments in database
            for segment_data in segments:
                segment = RegulationSegment(
                    document=document,
                    title=segment_data['title'],
                    content=segment_data['content'],
                    segment_type=segment_data['type'],
                    pages=','.join(map(str, segment_data['pages'])),
                    metadata=segment_data['metadata']
                )
                segment.save()
            
            # Update document status
            document.is_processed = True
            document.save()
            
            return True
        
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {str(e)}")
            return False
    
    def batch_process_documents(self, document_ids: List[int]) -> Dict[int, bool]:
        """
        Process multiple regulation documents.
        
        Parameters
        ----------
        document_ids : List[int]
            List of RegulationDocument IDs to process
            
        Returns
        -------
        Dict[int, bool]
            Dictionary mapping document IDs to processing success status
        """
        results = {}
        
        for doc_id in document_ids:
            results[doc_id] = self.process_document(doc_id)
        
        return results


@shared_task
def process_pdf_document(document_id: int) -> bool:
    """
    Celery task to process a PDF document asynchronously.
    
    Parameters
    ----------
    document_id : int
        ID of the RegulationDocument to process
        
    Returns
    -------
    bool
        True if processing was successful, False otherwise
    """
    processor = PDFProcessor()
    return processor.process_document(document_id)


@shared_task
def batch_process_pdf_documents(document_ids: List[int]) -> Dict[int, bool]:
    """
    Celery task to process multiple PDF documents asynchronously.
    
    Parameters
    ----------
    document_ids : List[int]
        List of RegulationDocument IDs to process
        
    Returns
    -------
    Dict[int, bool]
        Dictionary mapping document IDs to processing success status
    """
    processor = PDFProcessor()
    return processor.batch_process_documents(document_ids)
