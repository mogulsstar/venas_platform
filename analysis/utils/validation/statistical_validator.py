"""
Statistical validator for data validation.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union
from scipy import stats

from .base import ValidationRule, ValidationResult


class StatisticalValidator(ValidationRule):
    """
    Validation rule based on statistical tests.
    
    This validator performs statistical tests on the data and checks if they pass.
    """
    
    def __init__(self, rule_id: str, name: str, description: str, test_type: str,
                 column: str, **kwargs):
        """
        Initialize the statistical validator.
        
        Parameters
        ----------
        rule_id : str
            Identifier of the validation rule
        name : str
            Name of the validation rule
        description : str
            Description of the validation rule
        test_type : str
            Type of statistical test to perform
        column : str
            Column to validate
        **kwargs : dict
            Additional test-specific parameters:
            - alpha: float, significance level (default: 0.05)
            - distribution: str, distribution for normality test (default: 'norm')
            - reference_value: float, reference value for t-test
            - reference_column: str, reference column for paired t-test
        """
        super().__init__(rule_id, name, description, **kwargs)
        self.test_type = test_type
        self.column = column
        self.alpha = kwargs.get('alpha', 0.05)
        self.distribution = kwargs.get('distribution', 'norm')
        self.reference_value = kwargs.get('reference_value', None)
        self.reference_column = kwargs.get('reference_column', None)
    
    def validate(self, data: pd.DataFrame) -> ValidationResult:
        """
        Validate the data using statistical tests.
        
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
            If the test type is invalid or required parameters are missing
        """
        try:
            # Check if the column exists
            if self.column not in data.columns:
                raise ValueError(f"Column '{self.column}' not found in data")
            
            # Check if the column is numeric
            if not pd.api.types.is_numeric_dtype(data[self.column]):
                raise ValueError(f"Column '{self.column}' is not numeric")
            
            # Get the column data
            column_data = data[self.column].dropna()
            
            # Perform the statistical test
            if self.test_type == 'normality':
                # Normality test (Shapiro-Wilk)
                if len(column_data) < 3:
                    raise ValueError("Normality test requires at least 3 data points")
                
                statistic, p_value = stats.shapiro(column_data)
                passed = p_value > self.alpha
                
                details = {
                    'test': 'Shapiro-Wilk normality test',
                    'column': self.column,
                    'statistic': statistic,
                    'p_value': p_value,
                    'alpha': self.alpha,
                    'null_hypothesis': 'Data is normally distributed',
                    'interpretation': 'Fail to reject null hypothesis' if passed else 'Reject null hypothesis'
                }
                
            elif self.test_type == 'ttest_1samp':
                # One-sample t-test
                if self.reference_value is None:
                    raise ValueError("Reference value is required for one-sample t-test")
                
                statistic, p_value = stats.ttest_1samp(column_data, self.reference_value)
                passed = p_value > self.alpha
                
                details = {
                    'test': 'One-sample t-test',
                    'column': self.column,
                    'reference_value': self.reference_value,
                    'statistic': statistic,
                    'p_value': p_value,
                    'alpha': self.alpha,
                    'null_hypothesis': f'Mean equals {self.reference_value}',
                    'interpretation': 'Fail to reject null hypothesis' if passed else 'Reject null hypothesis'
                }
                
            elif self.test_type == 'ttest_paired':
                # Paired t-test
                if self.reference_column is None:
                    raise ValueError("Reference column is required for paired t-test")
                
                if self.reference_column not in data.columns:
                    raise ValueError(f"Reference column '{self.reference_column}' not found in data")
                
                if not pd.api.types.is_numeric_dtype(data[self.reference_column]):
                    raise ValueError(f"Reference column '{self.reference_column}' is not numeric")
                
                reference_data = data[self.reference_column].dropna()
                
                # Ensure both columns have the same length
                common_index = column_data.index.intersection(reference_data.index)
                column_data = column_data.loc[common_index]
                reference_data = reference_data.loc[common_index]
                
                statistic, p_value = stats.ttest_rel(column_data, reference_data)
                passed = p_value > self.alpha
                
                details = {
                    'test': 'Paired t-test',
                    'column': self.column,
                    'reference_column': self.reference_column,
                    'statistic': statistic,
                    'p_value': p_value,
                    'alpha': self.alpha,
                    'null_hypothesis': f'No difference between {self.column} and {self.reference_column}',
                    'interpretation': 'Fail to reject null hypothesis' if passed else 'Reject null hypothesis'
                }
                
            elif self.test_type == 'outliers':
                # Outlier test (Grubbs' test)
                if len(column_data) < 3:
                    raise ValueError("Outlier test requires at least 3 data points")
                
                # Calculate z-scores
                z_scores = np.abs(stats.zscore(column_data))
                
                # Check for outliers (z-score > 3)
                outliers = z_scores > 3
                passed = not outliers.any()
                
                # Get indices of outliers
                failed_indices = column_data.index[outliers].tolist()
                
                details = {
                    'test': 'Outlier test (z-score)',
                    'column': self.column,
                    'threshold': 3,
                    'outlier_count': outliers.sum(),
                    'total_count': len(column_data)
                }
                
                return ValidationResult(
                    rule_id=self.rule_id,
                    name=self.name,
                    description=self.description,
                    passed=passed,
                    details=details,
                    failed_indices=failed_indices
                )
                
            else:
                raise ValueError(f"Unknown test type: {self.test_type}")
            
            # Create validation result
            return ValidationResult(
                rule_id=self.rule_id,
                name=self.name,
                description=self.description,
                passed=passed,
                details=details
            )
                
        except Exception as e:
            # If there's an error, the validation fails
            return ValidationResult(
                rule_id=self.rule_id,
                name=self.name,
                description=self.description,
                passed=False,
                details={
                    'test_type': self.test_type,
                    'column': self.column,
                    'error': str(e)
                }
            )
