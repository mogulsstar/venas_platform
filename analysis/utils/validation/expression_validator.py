"""
Expression-based validator for data validation.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union
import re

from .base import ValidationRule, ValidationResult


class ExpressionValidator(ValidationRule):
    """
    Validation rule based on expressions.
    
    This validator evaluates expressions on the data and checks if they are true.
    Expressions can use column names, comparison operators, and logical operators.
    """
    
    def __init__(self, rule_id: str, name: str, description: str, expression: str, **kwargs):
        """
        Initialize the expression validator.
        
        Parameters
        ----------
        rule_id : str
            Identifier of the validation rule
        name : str
            Name of the validation rule
        description : str
            Description of the validation rule
        expression : str
            Expression to evaluate
        **kwargs : dict
            Additional rule-specific parameters
        """
        super().__init__(rule_id, name, description, **kwargs)
        self.expression = expression
    
    def validate(self, data: pd.DataFrame) -> ValidationResult:
        """
        Validate the data using the expression.
        
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
            If the expression is invalid
        """
        try:
            # Parse the expression
            parsed_expr = self._parse_expression(self.expression, data)
            
            # Evaluate the expression
            result = eval(parsed_expr, {"__builtins__": {}}, {"df": data, "np": np})
            
            # Check if the result is a Series or DataFrame
            if isinstance(result, (pd.Series, pd.DataFrame)):
                # If it's a Series or DataFrame, check if all values are True
                all_passed = result.all().all()
                
                # Get indices of failed rows
                if isinstance(result, pd.Series):
                    failed_indices = result[~result].index.tolist()
                else:
                    # For DataFrame, get rows where any column is False
                    failed_indices = result[~result.all(axis=1)].index.tolist()
                
                # Create validation result
                return ValidationResult(
                    rule_id=self.rule_id,
                    name=self.name,
                    description=self.description,
                    passed=all_passed,
                    details={
                        'expression': self.expression,
                        'parsed_expression': parsed_expr,
                        'failed_count': len(failed_indices),
                        'total_count': len(data)
                    },
                    failed_indices=failed_indices
                )
            else:
                # If it's a scalar, check if it's True
                return ValidationResult(
                    rule_id=self.rule_id,
                    name=self.name,
                    description=self.description,
                    passed=bool(result),
                    details={
                        'expression': self.expression,
                        'parsed_expression': parsed_expr,
                        'result': result
                    }
                )
                
        except Exception as e:
            # If there's an error, the validation fails
            return ValidationResult(
                rule_id=self.rule_id,
                name=self.name,
                description=self.description,
                passed=False,
                details={
                    'expression': self.expression,
                    'error': str(e)
                }
            )
    
    def _parse_expression(self, expression: str, data: pd.DataFrame) -> str:
        """
        Parse the expression to make it safe for evaluation.
        
        Parameters
        ----------
        expression : str
            Expression to parse
        data : pd.DataFrame
            The data to validate
            
        Returns
        -------
        str
            Parsed expression
            
        Raises
        ------
        ValueError
            If the expression is invalid
        """
        # Replace column names with df['column_name']
        for col in data.columns:
            # Escape special characters in column name
            escaped_col = re.escape(col)
            # Replace column name with df['column_name']
            expression = re.sub(
                r'\b' + escaped_col + r'\b',
                f"df['{col}']",
                expression
            )
        
        # Replace logical operators
        expression = expression.replace(' AND ', ' and ')
        expression = expression.replace(' OR ', ' or ')
        expression = expression.replace(' NOT ', ' not ')
        
        # Replace comparison operators
        expression = expression.replace('==', '==')  # Already correct
        expression = expression.replace('!=', '!=')  # Already correct
        expression = expression.replace('>=', '>=')  # Already correct
        expression = expression.replace('<=', '<=')  # Already correct
        expression = expression.replace('>', '>')    # Already correct
        expression = expression.replace('<', '<')    # Already correct
        
        # Replace mathematical functions
        expression = expression.replace('SQRT', 'np.sqrt')
        expression = expression.replace('ABS', 'np.abs')
        expression = expression.replace('SIN', 'np.sin')
        expression = expression.replace('COS', 'np.cos')
        expression = expression.replace('TAN', 'np.tan')
        expression = expression.replace('EXP', 'np.exp')
        expression = expression.replace('LOG', 'np.log')
        expression = expression.replace('LOG10', 'np.log10')
        
        # Replace statistical functions
        expression = expression.replace('MEAN', 'np.mean')
        expression = expression.replace('MEDIAN', 'np.median')
        expression = expression.replace('STD', 'np.std')
        expression = expression.replace('MIN', 'np.min')
        expression = expression.replace('MAX', 'np.max')
        
        return expression
