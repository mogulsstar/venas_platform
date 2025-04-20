"""
Translation service for regulations.
"""

import os
import json
import hashlib
import requests
from typing import Dict, List, Optional, Any
import logging
from django.conf import settings
from django.core.cache import cache
from celery import shared_task

logger = logging.getLogger(__name__)

class TranslationService:
    """
    Service for translating regulation content.
    
    This class provides methods for translating text using various
    translation APIs and caching results to reduce API calls.
    """
    
    # Cache timeout (24 hours)
    CACHE_TIMEOUT = 86400
    
    def __init__(self, api_key=None, provider='google'):
        """
        Initialize the translation service.
        
        Parameters
        ----------
        api_key : str, optional
            API key for the translation service
        provider : str, optional
            Translation service provider ('google', 'deepl', etc.)
        """
        self.api_key = api_key or os.environ.get('TRANSLATION_API_KEY', '')
        self.provider = provider
        
        # Create cache directory if it doesn't exist
        cache_dir = os.path.join(settings.MEDIA_ROOT, 'translation_cache')
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_dir = cache_dir
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text from source language to target language.
        
        Parameters
        ----------
        text : str
            Text to translate
        source_lang : str
            Source language code (e.g., 'en', 'zh', 'de')
        target_lang : str
            Target language code (e.g., 'en', 'zh', 'de')
            
        Returns
        -------
        str
            Translated text
        """
        # Check if translation is in cache
        cache_key = self._get_cache_key(text, source_lang, target_lang)
        cached_translation = cache.get(cache_key)
        
        if cached_translation:
            logger.info(f"Using cached translation for {source_lang} to {target_lang}")
            return cached_translation
        
        # If not in cache, call translation API
        if self.provider == 'google':
            translated_text = self._translate_with_google(text, source_lang, target_lang)
        elif self.provider == 'deepl':
            translated_text = self._translate_with_deepl(text, source_lang, target_lang)
        else:
            raise ValueError(f"Unsupported translation provider: {self.provider}")
        
        # Cache the result
        cache.set(cache_key, translated_text, self.CACHE_TIMEOUT)
        
        # Also save to file cache as backup
        self._save_to_file_cache(cache_key, translated_text)
        
        return translated_text
    
    def _get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Generate a cache key for a translation request.
        
        Parameters
        ----------
        text : str
            Text to translate
        source_lang : str
            Source language code
        target_lang : str
            Target language code
            
        Returns
        -------
        str
            Cache key
        """
        # Create a hash of the text to use as part of the cache key
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"translation_{source_lang}_{target_lang}_{text_hash}"
    
    def _save_to_file_cache(self, cache_key: str, translated_text: str) -> None:
        """
        Save translation to file cache.
        
        Parameters
        ----------
        cache_key : str
            Cache key
        translated_text : str
            Translated text
        """
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({'translation': translated_text}, f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving translation to file cache: {str(e)}")
    
    def _translate_with_google(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text using Google Translate API.
        
        Parameters
        ----------
        text : str
            Text to translate
        source_lang : str
            Source language code
        target_lang : str
            Target language code
            
        Returns
        -------
        str
            Translated text
        """
        try:
            url = "https://translation.googleapis.com/language/translate/v2"
            params = {
                'q': text,
                'source': source_lang,
                'target': target_lang,
                'key': self.api_key
            }
            
            response = requests.post(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            return result['data']['translations'][0]['translatedText']
        
        except Exception as e:
            logger.error(f"Error translating with Google: {str(e)}")
            # Return original text if translation fails
            return text
    
    def _translate_with_deepl(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text using DeepL API.
        
        Parameters
        ----------
        text : str
            Text to translate
        source_lang : str
            Source language code
        target_lang : str
            Target language code
            
        Returns
        -------
        str
            Translated text
        """
        try:
            url = "https://api-free.deepl.com/v2/translate"
            params = {
                'text': text,
                'source_lang': source_lang.upper(),
                'target_lang': target_lang.upper(),
                'auth_key': self.api_key
            }
            
            response = requests.post(url, data=params)
            response.raise_for_status()
            
            result = response.json()
            return result['translations'][0]['text']
        
        except Exception as e:
            logger.error(f"Error translating with DeepL: {str(e)}")
            # Return original text if translation fails
            return text
    
    def translate_document_segments(self, document_id: int, target_lang: str) -> Dict[int, bool]:
        """
        Translate all segments of a regulation document.
        
        Parameters
        ----------
        document_id : int
            ID of the RegulationDocument
        target_lang : str
            Target language code
            
        Returns
        -------
        Dict[int, bool]
            Dictionary mapping segment IDs to translation success status
        """
        from regulations.models import RegulationDocument, RegulationSegment
        
        results = {}
        
        try:
            # Get the document
            document = RegulationDocument.objects.get(id=document_id)
            
            # Get the document's language
            source_lang = document.language
            
            # Get all segments
            segments = RegulationSegment.objects.filter(document=document)
            
            for segment in segments:
                try:
                    # Translate title
                    translated_title = self.translate_text(segment.title, source_lang, target_lang)
                    
                    # Translate content
                    translated_content = self.translate_text(segment.content, source_lang, target_lang)
                    
                    # Store translation in segment's translations field
                    translations = segment.translations or {}
                    translations[target_lang] = {
                        'title': translated_title,
                        'content': translated_content,
                        'is_verified': False  # Needs human verification
                    }
                    
                    segment.translations = translations
                    segment.save()
                    
                    results[segment.id] = True
                
                except Exception as e:
                    logger.error(f"Error translating segment {segment.id}: {str(e)}")
                    results[segment.id] = False
            
            return results
        
        except Exception as e:
            logger.error(f"Error translating document {document_id}: {str(e)}")
            return results


@shared_task
def translate_document(document_id: int, target_lang: str) -> Dict[int, bool]:
    """
    Celery task to translate a document asynchronously.
    
    Parameters
    ----------
    document_id : int
        ID of the RegulationDocument to translate
    target_lang : str
        Target language code
        
    Returns
    -------
    Dict[int, bool]
        Dictionary mapping segment IDs to translation success status
    """
    service = TranslationService()
    return service.translate_document_segments(document_id, target_lang)
