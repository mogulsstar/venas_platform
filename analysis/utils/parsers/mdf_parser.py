"""
MDF (Measurement Data Format) file parser.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union

from .base import DataParser


class MDFParser(DataParser):
    """
    Parser for MDF (Measurement Data Format) files (.mdf, .dat).
    
    This parser handles MDF files which are commonly used in automotive
    measurement and calibration applications.
    
    Note: This implementation requires the 'asammdf' package.
    Install with: pip install asammdf
    """
    
    def __init__(self, file_path: str = None, file_obj: Any = None, **kwargs):
        """
        Initialize the MDF parser.
        
        Parameters
        ----------
        file_path : str, optional
            Path to the MDF file
        file_obj : Any, optional
            File object if the file is already open
        **kwargs : dict
            Additional parser-specific parameters:
            - channels: list, default None (all channels)
            - start_time: float, default None
            - end_time: float, default None
            - resample: float, default None (no resampling)
        """
        super().__init__(file_path, file_obj, **kwargs)
        self.channels = kwargs.get('channels', None)
        self.start_time = kwargs.get('start_time', None)
        self.end_time = kwargs.get('end_time', None)
        self.resample = kwargs.get('resample', None)
    
    def parse(self) -> pd.DataFrame:
        """
        Parse the MDF file and return a pandas DataFrame.
        
        Returns
        -------
        pd.DataFrame
            The parsed data with time as index and channels as columns
            
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
            raise ValueError("file_path must be provided for MDF parsing")
        
        try:
            # Import asammdf
            try:
                from asammdf import MDF
            except ImportError:
                raise ImportError("The 'asammdf' package is required for MDF parsing. Install with: pip install asammdf")
            
            # Open the file
            mdf = MDF(self.file_path)
            
            # Get available channels
            available_channels = mdf.channels_db
            
            # Select channels
            if self.channels is not None:
                # Validate channels
                invalid_channels = [ch for ch in self.channels if ch not in available_channels]
                if invalid_channels:
                    raise ValueError(f"Invalid channels: {invalid_channels}")
                
                channels = self.channels
            else:
                # Use all channels except for special ones
                channels = [ch for ch in available_channels if not ch.startswith('_')]
            
            # Extract data
            if self.resample is not None:
                # Resample data
                signals = mdf.to_dataframe(channels=channels, time_from_zero=False, raster=self.resample)
            else:
                # Get raw data
                signals = mdf.to_dataframe(channels=channels, time_from_zero=False)
            
            # Apply time filter if specified
            if self.start_time is not None or self.end_time is not None:
                start = self.start_time if self.start_time is not None else signals.index[0]
                end = self.end_time if self.end_time is not None else signals.index[-1]
                signals = signals.loc[start:end]
            
            # Extract metadata
            self.metadata = {
                'file_format': 'mdf',
                'version': mdf.version,
                'channels': list(signals.columns),
                'channel_count': len(signals.columns),
                'start_time': signals.index[0] if not signals.empty else None,
                'end_time': signals.index[-1] if not signals.empty else None,
                'duration': signals.index[-1] - signals.index[0] if not signals.empty else None,
                'rows': len(signals),
                'sample_rate': self.resample if self.resample is not None else 'variable',
                'file_metadata': {
                    'author': mdf.header.author,
                    'department': mdf.header.department,
                    'project': mdf.header.project,
                    'subject': mdf.header.subject,
                    'comment': mdf.header.comment,
                    'date': str(mdf.header.start_time) if mdf.header.start_time else None,
                }
            }
            
            return signals
            
        except Exception as e:
            raise ValueError(f"Failed to parse MDF file: {str(e)}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata from the MDF file.
        
        Returns
        -------
        Dict[str, Any]
            Metadata extracted from the file
        """
        if not self.metadata:
            # Parse the file to extract metadata
            self.parse()
        
        return self.metadata
    
    def list_channels(self) -> List[str]:
        """
        List all channels in the MDF file.
        
        Returns
        -------
        List[str]
            List of channel names
        """
        if self.file_path is None:
            raise ValueError("file_path must be provided for MDF parsing")
        
        try:
            # Import asammdf
            from asammdf import MDF
            
            # Open the file
            mdf = MDF(self.file_path)
            
            # Get available channels
            channels = list(mdf.channels_db.keys())
            
            return channels
            
        except Exception as e:
            raise ValueError(f"Failed to list channels: {str(e)}")
    
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
        if ext.lower() not in ['.mdf', '.dat', '.mf4']:
            return False
        
        # Check if asammdf is installed
        try:
            from asammdf import MDF
            
            # Try to open the file
            try:
                MDF(file_path)
                return True
            except:
                return False
        except ImportError:
            return False
