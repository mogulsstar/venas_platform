"""
Column operations for data cleaning.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Callable
import re

from .base import DataCleaner


class ColumnOperations(DataCleaner):
    """
    Data cleaner for column operations.
    
    This cleaner provides various operations for manipulating columns:
    - Creating new columns based on mathematical expressions
    - Renaming columns
    - Dropping columns
    - Type conversion
    - Scaling and normalization
    """
    
    def __init__(self, operations: List[Dict[str, Any]], **kwargs):
        """
        Initialize the column operations cleaner.
        
        Parameters
        ----------
        operations : List[Dict[str, Any]]
            List of operations to perform. Each operation is a dict with:
            - type: str, operation type ('create', 'rename', 'drop', 'convert', 'scale')
            - parameters: dict, operation-specific parameters
        **kwargs : dict
            Additional cleaner-specific parameters
        """
        super().__init__(**kwargs)
        self.operations = operations
    
    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the data by performing column operations.
        
        Parameters
        ----------
        data : pd.DataFrame
            The data to clean
            
        Returns
        -------
        pd.DataFrame
            The cleaned data
            
        Raises
        ------
        ValueError
            If an operation is invalid
        """
        # Make a copy of the data to avoid modifying the original
        df = data.copy()
        
        # Track changes for metadata
        changes = []
        
        # Process each operation
        for op in self.operations:
            op_type = op.get('type')
            params = op.get('parameters', {})
            
            if op_type == 'create':
                df, change = self._create_column(df, params)
            elif op_type == 'rename':
                df, change = self._rename_columns(df, params)
            elif op_type == 'drop':
                df, change = self._drop_columns(df, params)
            elif op_type == 'convert':
                df, change = self._convert_types(df, params)
            elif op_type == 'scale':
                df, change = self._scale_columns(df, params)
            else:
                raise ValueError(f"Unknown operation type: {op_type}")
            
            changes.append(change)
        
        # Update metadata
        self.metadata = {
            'operations': len(self.operations),
            'changes': changes,
            'columns_before': list(data.columns),
            'columns_after': list(df.columns),
            'rows_before': len(data),
            'rows_after': len(df)
        }
        
        return df
    
    def _create_column(self, df: pd.DataFrame, params: Dict[str, Any]) -> tuple:
        """
        Create a new column based on an expression.
        
        Parameters
        ----------
        df : pd.DataFrame
            The data
        params : Dict[str, Any]
            Parameters for the operation:
            - name: str, name of the new column
            - expression: str, expression to evaluate
            - description: str, optional description
            
        Returns
        -------
        tuple
            (modified DataFrame, change description)
        """
        name = params.get('name')
        expression = params.get('expression')
        description = params.get('description', '')
        
        if not name or not expression:
            raise ValueError("Column name and expression are required")
        
        # Check if the column already exists
        if name in df.columns:
            raise ValueError(f"Column '{name}' already exists")
        
        # Create a safe evaluation environment
        def safe_eval(expr, row):
            # Create a namespace with numpy functions
            namespace = {
                'np': np,
                'sin': np.sin,
                'cos': np.cos,
                'tan': np.tan,
                'exp': np.exp,
                'log': np.log,
                'log10': np.log10,
                'sqrt': np.sqrt,
                'abs': np.abs,
                'min': np.minimum,
                'max': np.maximum,
                'round': np.round,
                'floor': np.floor,
                'ceil': np.ceil,
                'pi': np.pi,
                'e': np.e
            }
            
            # Add row values to namespace
            for col in df.columns:
                namespace[col] = row[col]
            
            # Evaluate the expression
            return eval(expr, {"__builtins__": {}}, namespace)
        
        # Apply the expression to each row
        try:
            df[name] = df.apply(lambda row: safe_eval(expression, row), axis=1)
            change = {
                'type': 'create',
                'name': name,
                'expression': expression,
                'description': description
            }
            return df, change
        except Exception as e:
            raise ValueError(f"Error evaluating expression: {str(e)}")
    
    def _rename_columns(self, df: pd.DataFrame, params: Dict[str, Any]) -> tuple:
        """
        Rename columns.
        
        Parameters
        ----------
        df : pd.DataFrame
            The data
        params : Dict[str, Any]
            Parameters for the operation:
            - mapping: dict, mapping of old names to new names
            
        Returns
        -------
        tuple
            (modified DataFrame, change description)
        """
        mapping = params.get('mapping', {})
        
        if not mapping:
            raise ValueError("Column mapping is required")
        
        # Check if all columns exist
        missing_columns = [col for col in mapping.keys() if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Columns not found: {missing_columns}")
        
        # Rename columns
        df = df.rename(columns=mapping)
        
        change = {
            'type': 'rename',
            'mapping': mapping
        }
        
        return df, change
    
    def _drop_columns(self, df: pd.DataFrame, params: Dict[str, Any]) -> tuple:
        """
        Drop columns.
        
        Parameters
        ----------
        df : pd.DataFrame
            The data
        params : Dict[str, Any]
            Parameters for the operation:
            - columns: list, columns to drop
            
        Returns
        -------
        tuple
            (modified DataFrame, change description)
        """
        columns = params.get('columns', [])
        
        if not columns:
            raise ValueError("Columns to drop are required")
        
        # Check if all columns exist
        existing_columns = [col for col in columns if col in df.columns]
        
        # Drop columns
        df = df.drop(columns=existing_columns)
        
        change = {
            'type': 'drop',
            'columns': existing_columns
        }
        
        return df, change
    
    def _convert_types(self, df: pd.DataFrame, params: Dict[str, Any]) -> tuple:
        """
        Convert column types.
        
        Parameters
        ----------
        df : pd.DataFrame
            The data
        params : Dict[str, Any]
            Parameters for the operation:
            - conversions: dict, mapping of column names to types
            
        Returns
        -------
        tuple
            (modified DataFrame, change description)
        """
        conversions = params.get('conversions', {})
        
        if not conversions:
            raise ValueError("Type conversions are required")
        
        # Check if all columns exist
        missing_columns = [col for col in conversions.keys() if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Columns not found: {missing_columns}")
        
        # Track successful conversions
        successful = {}
        
        # Convert types
        for col, dtype in conversions.items():
            try:
                df[col] = df[col].astype(dtype)
                successful[col] = dtype
            except Exception as e:
                # Skip failed conversions
                pass
        
        change = {
            'type': 'convert',
            'conversions': successful
        }
        
        return df, change
    
    def _scale_columns(self, df: pd.DataFrame, params: Dict[str, Any]) -> tuple:
        """
        Scale columns.
        
        Parameters
        ----------
        df : pd.DataFrame
            The data
        params : Dict[str, Any]
            Parameters for the operation:
            - columns: list, columns to scale
            - method: str, scaling method ('minmax', 'standard', 'robust')
            - inplace: bool, whether to replace original columns
            
        Returns
        -------
        tuple
            (modified DataFrame, change description)
        """
        columns = params.get('columns', [])
        method = params.get('method', 'minmax')
        inplace = params.get('inplace', False)
        
        if not columns:
            raise ValueError("Columns to scale are required")
        
        # Check if all columns exist
        missing_columns = [col for col in columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Columns not found: {missing_columns}")
        
        # Scale columns
        scaled_data = {}
        
        for col in columns:
            # Skip non-numeric columns
            if not pd.api.types.is_numeric_dtype(df[col]):
                continue
            
            if method == 'minmax':
                # Min-max scaling
                min_val = df[col].min()
                max_val = df[col].max()
                if max_val > min_val:
                    scaled = (df[col] - min_val) / (max_val - min_val)
                else:
                    scaled = df[col] - min_val  # Avoid division by zero
            elif method == 'standard':
                # Standard scaling (z-score)
                mean = df[col].mean()
                std = df[col].std()
                if std > 0:
                    scaled = (df[col] - mean) / std
                else:
                    scaled = df[col] - mean  # Avoid division by zero
            elif method == 'robust':
                # Robust scaling using median and IQR
                median = df[col].median()
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                if iqr > 0:
                    scaled = (df[col] - median) / iqr
                else:
                    scaled = df[col] - median  # Avoid division by zero
            else:
                raise ValueError(f"Unknown scaling method: {method}")
            
            # Store scaled data
            if inplace:
                df[col] = scaled
            else:
                df[f"{col}_{method}_scaled"] = scaled
                scaled_data[col] = f"{col}_{method}_scaled"
        
        change = {
            'type': 'scale',
            'method': method,
            'columns': columns,
            'inplace': inplace,
            'scaled_columns': scaled_data if not inplace else columns
        }
        
        return df, change
