"""
Base classes for data validation.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """
    Result of a validation rule.
    
    Attributes
    ----------
    rule_id : str
        Identifier of the validation rule
    name : str
        Name of the validation rule
    description : str
        Description of the validation rule
    passed : bool
        Whether the validation passed
    details : Dict[str, Any]
        Additional details about the validation result
    failed_indices : List[int]
        Indices of rows that failed validation
    """
    rule_id: str
    name: str
    description: str
    passed: bool
    details: Dict[str, Any] = None
    failed_indices: List[int] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.details is None:
            self.details = {}
        if self.failed_indices is None:
            self.failed_indices = []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the validation result to a dictionary.
        
        Returns
        -------
        Dict[str, Any]
            Dictionary representation of the validation result
        """
        return {
            'rule_id': self.rule_id,
            'name': self.name,
            'description': self.description,
            'passed': self.passed,
            'details': self.details,
            'failed_count': len(self.failed_indices),
            'failed_indices': self.failed_indices[:10]  # Limit to first 10 for brevity
        }


class ValidationRule(ABC):
    """
    Abstract base class for validation rules.
    
    This class defines the interface for all validation rules.
    Each specific validation rule should inherit from this class
    and implement the required methods.
    """
    
    def __init__(self, rule_id: str, name: str, description: str, **kwargs):
        """
        Initialize the validation rule.
        
        Parameters
        ----------
        rule_id : str
            Identifier of the validation rule
        name : str
            Name of the validation rule
        description : str
            Description of the validation rule
        **kwargs : dict
            Additional rule-specific parameters
        """
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.kwargs = kwargs
    
    @abstractmethod
    def validate(self, data: pd.DataFrame) -> ValidationResult:
        """
        Validate the data.
        
        Parameters
        ----------
        data : pd.DataFrame
            The data to validate
            
        Returns
        -------
        ValidationResult
            Result of the validation
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the validation rule.
        
        Returns
        -------
        Dict[str, Any]
            Metadata about the validation rule
        """
        return {
            'rule_id': self.rule_id,
            'name': self.name,
            'description': self.description,
            **self.kwargs
        }
