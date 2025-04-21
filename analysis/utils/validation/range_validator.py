"""
Range-based validator for data validation.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union

from .base import ValidationRule, ValidationResult


class RangeValidator(ValidationRule):
    """
    Validation rule based on value ranges.
    
    This validator checks if values in a column are within a specified range.
    """
    
    def __init__(self, rule_id: str, name: str, description: str, column: str,
                 min_value: Optional[float] = None, max_value: Optional[float] = None,
                 inclusive: bool = True, **kwargs):
        """
        Initialize the range validator.
        
        Parameters
        ----------
        rule_id : str
            Identifier of the validation rule
        name : str
            Name of the validation rule
        description : str
            Description of the validation rule
        column : str
            Column to validate
        min_value : float, optional
            Minimum allowed value
        max_value : float, optional
            Maximum allowed value
        inclusive : bool, default True
            Whether the range is inclusive
        **kwargs : dict
            Additional rule-specific parameters
        """
        super().__init__(rule_id, name, description, **kwargs)
        self.column = column
        self.min_value = min_value
        self.max_value = max_value
        self.inclusive = inclusive
    
    def validate(self, data: pd.DataFrame) -> ValidationResult:
        """
        Validate the data using the range check.
        
        Parameters
        ----------
        data : pd.DataFrame
            The data to validate
            
        Returns
        -------
        ValidationResult
            Result of the validation
            
        Raises
        ------
        ValueError
            If the column is not found or not numeric
        """
        try:
            # Check if the column exists
            if self.column not in data.columns:
                raise ValueError(f"Column '{self.column}' not found in data")
            
            # Check if the column is numeric
            if not pd.api.types.is_numeric_dtype(data[self.column]):
                raise ValueError(f"Column '{self.column}' is not numeric")
            
            # Get the column data
            column_data = data[self.column]
            
            # Check the range
            if self.min_value is not None and self.max_value is not None:
                # Both min and max are specified
                if self.inclusive:
                    mask = (column_data >= self.min_value) & (column_data <= self.max_value)
                else:
                    mask = (column_data > self.min_value) & (column_data < self.max_value)
                
                range_str = f"[{self.min_value}, {self.max_value}]" if self.inclusive else f"({self.min_value}, {self.max_value})"
                
            elif self.min_value is not None:
                # Only min is specified
                if self.inclusive:
                    mask = column_data >= self.min_value
                else:
                    mask = column_data > self.min_value
                
                range_str = f"[{self.min_value}, inf)" if self.inclusive else f"({self.min_value}, inf)"
                
            elif self.max_value is not None:
                # Only max is specified
                if self.inclusive:
                    mask = column_data <= self.max_value
                else:
                    mask = column_data < self.max_value
                
                range_str = f"(-inf, {self.max_value}]" if self.inclusive else f"(-inf, {self.max_value})"
                
            else:
                # Neither min nor max is specified
                mask = pd.Series(True, index=column_data.index)
                range_str = "(-inf, inf)"
            
            # Check if all values are within the range
            all_passed = mask.all()
            
            # Get indices of failed rows
            failed_indices = column_data[~mask].index.tolist()
            
            # Create validation result
            return ValidationResult(
                rule_id=self.rule_id,
                name=self.name,
                description=self.description,
                passed=all_passed,
                details={
                    'column': self.column,
                    'range': range_str,
                    'min_value': self.min_value,
                    'max_value': self.max_value,
                    'inclusive': self.inclusive,
                    'failed_count': len(failed_indices),
                    'total_count': len(data)
                },
                failed_indices=failed_indices
            )
                
        except Exception as e:
            # If there's an error, the validation fails
            return ValidationResult(
                rule_id=self.rule_id,
                name=self.name,
                description=self.description,
                passed=False,
                details={
                    'column': self.column,
                    'min_value': self.min_value,
                    'max_value': self.max_value,
                    'inclusive': self.inclusive,
                    'error': str(e)
                }
            )
