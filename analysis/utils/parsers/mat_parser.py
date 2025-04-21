"""
MATLAB MAT file parser.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union

from .base import DataParser


class MATParser(DataParser):
    """
    Parser for MATLAB MAT files (.mat).
    
    This parser handles MATLAB MAT files which are commonly used for storing
    scientific data and variables.
    
    Note: This implementation requires the 'scipy' package.
    Install with: pip install scipy
    """
    
    def __init__(self, file_path: str = None, file_obj: Any = None, **kwargs):
        """
        Initialize the MAT parser.
        
        Parameters
        ----------
        file_path : str, optional
            Path to the MAT file
        file_obj : Any, optional
            File object if the file is already open
        **kwargs : dict
            Additional parser-specific parameters:
            - variable: str, default None (auto-detect)
            - squeeze_me: bool, default False
            - struct_as_record: bool, default True
        """
        super().__init__(file_path, file_obj, **kwargs)
        self.variable = kwargs.get('variable', None)
        self.squeeze_me = kwargs.get('squeeze_me', False)
        self.struct_as_record = kwargs.get('struct_as_record', True)
        self.variables = {}
    
    def parse(self) -> Union[pd.DataFrame, Dict[str, Any]]:
        """
        Parse the MAT file and return a pandas DataFrame or dict of variables.
        
        Returns
        -------
        Union[pd.DataFrame, Dict[str, Any]]
            The parsed data. If variable is specified, returns a DataFrame if possible.
            Otherwise, returns a dict of variables.
            
        Raises
        ------
        ValueError
            If the file cannot be parsed
        FileNotFoundError
            If the file does not exist
        ImportError
            If the required dependencies are not installed
        """
        if self.file_path is None:
            raise ValueError("file_path must be provided for MAT parsing")
        
        try:
            # Import scipy.io
            try:
                import scipy.io as sio
            except ImportError:
                raise ImportError("The 'scipy' package is required for MAT parsing. Install with: pip install scipy")
            
            # Load the MAT file
            mat_data = sio.loadmat(
                self.file_path,
                squeeze_me=self.squeeze_me,
                struct_as_record=self.struct_as_record
            )
            
            # Remove special variables
            for key in list(mat_data.keys()):
                if key.startswith('__') and key.endswith('__'):
                    del mat_data[key]
            
            # Store variables
            self.variables = mat_data
            
            # Extract metadata
            self.metadata = {
                'file_format': 'mat',
                'variables': list(mat_data.keys()),
                'variable_count': len(mat_data),
                'variable_types': {k: str(type(v)) for k, v in mat_data.items()}
            }
            
            # If variable is specified, return that variable
            if self.variable is not None:
                if self.variable in mat_data:
                    data = mat_data[self.variable]
                    
                    # Try to convert to DataFrame
                    if isinstance(data, np.ndarray):
                        if len(data.shape) <= 2:
                            if len(data.shape) == 1:
                                df = pd.DataFrame({self.variable: data})
                            else:
                                # Create column names
                                columns = [f"{self.variable}_{i}" for i in range(data.shape[1])]
                                df = pd.DataFrame(data, columns=columns)
                            
                            return df
                        else:
                            # Return as is for higher dimensional data
                            return {self.variable: data}
                    elif isinstance(data, dict):
                        # Try to convert struct to DataFrame
                        try:
                            df = pd.DataFrame.from_dict(data)
                            return df
                        except:
                            return {self.variable: data}
                    else:
                        return {self.variable: data}
                else:
                    raise ValueError(f"Variable '{self.variable}' not found in MAT file")
            
            # Otherwise, return all variables
            return mat_data
            
        except Exception as e:
            raise ValueError(f"Failed to parse MAT file: {str(e)}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata from the MAT file.
        
        Returns
        -------
        Dict[str, Any]
            Metadata extracted from the file
        """
        if not self.metadata:
            # Parse the file to extract metadata
            self.parse()
        
        return self.metadata
    
    def list_variables(self) -> List[str]:
        """
        List all variables in the MAT file.
        
        Returns
        -------
        List[str]
            List of variable names
        """
        if not self.variables:
            # Parse the file to extract variables
            self.parse()
        
        return list(self.variables.keys())
    
    def get_variable(self, name: str) -> Any:
        """
        Get a specific variable from the MAT file.
        
        Parameters
        ----------
        name : str
            Name of the variable
            
        Returns
        -------
        Any
            The variable value
            
        Raises
        ------
        ValueError
            If the variable does not exist
        """
        if not self.variables:
            # Parse the file to extract variables
            self.parse()
        
        if name in self.variables:
            return self.variables[name]
        else:
            raise ValueError(f"Variable '{name}' not found in MAT file")
    
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
        if ext.lower() != '.mat':
            return False
        
        # Check if scipy is installed
        try:
            import scipy.io as sio
            
            # Try to open the file
            try:
                sio.loadmat(file_path)
                return True
            except:
                return False
        except ImportError:
            return False
