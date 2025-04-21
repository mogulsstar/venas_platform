"""
Missing value handling utilities for data cleaning.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union
from sklearn.impute import SimpleImputer, KNNImputer

from .base import DataCleaner


class MissingValueHandler(DataCleaner):
    """
    Data cleaner for handling missing values.
    
    This cleaner provides various methods for handling missing values:
    - Drop rows or columns with missing values
    - Fill missing values with a constant
    - Fill missing values with statistical measures (mean, median, mode)
    - Fill missing values using interpolation
    - Fill missing values using KNN imputation
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the missing value handler.
        
        Parameters
        ----------
        **kwargs : dict
            Additional cleaner-specific parameters:
            - columns: list, columns to check for missing values
            - method: str, handling method ('drop_rows', 'drop_columns', 'fill_constant', 
                                           'fill_mean', 'fill_median', 'fill_mode',
                                           'fill_interpolate', 'fill_knn')
            - threshold: float, threshold for dropping (fraction of missing values)
            - fill_value: Any, value to use for filling if method='fill_constant'
            - interpolation_method: str, interpolation method if method='fill_interpolate'
            - knn_neighbors: int, number of neighbors for KNN imputation
        """
        super().__init__(**kwargs)
        self.columns = kwargs.get('columns', [])
        self.method = kwargs.get('method', 'fill_mean')
        self.threshold = kwargs.get('threshold', 0.5)
        self.fill_value = kwargs.get('fill_value', 0)
        self.interpolation_method = kwargs.get('interpolation_method', 'linear')
        self.knn_neighbors = kwargs.get('knn_neighbors', 5)
    
    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the data by handling missing values.
        
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
            If required parameters are missing or invalid
        """
        # Make a copy of the data to avoid modifying the original
        df = data.copy()
        
        # Validate parameters
        if not self.columns:
            # Use all columns if none specified
            self.columns = df.columns.tolist()
        
        # Check if all columns exist
        missing_columns = [col for col in self.columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Columns not found: {missing_columns}")
        
        # Count missing values
        missing_counts = df[self.columns].isna().sum()
        total_missing = missing_counts.sum()
        
        # Handle missing values
        if self.method == 'drop_rows':
            # Drop rows with missing values
            if len(self.columns) == len(df.columns):
                # If all columns are specified, use dropna directly
                df = df.dropna(thresh=int((1 - self.threshold) * len(self.columns)))
            else:
                # Otherwise, only consider specified columns
                mask = df[self.columns].isna().sum(axis=1) <= self.threshold * len(self.columns)
                df = df[mask].reset_index(drop=True)
                
        elif self.method == 'drop_columns':
            # Drop columns with too many missing values
            cols_to_drop = [col for col in self.columns if df[col].isna().mean() > self.threshold]
            df = df.drop(columns=cols_to_drop)
            
        elif self.method == 'fill_constant':
            # Fill missing values with a constant
            df[self.columns] = df[self.columns].fillna(self.fill_value)
            
        elif self.method == 'fill_mean':
            # Fill missing values with column means
            for col in self.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].mean())
            
        elif self.method == 'fill_median':
            # Fill missing values with column medians
            for col in self.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].median())
            
        elif self.method == 'fill_mode':
            # Fill missing values with column modes
            for col in self.columns:
                mode_value = df[col].mode()[0] if not df[col].mode().empty else None
                if mode_value is not None:
                    df[col] = df[col].fillna(mode_value)
            
        elif self.method == 'fill_interpolate':
            # Fill missing values using interpolation
            for col in self.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].interpolate(method=self.interpolation_method)
            
        elif self.method == 'fill_knn':
            # Fill missing values using KNN imputation
            numeric_columns = [col for col in self.columns if pd.api.types.is_numeric_dtype(df[col])]
            
            if numeric_columns:
                # Create KNN imputer
                imputer = KNNImputer(n_neighbors=self.knn_neighbors)
                
                # Impute missing values
                imputed_data = imputer.fit_transform(df[numeric_columns])
                
                # Update DataFrame
                df[numeric_columns] = imputed_data
            
        else:
            raise ValueError(f"Unknown missing value handling method: {self.method}")
        
        # Count remaining missing values
        remaining_missing = df[self.columns].isna().sum()
        total_remaining = remaining_missing.sum()
        
        # Update metadata
        self.metadata = {
            'method': self.method,
            'columns': self.columns,
            'missing_counts_before': missing_counts.to_dict(),
            'total_missing_before': total_missing,
            'missing_counts_after': remaining_missing.to_dict(),
            'total_missing_after': total_remaining,
            'rows_before': len(data),
            'rows_after': len(df)
        }
        
        return df
