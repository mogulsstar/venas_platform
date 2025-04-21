"""
CSV file parser.
"""

import os
import pandas as pd
from typing import Dict, Any, Optional, List
import csv
import chardet

from .base import DataParser


class CSVParser(DataParser):
    """
    Parser for CSV files.
    """
    
    def __init__(self, file_path: str = None, file_obj: Any = None, **kwargs):
        """
        Initialize the CSV parser.
        
        Parameters
        ----------
        file_path : str, optional
            Path to the CSV file
        file_obj : Any, optional
            File object if the file is already open
        **kwargs : dict
            Additional parser-specific parameters:
            - delimiter: str, default ','
            - encoding: str, default None (auto-detect)
            - header: int or list of int, default 'infer'
            - skiprows: list-like, int or callable, default None
        """
        super().__init__(file_path, file_obj, **kwargs)
        self.delimiter = kwargs.get('delimiter', ',')
        self.encoding = kwargs.get('encoding', None)
        self.header = kwargs.get('header', 'infer')
        self.skiprows = kwargs.get('skiprows', None)
    
    def parse(self) -> pd.DataFrame:
        """
        Parse the CSV file and return a pandas DataFrame.
        
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
        if self.file_path is None and self.file_obj is None:
            raise ValueError("Either file_path or file_obj must be provided")
        
        try:
            # Auto-detect encoding if not provided
            if self.encoding is None and self.file_path is not None:
                with open(self.file_path, 'rb') as f:
                    result = chardet.detect(f.read(1024 * 1024))  # Read first 1MB
                    self.encoding = result['encoding']
            
            # Auto-detect delimiter if not provided
            if self.delimiter == 'auto' and self.file_path is not None:
                with open(self.file_path, 'r', encoding=self.encoding) as f:
                    sample = f.read(1024)
                    sniffer = csv.Sniffer()
                    self.delimiter = sniffer.sniff(sample).delimiter
            
            # Parse the file
            if self.file_path is not None:
                df = pd.read_csv(
                    self.file_path,
                    delimiter=self.delimiter,
                    encoding=self.encoding,
                    header=self.header,
                    skiprows=self.skiprows
                )
            else:
                df = pd.read_csv(
                    self.file_obj,
                    delimiter=self.delimiter,
                    encoding=self.encoding,
                    header=self.header,
                    skiprows=self.skiprows
                )
            
            # Extract metadata
            self.metadata = {
                'rows': len(df),
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'file_format': 'csv',
                'delimiter': self.delimiter,
                'encoding': self.encoding
            }
            
            return df
            
        except Exception as e:
            raise ValueError(f"Failed to parse CSV file: {str(e)}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata from the CSV file.
        
        Returns
        -------
        Dict[str, Any]
            Metadata extracted from the file
        """
        if not self.metadata:
            # Parse the file to extract metadata
            self.parse()
        
        return self.metadata
    
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
        if ext.lower() in ['.csv', '.tsv', '.txt']:
            # For .txt files, try to detect if it's CSV-like
            if ext.lower() == '.txt':
                try:
                    with open(file_path, 'r', errors='ignore') as f:
                        sample = f.read(1024)
                        sniffer = csv.Sniffer()
                        return sniffer.has_header(sample)
                except:
                    return False
            return True
        
        return False
