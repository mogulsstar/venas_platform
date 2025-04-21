"""
Outlier detection utilities for data cleaning.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from scipy import stats

from .base import DataCleaner


class OutlierDetection(DataCleaner):
    """
    Data cleaner for detecting and handling outliers.
    
    This cleaner provides various methods for outlier detection:
    - Z-score method
    - IQR method
    - Isolation Forest
    - Local Outlier Factor
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the outlier detection cleaner.
        
        Parameters
        ----------
        **kwargs : dict
            Additional cleaner-specific parameters:
            - columns: list, columns to check for outliers
            - method: str, detection method ('zscore', 'iqr', 'isolation_forest', 'lof')
            - threshold: float, threshold for outlier detection
            - action: str, action to take ('flag', 'remove', 'replace')
            - replacement: str, replacement method ('mean', 'median', 'mode', 'value')
            - replacement_value: Any, value to use for replacement if action='replace' and replacement='value'
        """
        super().__init__(**kwargs)
        self.columns = kwargs.get('columns', [])
        self.method = kwargs.get('method', 'zscore')
        self.threshold = kwargs.get('threshold', 3.0)  # Default threshold for z-score
        self.action = kwargs.get('action', 'flag')
        self.replacement = kwargs.get('replacement', 'mean')
        self.replacement_value = kwargs.get('replacement_value', None)
    
    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the data by detecting and handling outliers.
        
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
            # Use all numeric columns if none specified
            self.columns = df.select_dtypes(include=np.number).columns.tolist()
        
        # Check if all columns exist and are numeric
        missing_columns = [col for col in self.columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Columns not found: {missing_columns}")
        
        non_numeric_columns = [col for col in self.columns if not pd.api.types.is_numeric_dtype(df[col])]
        if non_numeric_columns:
            raise ValueError(f"Non-numeric columns: {non_numeric_columns}")
        
        # Detect outliers
        if self.method == 'zscore':
            outliers = self._detect_zscore(df)
        elif self.method == 'iqr':
            outliers = self._detect_iqr(df)
        elif self.method == 'isolation_forest':
            outliers = self._detect_isolation_forest(df)
        elif self.method == 'lof':
            outliers = self._detect_lof(df)
        else:
            raise ValueError(f"Unknown outlier detection method: {self.method}")
        
        # Count outliers
        outlier_counts = {col: outliers[col].sum() for col in self.columns}
        total_outliers = sum(outlier_counts.values())
        
        # Handle outliers
        if self.action == 'flag':
            # Add outlier flag columns
            for col in self.columns:
                df[f"{col}_outlier"] = outliers[col]
                
        elif self.action == 'remove':
            # Create a mask for rows to keep
            keep_mask = ~outliers.any(axis=1)
            df = df[keep_mask].reset_index(drop=True)
            
        elif self.action == 'replace':
            # Replace outliers with specified value
            for col in self.columns:
                if self.replacement == 'mean':
                    replacement_value = df[col].mean()
                elif self.replacement == 'median':
                    replacement_value = df[col].median()
                elif self.replacement == 'mode':
                    replacement_value = df[col].mode()[0]
                elif self.replacement == 'value':
                    replacement_value = self.replacement_value
                else:
                    raise ValueError(f"Unknown replacement method: {self.replacement}")
                
                # Replace outliers
                df.loc[outliers[col], col] = replacement_value
        
        # Update metadata
        self.metadata = {
            'method': self.method,
            'threshold': self.threshold,
            'action': self.action,
            'columns': self.columns,
            'outlier_counts': outlier_counts,
            'total_outliers': total_outliers,
            'rows_before': len(data),
            'rows_after': len(df)
        }
        
        return df
    
    def _detect_zscore(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect outliers using the Z-score method.
        
        Parameters
        ----------
        df : pd.DataFrame
            The data
            
        Returns
        -------
        pd.DataFrame
            Boolean DataFrame with True for outliers
        """
        outliers = pd.DataFrame(False, index=df.index, columns=self.columns)
        
        for col in self.columns:
            # Calculate z-scores
            z_scores = np.abs(stats.zscore(df[col], nan_policy='omit'))
            
            # Mark outliers
            outliers[col] = z_scores > self.threshold
        
        return outliers
    
    def _detect_iqr(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect outliers using the IQR method.
        
        Parameters
        ----------
        df : pd.DataFrame
            The data
            
        Returns
        -------
        pd.DataFrame
            Boolean DataFrame with True for outliers
        """
        outliers = pd.DataFrame(False, index=df.index, columns=self.columns)
        
        for col in self.columns:
            # Calculate quartiles
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            
            # Calculate bounds
            lower_bound = q1 - self.threshold * iqr
            upper_bound = q3 + self.threshold * iqr
            
            # Mark outliers
            outliers[col] = (df[col] < lower_bound) | (df[col] > upper_bound)
        
        return outliers
    
    def _detect_isolation_forest(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect outliers using Isolation Forest.
        
        Parameters
        ----------
        df : pd.DataFrame
            The data
            
        Returns
        -------
        pd.DataFrame
            Boolean DataFrame with True for outliers
        """
        # Select only the columns to check
        X = df[self.columns]
        
        # Fit Isolation Forest
        clf = IsolationForest(contamination=self.threshold/100, random_state=42)
        y_pred = clf.fit_predict(X)
        
        # Convert predictions to outlier flags (-1 for outliers, 1 for inliers)
        outlier_flags = y_pred == -1
        
        # Create outlier DataFrame
        outliers = pd.DataFrame(False, index=df.index, columns=self.columns)
        
        # Mark all specified columns as outliers for the flagged rows
        for col in self.columns:
            outliers[col] = outlier_flags
        
        return outliers
    
    def _detect_lof(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect outliers using Local Outlier Factor.
        
        Parameters
        ----------
        df : pd.DataFrame
            The data
            
        Returns
        -------
        pd.DataFrame
            Boolean DataFrame with True for outliers
        """
        # Select only the columns to check
        X = df[self.columns]
        
        # Fit Local Outlier Factor
        clf = LocalOutlierFactor(n_neighbors=20, contamination=self.threshold/100)
        y_pred = clf.fit_predict(X)
        
        # Convert predictions to outlier flags (-1 for outliers, 1 for inliers)
        outlier_flags = y_pred == -1
        
        # Create outlier DataFrame
        outliers = pd.DataFrame(False, index=df.index, columns=self.columns)
        
        # Mark all specified columns as outliers for the flagged rows
        for col in self.columns:
            outliers[col] = outlier_flags
        
        return outliers
