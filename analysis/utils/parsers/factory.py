"""
Parser factory for selecting the appropriate parser for a given file.
"""

import os
from typing import Dict, Any, Optional, Type, List

from .base import DataParser
from .csv_parser import CSVParser
from .excel_parser import ExcelParser
from .txt_parser import TXTParser
from .blf_parser import BLFParser
from .h5_parser import H5Parser
from .mdf_parser import MDFParser
from .mat_parser import MATParser


class ParserFactory:
    """
    Factory class for creating data parsers.
    """
    
    # Registry of parsers
    _parsers = [
        CSVParser,
        ExcelParser,
        TXTParser,
        BLFParser,
        H5Parser,
        MDFParser,
        MATParser,
    ]
    
    @classmethod
    def get_parser(cls, file_path: str, **kwargs) -> DataParser:
        """
        Get the appropriate parser for the given file.
        
        Parameters
        ----------
        file_path : str
            Path to the data file
        **kwargs : dict
            Additional parser-specific parameters
            
        Returns
        -------
        DataParser
            The parser instance
            
        Raises
        ------
        ValueError
            If no parser can handle the file
        FileNotFoundError
            If the file does not exist
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Try to find a parser that can handle this file
        for parser_cls in cls._parsers:
            if parser_cls.can_parse(file_path):
                return parser_cls(file_path=file_path, **kwargs)
        
        # If no parser is found, try to guess based on extension
        if ext in ['.csv', '.tsv']:
            return CSVParser(file_path=file_path, **kwargs)
        elif ext in ['.xls', '.xlsx', '.xlsm']:
            return ExcelParser(file_path=file_path, **kwargs)
        elif ext == '.txt':
            return TXTParser(file_path=file_path, **kwargs)
        elif ext == '.blf':
            return BLFParser(file_path=file_path, **kwargs)
        elif ext in ['.h5', '.hdf5', '.he5']:
            return H5Parser(file_path=file_path, **kwargs)
        elif ext in ['.mdf', '.dat', '.mf4']:
            return MDFParser(file_path=file_path, **kwargs)
        elif ext == '.mat':
            return MATParser(file_path=file_path, **kwargs)
        
        raise ValueError(f"No parser available for file: {file_path}")
    
    @classmethod
    def register_parser(cls, parser_cls: Type[DataParser]) -> None:
        """
        Register a new parser.
        
        Parameters
        ----------
        parser_cls : Type[DataParser]
            The parser class to register
        """
        if parser_cls not in cls._parsers:
            cls._parsers.append(parser_cls)
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """
        Get a list of supported file extensions.
        
        Returns
        -------
        List[str]
            List of supported file extensions
        """
        extensions = []
        for parser_cls in cls._parsers:
            # Get extensions from docstring
            docstring = parser_cls.__doc__ or ""
            for line in docstring.split('\n'):
                if '.(' in line and ')' in line:
                    ext_part = line.split('(')[1].split(')')[0]
                    exts = [e.strip() for e in ext_part.split(',')]
                    extensions.extend(exts)
        
        # Add known extensions
        known_extensions = [
            '.csv', '.tsv', '.xls', '.xlsx', '.xlsm', '.txt',
            '.blf', '.h5', '.hdf5', '.he5', '.mdf', '.dat', '.mf4', '.mat'
        ]
        
        # Combine and remove duplicates
        all_extensions = list(set(extensions + known_extensions))
        
        return sorted(all_extensions)
