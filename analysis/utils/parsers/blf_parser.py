"""
BLF (Binary Logging Format) file parser.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import struct
import datetime

from .base import DataParser


class BLFParser(DataParser):
    """
    Parser for BLF (Binary Logging Format) files.
    
    This parser handles Vector BLF files commonly used in automotive CAN bus logging.
    Note: This implementation requires the 'can' package with BLF support.
    Install with: pip install python-can
    """
    
    def __init__(self, file_path: str = None, file_obj: Any = None, **kwargs):
        """
        Initialize the BLF parser.
        
        Parameters
        ----------
        file_path : str, optional
            Path to the BLF file
        file_obj : Any, optional
            File object if the file is already open
        **kwargs : dict
            Additional parser-specific parameters:
            - channels: list, default None (all channels)
            - start_time: datetime, default None
            - end_time: datetime, default None
        """
        super().__init__(file_path, file_obj, **kwargs)
        self.channels = kwargs.get('channels', None)
        self.start_time = kwargs.get('start_time', None)
        self.end_time = kwargs.get('end_time', None)
    
    def parse(self) -> pd.DataFrame:
        """
        Parse the BLF file and return a pandas DataFrame.
        
        Returns
        -------
        pd.DataFrame
            The parsed data with columns for timestamp, channel, ID, data, etc.
            
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
            raise ValueError("file_path must be provided for BLF parsing")
        
        try:
            # Import can module (python-can)
            try:
                import can
                from can.io import BLFReader
            except ImportError:
                raise ImportError("The 'can' package is required for BLF parsing. Install with: pip install python-can")
            
            # Parse the file
            messages = []
            with BLFReader(self.file_path) as reader:
                for msg in reader:
                    # Apply time filter if specified
                    if self.start_time and msg.timestamp < self.start_time.timestamp():
                        continue
                    if self.end_time and msg.timestamp > self.end_time.timestamp():
                        continue
                    
                    # Apply channel filter if specified
                    if self.channels and msg.channel not in self.channels:
                        continue
                    
                    # Extract message data
                    data = {
                        'timestamp': msg.timestamp,
                        'datetime': datetime.datetime.fromtimestamp(msg.timestamp),
                        'channel': msg.channel,
                        'id': msg.arbitration_id,
                        'is_extended_id': msg.is_extended_id,
                        'is_remote_frame': msg.is_remote_frame,
                        'is_error_frame': msg.is_error_frame,
                        'dlc': msg.dlc,
                        'data': ' '.join(f'{b:02X}' for b in msg.data),
                        'data_bytes': msg.data,
                    }
                    messages.append(data)
            
            # Create DataFrame
            df = pd.DataFrame(messages)
            
            # Extract metadata
            self.metadata = {
                'rows': len(df),
                'columns': list(df.columns),
                'file_format': 'blf',
                'start_time': df['timestamp'].min() if not df.empty else None,
                'end_time': df['timestamp'].max() if not df.empty else None,
                'channels': df['channel'].unique().tolist() if not df.empty else [],
                'message_count': len(df),
                'unique_ids': df['id'].nunique() if not df.empty else 0
            }
            
            return df
            
        except Exception as e:
            raise ValueError(f"Failed to parse BLF file: {str(e)}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata from the BLF file.
        
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
        if ext.lower() != '.blf':
            return False
        
        # Check if python-can is installed
        try:
            import can
            return True
        except ImportError:
            return False
