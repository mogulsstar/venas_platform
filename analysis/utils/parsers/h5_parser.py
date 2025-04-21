"""
HDF5 file parser.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union

from .base import DataParser


class H5Parser(DataParser):
    """
    Parser for HDF5 files (.h5, .hdf5).
    
    This parser handles HDF5 files which are commonly used for storing large
    scientific datasets.
    
    Note: This implementation requires the 'h5py' package.
    Install with: pip install h5py
    """
    
    def __init__(self, file_path: str = None, file_obj: Any = None, **kwargs):
        """
        Initialize the HDF5 parser.
        
        Parameters
        ----------
        file_path : str, optional
            Path to the HDF5 file
        file_obj : Any, optional
            File object if the file is already open
        **kwargs : dict
            Additional parser-specific parameters:
            - dataset_path: str, default None (auto-detect)
            - key: str, default None (for pandas HDFStore)
        """
        super().__init__(file_path, file_obj, **kwargs)
        self.dataset_path = kwargs.get('dataset_path', None)
        self.key = kwargs.get('key', None)
        self.structure = {}
    
    def parse(self) -> Union[pd.DataFrame, Dict[str, Any]]:
        """
        Parse the HDF5 file and return a pandas DataFrame or dict of datasets.
        
        Returns
        -------
        Union[pd.DataFrame, Dict[str, Any]]
            The parsed data. If dataset_path or key is specified, returns a DataFrame.
            Otherwise, returns a dict of datasets.
            
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
            raise ValueError("file_path must be provided for HDF5 parsing")
        
        try:
            # Try to open as pandas HDFStore first
            try:
                # If key is provided, try to read as pandas HDFStore
                if self.key is not None:
                    df = pd.read_hdf(self.file_path, key=self.key)
                    
                    # Extract metadata
                    self.metadata = {
                        'rows': len(df),
                        'columns': list(df.columns),
                        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                        'file_format': 'hdf5',
                        'key': self.key
                    }
                    
                    return df
            except:
                pass
            
            # Import h5py
            try:
                import h5py
            except ImportError:
                raise ImportError("The 'h5py' package is required for HDF5 parsing. Install with: pip install h5py")
            
            # Open the file
            with h5py.File(self.file_path, 'r') as f:
                # Map the file structure
                self._map_structure(f, self.structure)
                
                # If dataset_path is provided, return that dataset
                if self.dataset_path is not None:
                    if self.dataset_path in f:
                        dataset = f[self.dataset_path]
                        if isinstance(dataset, h5py.Dataset):
                            data = dataset[:]
                            
                            # Convert to DataFrame if possible
                            if len(data.shape) <= 2:
                                if len(data.shape) == 1:
                                    df = pd.DataFrame({self.dataset_path: data})
                                else:
                                    # Try to get column names from attributes
                                    if 'column_names' in dataset.attrs:
                                        columns = dataset.attrs['column_names']
                                    else:
                                        columns = [f"Column_{i}" for i in range(data.shape[1])]
                                    
                                    df = pd.DataFrame(data, columns=columns)
                                
                                # Extract metadata
                                self.metadata = {
                                    'rows': len(df),
                                    'columns': list(df.columns),
                                    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                                    'file_format': 'hdf5',
                                    'dataset_path': self.dataset_path,
                                    'shape': data.shape,
                                    'dtype': str(data.dtype),
                                    'attributes': {k: v for k, v in dataset.attrs.items()}
                                }
                                
                                return df
                            else:
                                # Return as is for higher dimensional data
                                self.metadata = {
                                    'file_format': 'hdf5',
                                    'dataset_path': self.dataset_path,
                                    'shape': data.shape,
                                    'dtype': str(data.dtype),
                                    'attributes': {k: v for k, v in dataset.attrs.items()}
                                }
                                
                                return {'data': data, 'metadata': self.metadata}
                        else:
                            raise ValueError(f"Path '{self.dataset_path}' is not a dataset")
                    else:
                        raise ValueError(f"Dataset path '{self.dataset_path}' not found in file")
                
                # Otherwise, return the structure
                self.metadata = {
                    'file_format': 'hdf5',
                    'structure': self.structure,
                    'groups': [k for k, v in self.structure.items() if isinstance(v, dict)],
                    'datasets': [k for k, v in self.structure.items() if not isinstance(v, dict)]
                }
                
                return {'structure': self.structure, 'metadata': self.metadata}
            
        except Exception as e:
            raise ValueError(f"Failed to parse HDF5 file: {str(e)}")
    
    def _map_structure(self, group, structure_dict):
        """
        Recursively map the structure of an HDF5 file.
        
        Parameters
        ----------
        group : h5py.Group
            The HDF5 group to map
        structure_dict : dict
            The dictionary to store the structure in
        """
        import h5py
        
        for key, item in group.items():
            if isinstance(item, h5py.Group):
                structure_dict[key] = {}
                self._map_structure(item, structure_dict[key])
            elif isinstance(item, h5py.Dataset):
                structure_dict[key] = {
                    'shape': item.shape,
                    'dtype': str(item.dtype),
                    'attributes': {k: v for k, v in item.attrs.items()}
                }
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata from the HDF5 file.
        
        Returns
        -------
        Dict[str, Any]
            Metadata extracted from the file
        """
        if not self.metadata:
            # Parse the file to extract metadata
            self.parse()
        
        return self.metadata
    
    def get_structure(self) -> Dict[str, Any]:
        """
        Get the structure of the HDF5 file.
        
        Returns
        -------
        Dict[str, Any]
            Structure of the HDF5 file
        """
        if not self.structure:
            # Parse the file to extract structure
            self.parse()
        
        return self.structure
    
    def list_datasets(self) -> List[str]:
        """
        List all datasets in the HDF5 file.
        
        Returns
        -------
        List[str]
            List of dataset paths
        """
        structure = self.get_structure()
        datasets = []
        
        def _find_datasets(struct, prefix=''):
            for key, value in struct.items():
                path = f"{prefix}/{key}" if prefix else key
                if isinstance(value, dict) and 'shape' in value and 'dtype' in value:
                    datasets.append(path)
                elif isinstance(value, dict) and 'shape' not in value:
                    _find_datasets(value, path)
        
        _find_datasets(structure)
        return datasets
    
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
        if ext.lower() not in ['.h5', '.hdf5', '.he5']:
            return False
        
        # Check if h5py is installed
        try:
            import h5py
            
            # Try to open the file
            try:
                with h5py.File(file_path, 'r') as f:
                    return True
            except:
                # Try as pandas HDFStore
                try:
                    with pd.HDFStore(file_path, 'r') as store:
                        return True
                except:
                    return False
        except ImportError:
            return False
