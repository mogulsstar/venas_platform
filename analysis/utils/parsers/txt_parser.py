"""
Text file parser.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import chardet
import re

from .base import DataParser


class TXTParser(DataParser):
    """
    Parser for generic text files.
    """
    
    def __init__(self, file_path: str = None, file_obj: Any = None, **kwargs):
        """
        Initialize the TXT parser.
        
        Parameters
        ----------
        file_path : str, optional
            Path to the text file
        file_obj : Any, optional
            File object if the file is already open
        **kwargs : dict
            Additional parser-specific parameters:
            - delimiter: str, default None (auto-detect)
            - encoding: str, default None (auto-detect)
            - header: int or list of int, default None
            - skiprows: list-like, int or callable, default None
            - comment: str, default None
        """
        super().__init__(file_path, file_obj, **kwargs)
        self.delimiter = kwargs.get('delimiter', None)
        self.encoding = kwargs.get('encoding', None)
        self.header = kwargs.get('header', None)
        self.skiprows = kwargs.get('skiprows', None)
        self.comment = kwargs.get('comment', None)
    
    def parse(self) -> pd.DataFrame:
        """
        Parse the text file and return a pandas DataFrame.
        
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
            
            # Read the file content
            if self.file_path is not None:
                with open(self.file_path, 'r', encoding=self.encoding) as f:
                    content = f.readlines()
            else:
                content = self.file_obj.readlines()
            
            # Skip comment lines and empty lines
            if self.comment is not None:
                content = [line for line in content if not line.strip().startswith(self.comment) and line.strip()]
            else:
                content = [line for line in content if line.strip()]
            
            # Skip rows if specified
            if self.skiprows is not None:
                if isinstance(self.skiprows, int):
                    content = content[self.skiprows:]
                elif callable(self.skiprows):
                    content = [line for i, line in enumerate(content) if not self.skiprows(i)]
                else:
                    content = [line for i, line in enumerate(content) if i not in self.skiprows]
            
            # Auto-detect delimiter if not provided
            if self.delimiter is None:
                # Try common delimiters
                delimiters = [',', '\t', ';', '|', ' ']
                max_columns = 0
                best_delimiter = None
                
                for delimiter in delimiters:
                    # Count columns in first few non-empty lines
                    column_counts = [len(line.strip().split(delimiter)) for line in content[:10] if line.strip()]
                    if column_counts and max(column_counts) > max_columns:
                        max_columns = max(column_counts)
                        best_delimiter = delimiter
                
                self.delimiter = best_delimiter if best_delimiter else ','
            
            # Parse the content
            data = []
            for line in content:
                row = line.strip().split(self.delimiter)
                data.append(row)
            
            # Determine header
            if self.header is not None:
                if isinstance(self.header, int):
                    header = data[self.header]
                    data = data[self.header + 1:]
                else:
                    header = [f"Column_{i}" for i in range(len(data[0]))]
            else:
                # Try to detect if first row is header
                first_row = data[0]
                rest_rows = data[1:]
                
                # Check if first row contains only strings and rest contains numbers
                first_row_is_header = True
                for row in rest_rows[:5]:  # Check first few rows
                    if len(row) != len(first_row):
                        first_row_is_header = False
                        break
                    
                    for cell in row:
                        # Try to convert to float
                        try:
                            float(cell)
                        except ValueError:
                            # If conversion fails, it might not be a header
                            if not re.match(r'^[a-zA-Z_]\w*$', cell):
                                first_row_is_header = False
                                break
                
                if first_row_is_header:
                    header = first_row
                    data = rest_rows
                else:
                    header = [f"Column_{i}" for i in range(len(data[0]))]
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=header)
            
            # Try to convert columns to appropriate types
            for col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col])
                except:
                    pass  # Keep as string if conversion fails
            
            # Extract metadata
            self.metadata = {
                'rows': len(df),
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'file_format': 'txt',
                'delimiter': self.delimiter,
                'encoding': self.encoding
            }
            
            return df
            
        except Exception as e:
            raise ValueError(f"Failed to parse text file: {str(e)}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata from the text file.
        
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
        if ext.lower() == '.txt':
            # Try to read a few lines to see if it's a structured text file
            try:
                with open(file_path, 'r', errors='ignore') as f:
                    lines = [line.strip() for line in f.readlines(1024) if line.strip()]
                    
                    if not lines:
                        return False
                    
                    # Check if all lines have similar structure
                    first_line_parts = len(lines[0].split())
                    similar_structure = all(abs(len(line.split()) - first_line_parts) <= 1 for line in lines[1:5] if line)
                    
                    return similar_structure
            except:
                return False
        
        return False
