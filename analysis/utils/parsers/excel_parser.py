"""
Excel file parser.
"""

import os
import pandas as pd
from typing import Dict, Any, Optional, List, Union

from .base import DataParser


class ExcelParser(DataParser):
    """
    Parser for Excel files (XLS, XLSX, XLSM).
    """
    
    def __init__(self, file_path: str = None, file_obj: Any = None, **kwargs):
        """
        Initialize the Excel parser.
        
        Parameters
        ----------
        file_path : str, optional
            Path to the Excel file
        file_obj : Any, optional
            File object if the file is already open
        **kwargs : dict
            Additional parser-specific parameters:
            - sheet_name: str or int or list or None, default 0
            - header: int, list of int, default 0
            - skiprows: list-like, int or callable, default None
        """
        super().__init__(file_path, file_obj, **kwargs)
        self.sheet_name = kwargs.get('sheet_name', 0)
        self.header = kwargs.get('header', 0)
        self.skiprows = kwargs.get('skiprows', None)
        self.sheet_names = []
    
    def parse(self) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Parse the Excel file and return a pandas DataFrame or dict of DataFrames.
        
        Returns
        -------
        Union[pd.DataFrame, Dict[str, pd.DataFrame]]
            The parsed data. If sheet_name is None, returns a dict of DataFrames.
            Otherwise, returns a single DataFrame.
            
        Raises
        ------
        ValueError
            If the file cannot be parsed
        FileNotFoundError
            If the file does not exist
        """
        if self.file_path is None and self.file_obj is None:
            raise ValueError("Either file_path or file_obj must be provided")
        
        try:
            # Parse the file
            if self.file_path is not None:
                # Get sheet names first
                xl = pd.ExcelFile(self.file_path)
                self.sheet_names = xl.sheet_names
                
                # Read the data
                df = pd.read_excel(
                    self.file_path,
                    sheet_name=self.sheet_name,
                    header=self.header,
                    skiprows=self.skiprows
                )
            else:
                # Get sheet names first
                xl = pd.ExcelFile(self.file_obj)
                self.sheet_names = xl.sheet_names
                
                # Read the data
                df = pd.read_excel(
                    self.file_obj,
                    sheet_name=self.sheet_name,
                    header=self.header,
                    skiprows=self.skiprows
                )
            
            # Extract metadata
            if isinstance(df, pd.DataFrame):
                self.metadata = {
                    'rows': len(df),
                    'columns': list(df.columns),
                    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                    'file_format': 'excel',
                    'sheet_name': self.sheet_name,
                    'sheet_names': self.sheet_names
                }
            else:  # Dict of DataFrames
                self.metadata = {
                    'sheets': list(df.keys()),
                    'sheet_count': len(df),
                    'file_format': 'excel',
                    'sheet_details': {
                        sheet: {
                            'rows': len(df_sheet),
                            'columns': list(df_sheet.columns)
                        } for sheet, df_sheet in df.items()
                    }
                }
            
            return df
            
        except Exception as e:
            raise ValueError(f"Failed to parse Excel file: {str(e)}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata from the Excel file.
        
        Returns
        -------
        Dict[str, Any]
            Metadata extracted from the file
        """
        if not self.metadata:
            # Parse the file to extract metadata
            self.parse()
        
        return self.metadata
    
    def get_sheet_names(self) -> List[str]:
        """
        Get the sheet names from the Excel file.
        
        Returns
        -------
        List[str]
            List of sheet names
        """
        if not self.sheet_names:
            if self.file_path is not None:
                xl = pd.ExcelFile(self.file_path)
                self.sheet_names = xl.sheet_names
            elif self.file_obj is not None:
                xl = pd.ExcelFile(self.file_obj)
                self.sheet_names = xl.sheet_names
        
        return self.sheet_names
    
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
        if not os.path.isfile(file_path):
            return False
        
        # Check file extension
        _, ext = os.path.splitext(file_path)
        return ext.lower() in ['.xls', '.xlsx', '.xlsm']
