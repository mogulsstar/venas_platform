"""
AI generator service for test cases.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from django.conf import settings
from celery import shared_task

from regulations.models import RegulationSegment
from testcases.models import TestCase, TestCaseTemplate

logger = logging.getLogger(__name__)

class AIGenerator:
    """
    Service for generating test cases using AI.
    
    This class provides methods for generating test cases based on
    regulation segments and templates using AI models.
    """
    
    def __init__(self, api_key=None, model=None):
        """
        Initialize the AI generator.
        
        Parameters
        ----------
        api_key : str, optional
            API key for the AI service
        model : str, optional
            AI model to use
        """
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY', '')
        self.model = model or settings.AI_MODEL
        
    def generate_test_case(self, regulation_text: str, template_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a test case based on regulation text and template.
        
        Parameters
        ----------
        regulation_text : str
            Regulation text to base the test case on
        template_structure : Dict[str, Any]
            Template structure to follow
            
        Returns
        -------
        Dict[str, Any]
            Generated test case content
        """
        # Construct the prompt
        prompt = self._construct_prompt(regulation_text, template_structure)
        
        # Call the AI API
        response = self._call_ai_api(prompt)
        
        # Parse the response
        return self._parse_response(response, template_structure)
    
    def _construct_prompt(self, regulation_text: str, template_structure: Dict[str, Any]) -> str:
        """
        Construct a prompt for the AI model.
        
        Parameters
        ----------
        regulation_text : str
            Regulation text to base the test case on
        template_structure : Dict[str, Any]
            Template structure to follow
            
        Returns
        -------
        str
            Prompt for the AI model
        """
        # Basic prompt structure
        prompt = f"""
        You are an expert in autonomous driving compliance testing. Your task is to create a detailed test case based on the following regulation:
        
        REGULATION:
        {regulation_text}
        
        Please create a test case that follows this template structure:
        {json.dumps(template_structure, indent=2)}
        
        Your test case should:
        1. Cover all requirements mentioned in the regulation
        2. Define clear test scenarios with specific parameters
        3. Include all necessary signals with appropriate ranges
        4. Consider edge cases and boundary conditions
        5. Be technically precise and implementable
        
        Format your response as a JSON object that matches the template structure.
        """
        
        return prompt.strip()
    
    def _call_ai_api(self, prompt: str) -> str:
        """
        Call the AI API with the prompt.
        
        Parameters
        ----------
        prompt : str
            Prompt for the AI model
            
        Returns
        -------
        str
            Response from the AI model
        """
        try:
            # OpenAI API call
            if 'gpt' in self.model.lower():
                return self._call_openai_api(prompt)
            # Add other AI providers as needed
            else:
                raise ValueError(f"Unsupported AI model: {self.model}")
        
        except Exception as e:
            logger.error(f"Error calling AI API: {str(e)}")
            raise
    
    def _call_openai_api(self, prompt: str) -> str:
        """
        Call the OpenAI API with the prompt.
        
        Parameters
        ----------
        prompt : str
            Prompt for the OpenAI model
            
        Returns
        -------
        str
            Response from the OpenAI model
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert in autonomous driving compliance testing."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 4000
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result['choices'][0]['message']['content']
        
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise
    
    def _parse_response(self, response: str, template_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the AI response into a test case structure.
        
        Parameters
        ----------
        response : str
            Response from the AI model
        template_structure : Dict[str, Any]
            Template structure to validate against
            
        Returns
        -------
        Dict[str, Any]
            Parsed test case content
        """
        try:
            # Extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in the response")
            
            json_str = response[json_start:json_end]
            content = json.loads(json_str)
            
            # Validate the content against the template structure
            # This is a simplified validation - in a real system, you would do more thorough validation
            if 'sections' not in content:
                content['sections'] = []
            
            if 'signals' not in content:
                content['signals'] = []
            
            return content
        
        except json.JSONDecodeError:
            logger.error(f"Error parsing AI response as JSON: {response}")
            # Return a basic structure if parsing fails
            return {
                "sections": [
                    {
                        "id": "error-section",
                        "type": "text",
                        "title": "Error Generating Test Case",
                        "content": "The AI model returned a response that could not be parsed. Please try again or create the test case manually."
                    }
                ],
                "signals": []
            }
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            raise
    
    def generate_test_case_from_segment(self, segment_id: int, template_id: int) -> Dict[str, Any]:
        """
        Generate a test case from a regulation segment and template.
        
        Parameters
        ----------
        segment_id : int
            ID of the RegulationSegment
        template_id : int
            ID of the TestCaseTemplate
            
        Returns
        -------
        Dict[str, Any]
            Generated test case content
        """
        try:
            # Get the segment
            segment = RegulationSegment.objects.get(id=segment_id)
            
            # Get the template
            template = TestCaseTemplate.objects.get(id=template_id)
            
            # Get the regulation text
            regulation_text = segment.content
            
            # Get the template structure
            template_structure = template.structure
            
            # Generate the test case
            return self.generate_test_case(regulation_text, template_structure)
        
        except (RegulationSegment.DoesNotExist, TestCaseTemplate.DoesNotExist) as e:
            logger.error(f"Error getting segment or template: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error generating test case: {str(e)}")
            raise


@shared_task
def generate_ai_test_case(test_case_id: int, segment_id: int, template_id: int) -> bool:
    """
    Celery task to generate a test case using AI.
    
    Parameters
    ----------
    test_case_id : int
        ID of the TestCase to update
    segment_id : int
        ID of the RegulationSegment to base the test case on
    template_id : int
        ID of the TestCaseTemplate to use
        
    Returns
    -------
    bool
        True if generation was successful, False otherwise
    """
    try:
        # Get the test case
        test_case = TestCase.objects.get(id=test_case_id)
        
        # Create the AI generator
        generator = AIGenerator()
        
        # Generate the test case content
        content = generator.generate_test_case_from_segment(segment_id, template_id)
        
        # Update the test case
        test_case.content = content
        test_case.is_ai_generated = True
        test_case.save()
        
        return True
    
    except Exception as e:
        logger.error(f"Error generating AI test case: {str(e)}")
        return False
