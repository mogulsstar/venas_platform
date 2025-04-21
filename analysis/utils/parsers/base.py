"""
Base parser class for data files.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, Optional, Union, List


class DataParser(ABC):
    """
    Abstract base class for data parsers.
    
    This class defines the interface for all data parsers.
    Each specific file format parser should inherit from this class
    and implement the required methods.
    """
    
    def __init__(self, file_path: str = None, file_obj: Any = None, **kwargs):
        """
        Initialize the parser.
        
        Parameters
        ----------
        file_path : str, optional
            Path to the data file
        file_obj : Any, optional
            File object if the file is already open
        **kwargs : dict
            Additional parser-specific parameters
        """
        self.file_path = file_path
        self.file_obj = file_obj
        self.kwargs = kwargs
        self.metadata = {}
    
    @abstractmethod
    def parse(self) -> pd.DataFrame:
        """
        Parse the data file and return a pandas DataFrame.
        
        Returns
        -------
        pd.DataFrame
            The parsed data
        
        Raises
        ------
        ValueError
            If the file cannot be parsed
        FileNotFoundError
            If the file does not exist
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata from the data file.
        
        Returns
        -------
        Dict[str, Any]
            Metadata extracted from the file
        """
        pass
    
    @classmethod
    def can_parse(cls, file_path: str) -> bool:
        """
        Check if this parser can parse the given file.
        
        Parameters
        ----------
        file_path : str
            Path to the data file
            
        Returns
        -------
        bool
            True if this parser can parse the file, False otherwise
        """
        return False
    
    def validate(self) -> bool:
        """
        Validate the data file.
        
        Returns
        -------
        bool
            True if the file is valid, False otherwise
        """
        try:
            self.parse()
            return True
        except Exception:
            return False
    
    def get_preview(self, rows: int = 5) -> pd.DataFrame:
        """
        Get a preview of the data.
        
        Parameters
        ----------
        rows : int, optional
            Number of rows to preview, by default 5
            
        Returns
        -------
        pd.DataFrame
            Preview of the data
        """
        try:
            df = self.parse()
            return df.head(rows)
        except Exception as e:
            raise ValueError(f"Could not generate preview: {str(e)}")
