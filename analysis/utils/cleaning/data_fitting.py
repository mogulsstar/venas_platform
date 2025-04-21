"""
Data fitting utilities for data cleaning.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Tuple
from sklearn.linear_model import LinearRegression, RANSACRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

from .base import DataCleaner


class DataFitting(DataCleaner):
    """
    Data cleaner for fitting data and creating new columns.
    
    This cleaner provides functionality to:
    - Identify linear segments in data
    - Fit polynomial models to data
    - Create new columns with fitted values
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the data fitting cleaner.
        
        Parameters
        ----------
        **kwargs : dict
            Additional cleaner-specific parameters:
            - x_column: str, column to use as x values
            - y_column: str, column to use as y values
            - degree: int, polynomial degree (default: 1)
            - method: str, fitting method ('linear', 'polynomial', 'ransac')
            - segment_detection: bool, whether to detect segments (default: False)
            - min_segment_size: int, minimum segment size (default: 10)
            - output_column: str, name of the output column (default: None)
            - residuals_column: str, name of the residuals column (default: None)
        """
        super().__init__(**kwargs)
        self.x_column = kwargs.get('x_column')
        self.y_column = kwargs.get('y_column')
        self.degree = kwargs.get('degree', 1)
        self.method = kwargs.get('method', 'linear')
        self.segment_detection = kwargs.get('segment_detection', False)
        self.min_segment_size = kwargs.get('min_segment_size', 10)
        self.output_column = kwargs.get('output_column')
        self.residuals_column = kwargs.get('residuals_column')
        
        # Model and segments will be set during fitting
        self.model = None
        self.segments = []
        self.coefficients = []
    
    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the data by fitting models and creating new columns.
        
        Parameters
        ----------
        data : pd.DataFrame
            The data to clean
            
        Returns
        -------
        pd.DataFrame
            The cleaned data with new columns
            
        Raises
        ------
        ValueError
            If required parameters are missing or invalid
        """
        # Make a copy of the data to avoid modifying the original
        df = data.copy()
        
        # Validate parameters
        if not self.x_column or not self.y_column:
            raise ValueError("x_column and y_column are required")
        
        if self.x_column not in df.columns:
            raise ValueError(f"x_column '{self.x_column}' not found in data")
        
        if self.y_column not in df.columns:
            raise ValueError(f"y_column '{self.y_column}' not found in data")
        
        # Get x and y values
        x = df[self.x_column].values.reshape(-1, 1)
        y = df[self.y_column].values
        
        # Detect segments if requested
        if self.segment_detection:
            segments = self._detect_segments(x, y)
            self.segments = segments
            
            # Fit models to each segment
            fitted_values = np.zeros_like(y)
            segment_indices = np.zeros_like(y, dtype=int)
            
            for i, (start, end) in enumerate(segments):
                segment_x = x[start:end]
                segment_y = y[start:end]
                
                # Fit model to segment
                model, coef = self._fit_model(segment_x, segment_y)
                
                # Store coefficients
                self.coefficients.append(coef)
                
                # Predict values
                segment_fitted = model.predict(segment_x)
                
                # Store fitted values
                fitted_values[start:end] = segment_fitted
                segment_indices[start:end] = i + 1
            
            # Create output columns
            if self.output_column:
                df[self.output_column] = fitted_values
            
            # Create residuals column
            if self.residuals_column:
                df[self.residuals_column] = y - fitted_values
            
            # Create segment column
            df[f"{self.y_column}_segment"] = segment_indices
            
        else:
            # Fit a single model to all data
            model, coef = self._fit_model(x, y)
            self.model = model
            self.coefficients = [coef]
            
            # Predict values
            fitted_values = model.predict(x)
            
            # Create output column
            if self.output_column:
                df[self.output_column] = fitted_values
            else:
                df[f"{self.y_column}_fitted"] = fitted_values
            
            # Create residuals column
            if self.residuals_column:
                df[self.residuals_column] = y - fitted_values
            else:
                df[f"{self.y_column}_residuals"] = y - fitted_values
        
        # Update metadata
        self.metadata = {
            'x_column': self.x_column,
            'y_column': self.y_column,
            'method': self.method,
            'degree': self.degree,
            'segment_detection': self.segment_detection,
            'segments': len(self.segments) if self.segment_detection else 1,
            'coefficients': self.coefficients,
            'output_column': self.output_column or f"{self.y_column}_fitted",
            'residuals_column': self.residuals_column or f"{self.y_column}_residuals"
        }
        
        return df
    
    def _fit_model(self, x: np.ndarray, y: np.ndarray) -> Tuple[Any, List[float]]:
        """
        Fit a model to the data.
        
        Parameters
        ----------
        x : np.ndarray
            X values
        y : np.ndarray
            Y values
            
        Returns
        -------
        Tuple[Any, List[float]]
            (fitted model, coefficients)
        """
        if self.method == 'linear':
            # Linear regression
            model = LinearRegression()
            model.fit(x, y)
            coef = [model.intercept_] + model.coef_.tolist()
            
        elif self.method == 'polynomial':
            # Polynomial regression
            model = make_pipeline(
                PolynomialFeatures(degree=self.degree),
                LinearRegression()
            )
            model.fit(x, y)
            
            # Extract coefficients
            linear_model = model.steps[1][1]
            poly_features = model.steps[0][1]
            coef = linear_model.coef_.tolist()
            
        elif self.method == 'ransac':
            # RANSAC regression (robust to outliers)
            model = RANSACRegressor(LinearRegression())
            model.fit(x, y)
            
            # Extract coefficients
            linear_model = model.estimator_
            coef = [linear_model.intercept_] + linear_model.coef_.tolist()
            
        else:
            raise ValueError(f"Unknown fitting method: {self.method}")
        
        return model, coef
    
    def _detect_segments(self, x: np.ndarray, y: np.ndarray) -> List[Tuple[int, int]]:
        """
        Detect linear segments in the data.
        
        Parameters
        ----------
        x : np.ndarray
            X values
        y : np.ndarray
            Y values
            
        Returns
        -------
        List[Tuple[int, int]]
            List of (start, end) indices for each segment
        """
        n = len(x)
        if n < self.min_segment_size * 2:
            # If data is too small, return a single segment
            return [(0, n)]
        
        # Initialize segments
        segments = []
        
        # Use a sliding window approach to detect segments
        start = 0
        while start < n - self.min_segment_size:
            # Find the longest segment starting at 'start'
            best_end = start + self.min_segment_size
            best_score = float('inf')
            
            for end in range(start + self.min_segment_size, n + 1):
                # Fit a model to the current segment
                segment_x = x[start:end]
                segment_y = y[start:end]
                
                model = LinearRegression()
                model.fit(segment_x, segment_y)
                
                # Calculate mean squared error
                y_pred = model.predict(segment_x)
                mse = np.mean((segment_y - y_pred) ** 2)
                
                # Calculate R-squared
                r2 = model.score(segment_x, segment_y)
                
                # Calculate score (lower is better)
                # We want high R-squared and low MSE
                score = mse / (r2 + 0.001)  # Avoid division by zero
                
                # Check if this is the best segment so far
                if score < best_score:
                    best_score = score
                    best_end = end
                elif end - start > self.min_segment_size * 2:
                    # If score is not improving for a while, stop
                    break
            
            # Add the best segment
            segments.append((start, best_end))
            
            # Move to the next segment
            start = best_end
        
        # If the last segment doesn't reach the end, add a final segment
        if segments[-1][1] < n:
            segments.append((segments[-1][1], n))
        
        return segments
    
    def get_segments(self) -> List[Tuple[int, int]]:
        """
        Get the detected segments.
        
        Returns
        -------
        List[Tuple[int, int]]
            List of (start, end) indices for each segment
        """
        return self.segments
    
    def get_coefficients(self) -> List[List[float]]:
        """
        Get the coefficients of the fitted models.
        
        Returns
        -------
        List[List[float]]
            List of coefficients for each segment
        """
        return self.coefficients
