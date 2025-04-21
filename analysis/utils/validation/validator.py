"""
Main validator class for data validation.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union

from .base import ValidationRule, ValidationResult
from .expression_validator import ExpressionValidator
from .range_validator import RangeValidator
from .statistical_validator import StatisticalValidator


class Validator:
    """
    Main validator class for data validation.
    
    This class manages multiple validation rules and runs them on data.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the validator.
        
        Parameters
        ----------
        name : str
            Name of the validator
        description : str, optional
            Description of the validator
        """
        self.name = name
        self.description = description
        self.rules = []
    
    def add_rule(self, rule: ValidationRule) -> None:
        """
        Add a validation rule.
        
        Parameters
        ----------
        rule : ValidationRule
            Validation rule to add
        """
        self.rules.append(rule)
    
    def add_expression_rule(self, rule_id: str, name: str, description: str, expression: str, **kwargs) -> None:
        """
        Add an expression validation rule.
        
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
        rule = ExpressionValidator(rule_id, name, description, expression, **kwargs)
        self.add_rule(rule)
    
    def add_range_rule(self, rule_id: str, name: str, description: str, column: str,
                       min_value: Optional[float] = None, max_value: Optional[float] = None,
                       inclusive: bool = True, **kwargs) -> None:
        """
        Add a range validation rule.
        
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
        rule = RangeValidator(rule_id, name, description, column, min_value, max_value, inclusive, **kwargs)
        self.add_rule(rule)
    
    def add_statistical_rule(self, rule_id: str, name: str, description: str, test_type: str,
                             column: str, **kwargs) -> None:
        """
        Add a statistical validation rule.
        
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
            Additional test-specific parameters
        """
        rule = StatisticalValidator(rule_id, name, description, test_type, column, **kwargs)
        self.add_rule(rule)
    
    def validate(self, data: pd.DataFrame) -> Dict[str, ValidationResult]:
        """
        Validate the data using all rules.
        
        Parameters
        ----------
        data : pd.DataFrame
            The data to validate
            
        Returns
        -------
        Dict[str, ValidationResult]
            Results of all validations, keyed by rule ID
        """
        results = {}
        
        for rule in self.rules:
            result = rule.validate(data)
            results[rule.rule_id] = result
        
        return results
    
    def validate_and_summarize(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate the data and summarize the results.
        
        Parameters
        ----------
        data : pd.DataFrame
            The data to validate
            
        Returns
        -------
        Dict[str, Any]
            Summary of validation results
        """
        results = self.validate(data)
        
        # Count passed and failed rules
        passed_count = sum(1 for result in results.values() if result.passed)
        failed_count = len(results) - passed_count
        
        # Get failed rows
        failed_rows = set()
        for result in results.values():
            if not result.passed and result.failed_indices:
                failed_rows.update(result.failed_indices)
        
        # Create summary
        summary = {
            'validator_name': self.name,
            'validator_description': self.description,
            'total_rules': len(results),
            'passed_rules': passed_count,
            'failed_rules': failed_count,
            'pass_rate': passed_count / len(results) if results else 0,
            'failed_rows_count': len(failed_rows),
            'total_rows': len(data),
            'row_pass_rate': 1 - len(failed_rows) / len(data) if data.shape[0] > 0 else 0,
            'results': {rule_id: result.to_dict() for rule_id, result in results.items()}
        }
        
        return summary
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """
        Get all validation rules.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of validation rules as dictionaries
        """
        return [rule.get_metadata() for rule in self.rules]
