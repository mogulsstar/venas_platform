"""
Pie chart visualization.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Tuple

from .base import Visualization


class PieChart(Visualization):
    """
    Pie chart visualization.
    
    This visualization displays data as slices of a circle.
    It is useful for showing the proportion of categories in a dataset.
    """
    
    def __init__(self, title: str = "", description: str = "", **kwargs):
        """
        Initialize the pie chart.
        
        Parameters
        ----------
        title : str, optional
            Title of the visualization
        description : str, optional
            Description of the visualization
        **kwargs : dict
            Additional visualization-specific parameters:
            - category_column: str, column to use for categories
            - value_column: str, column to use for values
            - colors: list, colors for each slice
            - show_labels: bool, whether to show labels
            - show_values: bool, whether to show values
            - show_percentages: bool, whether to show percentages
            - donut: bool, whether to show as donut chart
            - donut_radius: list, inner and outer radius for donut chart
            - sort_by: str, how to sort slices ('value', 'name', 'none')
            - sort_order: str, sort order ('ascending', 'descending')
            - top_n: int, number of top categories to show
            - other_category: str, name for 'other' category
            - annotations: list, annotations to add to the chart
        """
        super().__init__(title, description, **kwargs)
        self.category_column = kwargs.get('category_column')
        self.value_column = kwargs.get('value_column')
        self.colors = kwargs.get('colors', [])
        self.show_labels = kwargs.get('show_labels', True)
        self.show_values = kwargs.get('show_values', True)
        self.show_percentages = kwargs.get('show_percentages', True)
        self.donut = kwargs.get('donut', False)
        self.donut_radius = kwargs.get('donut_radius', ['40%', '70%'])
        self.sort_by = kwargs.get('sort_by', 'value')
        self.sort_order = kwargs.get('sort_order', 'descending')
        self.top_n = kwargs.get('top_n')
        self.other_category = kwargs.get('other_category', 'Other')
        self.annotations = kwargs.get('annotations', [])
    
    def generate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate the pie chart.
        
        Parameters
        ----------
        data : pd.DataFrame
            The data to visualize
            
        Returns
        -------
        Dict[str, Any]
            Pie chart data in a format suitable for frontend rendering
            
        Raises
        ------
        ValueError
            If required parameters are missing or invalid
        """
        # Validate parameters
        if not self.category_column:
            raise ValueError("category_column is required")
        
        if self.category_column not in data.columns:
            raise ValueError(f"category_column '{self.category_column}' not found in data")
        
        # Prepare data
        if self.value_column:
            if self.value_column not in data.columns:
                raise ValueError(f"value_column '{self.value_column}' not found in data")
            
            # Group by category and sum values
            grouped_data = data.groupby(self.category_column)[self.value_column].sum().reset_index()
        else:
            # Count occurrences of each category
            grouped_data = data[self.category_column].value_counts().reset_index()
            grouped_data.columns = [self.category_column, 'count']
            self.value_column = 'count'
        
        # Sort data
        if self.sort_by == 'value':
            ascending = self.sort_order == 'ascending'
            grouped_data = grouped_data.sort_values(by=self.value_column, ascending=ascending)
        elif self.sort_by == 'name':
            ascending = self.sort_order == 'ascending'
            grouped_data = grouped_data.sort_values(by=self.category_column, ascending=ascending)
        
        # Limit to top N categories if specified
        if self.top_n and self.top_n > 0 and self.top_n < len(grouped_data):
            if self.sort_by == 'value':
                # Take top N by value
                ascending = self.sort_order != 'ascending'  # Reverse for top N
                top_data = grouped_data.sort_values(by=self.value_column, ascending=ascending).head(self.top_n)
                
                # Combine remaining categories into 'Other'
                other_data = grouped_data.sort_values(by=self.value_column, ascending=ascending).iloc[self.top_n:]
                other_value = other_data[self.value_column].sum()
                
                # Add 'Other' category
                other_row = pd.DataFrame({
                    self.category_column: [self.other_category],
                    self.value_column: [other_value]
                })
                
                # Combine top categories and 'Other'
                grouped_data = pd.concat([top_data, other_row], ignore_index=True)
                
                # Sort again
                ascending = self.sort_order == 'ascending'
                grouped_data = grouped_data.sort_values(by=self.value_column, ascending=ascending)
            else:
                # Take top N categories
                grouped_data = grouped_data.head(self.top_n)
        
        # Calculate percentages
        total = grouped_data[self.value_column].sum()
        grouped_data['percentage'] = grouped_data[self.value_column] / total * 100
        
        # Prepare pie data
        pie_data = []
        for _, row in grouped_data.iterrows():
            pie_data.append({
                'name': str(row[self.category_column]),
                'value': float(row[self.value_column]),
                'percentage': float(row['percentage'])
            })
        
        # Prepare chart data
        chart_data = {
            'series': [
                {
                    'name': self.category_column,
                    'type': 'pie',
                    'data': pie_data,
                    'radius': self.donut_radius if self.donut else '70%',
                    'center': ['50%', '50%'],
                    'label': {
                        'show': self.show_labels,
                        'formatter': self._get_label_formatter()
                    },
                    'emphasis': {
                        'itemStyle': {
                            'shadowBlur': 10,
                            'shadowOffsetX': 0,
                            'shadowColor': 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }
            ]
        }
        
        # Add colors if specified
        if self.colors:
            chart_data['color'] = self.colors
        
        # Add annotations
        if self.annotations:
            chart_data['annotations'] = self.annotations
        
        # Add legend configuration
        chart_data['legend'] = {
            'orient': 'vertical',
            'left': 'left',
            'type': 'scroll'
        }
        
        # Add title and description
        chart_data['title'] = {
            'text': self.title or f'Distribution of {self.category_column}',
            'subtext': self.description,
            'left': 'center'
        }
        
        # Add tooltip configuration
        chart_data['tooltip'] = {
            'trigger': 'item',
            'formatter': self._get_tooltip_formatter()
        }
        
        # Add toolbox configuration
        chart_data['toolbox'] = {
            'feature': {
                'saveAsImage': {},
                'dataView': {},
                'restore': {}
            }
        }
        
        # Update metadata
        self.metadata = {
            'type': 'pie_chart',
            'category_column': self.category_column,
            'value_column': self.value_column,
            'donut': self.donut,
            'categories': len(pie_data),
            'total': float(total)
        }
        
        return {
            'type': 'echarts',
            'data': chart_data,
            'metadata': self.get_metadata()
        }
    
    def _get_label_formatter(self) -> str:
        """
        Get the label formatter based on configuration.
        
        Returns
        -------
        str
            Label formatter string
        """
        if self.show_labels and self.show_percentages and self.show_values:
            return '{b}: {c} ({d}%)'
        elif self.show_labels and self.show_percentages:
            return '{b}: {d}%'
        elif self.show_labels and self.show_values:
            return '{b}: {c}'
        elif self.show_percentages and self.show_values:
            return '{c} ({d}%)'
        elif self.show_labels:
            return '{b}'
        elif self.show_percentages:
            return '{d}%'
        elif self.show_values:
            return '{c}'
        else:
            return ''
    
    def _get_tooltip_formatter(self) -> str:
        """
        Get the tooltip formatter.
        
        Returns
        -------
        str
            Tooltip formatter string
        """
        return (
            f'{{a}}<br>'
            f'{{b}}: {{c}} ({self.value_column})<br>'
            f'Percentage: {{d}}%'
        )
    
    def get_type(self) -> str:
        """
        Get the type of visualization.
        
        Returns
        -------
        str
            Type of visualization
        """
        return 'pie_chart'
