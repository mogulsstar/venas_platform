"""
Base class for data cleaning operations.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, Optional, List, Union


class DataCleaner(ABC):
    """
    Abstract base class for data cleaning operations.
    
    This class defines the interface for all data cleaning operations.
    Each specific cleaning operation should inherit from this class
    and implement the required methods.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the data cleaner.
        
        Parameters
        ----------
        **kwargs : dict
            Additional cleaner-specific parameters
        """
        self.kwargs = kwargs
        self.metadata = {}
    
    @abstractmethod
    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the data.
        
        Parameters
        ----------
        data : pd.DataFrame
            The data to clean
            
        Returns
        -------
        pd.DataFrame
            The cleaned data
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the cleaning operation.
        
        Returns
        -------
        Dict[str, Any]
            Metadata about the cleaning operation
        """
        return self.metadata
    
    def validate(self, data: pd.DataFrame) -> bool:
        """
        Validate that the data can be cleaned by this cleaner.
        
        Parameters
        ----------
        data : pd.DataFrame
            The data to validate
            
        Returns
        -------
        bool
            True if the data can be cleaned, False otherwise
        """
        try:
            self.clean(data)
            return True
        except Exception:
            return False
