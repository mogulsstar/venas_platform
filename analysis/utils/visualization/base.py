"""
Base class for data visualizations.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, Optional, List, Union, Tuple


class Visualization(ABC):
    """
    Abstract base class for data visualizations.
    
    This class defines the interface for all data visualizations.
    Each specific visualization type should inherit from this class
    and implement the required methods.
    """
    
    def __init__(self, title: str = "", description: str = "", **kwargs):
        """
        Initialize the visualization.
        
        Parameters
        ----------
        title : str, optional
            Title of the visualization
        description : str, optional
            Description of the visualization
        **kwargs : dict
            Additional visualization-specific parameters
        """
        self.title = title
        self.description = description
        self.kwargs = kwargs
        self.metadata = {}
    
    @abstractmethod
    def generate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate the visualization.
        
        Parameters
        ----------
        data : pd.DataFrame
            The data to visualize
            
        Returns
        -------
        Dict[str, Any]
            Visualization data in a format suitable for frontend rendering
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the visualization.
        
        Returns
        -------
        Dict[str, Any]
            Metadata about the visualization
        """
        return {
            'title': self.title,
            'description': self.description,
            **self.metadata
        }
    
    @abstractmethod
    def get_type(self) -> str:
        """
        Get the type of visualization.
        
        Returns
        -------
        str
            Type of visualization
        """
        pass
