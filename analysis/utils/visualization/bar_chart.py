"""
Bar chart visualization.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Tuple

from .base import Visualization


class BarChart(Visualization):
    """
    Bar chart visualization.
    
    This visualization displays data as rectangular bars with heights proportional to the values.
    It is useful for comparing discrete categories.
    """
    
    def __init__(self, title: str = "", description: str = "", **kwargs):
        """
        Initialize the bar chart.
        
        Parameters
        ----------
        title : str, optional
            Title of the visualization
        description : str, optional
            Description of the visualization
        **kwargs : dict
            Additional visualization-specific parameters:
            - x_column: str, column to use for x-axis
            - y_columns: list, columns to use for y-axis
            - x_label: str, label for x-axis
            - y_label: str, label for y-axis
            - colors: list, colors for each bar series
            - orientation: str, orientation of the bars ('vertical' or 'horizontal')
            - stack: bool, whether to stack the bars
            - show_values: bool, whether to show values on bars
            - show_legend: bool, whether to show legend
            - grid: bool, whether to show grid
            - sort_by: str, column to sort by
            - sort_order: str, sort order ('ascending' or 'descending')
            - top_n: int, number of top values to show
            - annotations: list, annotations to add to the chart
        """
        super().__init__(title, description, **kwargs)
        self.x_column = kwargs.get('x_column')
        self.y_columns = kwargs.get('y_columns', [])
        self.x_label = kwargs.get('x_label', '')
        self.y_label = kwargs.get('y_label', '')
        self.colors = kwargs.get('colors', [])
        self.orientation = kwargs.get('orientation', 'vertical')
        self.stack = kwargs.get('stack', False)
        self.show_values = kwargs.get('show_values', False)
        self.show_legend = kwargs.get('show_legend', True)
        self.grid = kwargs.get('grid', True)
        self.sort_by = kwargs.get('sort_by')
        self.sort_order = kwargs.get('sort_order', 'descending')
        self.top_n = kwargs.get('top_n')
        self.annotations = kwargs.get('annotations', [])
    
    def generate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate the bar chart.
        
        Parameters
        ----------
        data : pd.DataFrame
            The data to visualize
            
        Returns
        -------
        Dict[str, Any]
            Bar chart data in a format suitable for frontend rendering
            
        Raises
        ------
        ValueError
            If required parameters are missing or invalid
        """
        # Validate parameters
        if not self.x_column:
            raise ValueError("x_column is required")
        
        if not self.y_columns:
            raise ValueError("y_columns is required")
        
        if self.x_column not in data.columns:
            raise ValueError(f"x_column '{self.x_column}' not found in data")
        
        missing_columns = [col for col in self.y_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"y_columns {missing_columns} not found in data")
        
        # Sort data if requested
        if self.sort_by:
            sort_column = self.sort_by
            if sort_column not in data.columns:
                raise ValueError(f"sort_by column '{sort_column}' not found in data")
            
            ascending = self.sort_order == 'ascending'
            data = data.sort_values(by=sort_column, ascending=ascending)
        
        # Limit to top N if requested
        if self.top_n and self.top_n > 0:
            data = data.head(self.top_n)
        
        # Prepare data
        chart_data = {
            'series': []
        }
        
        # Set x-axis categories
        categories = data[self.x_column].tolist()
        
        # Add each y column as a series
        for i, y_column in enumerate(self.y_columns):
            # Get color
            color = self.colors[i] if i < len(self.colors) else None
            
            # Create series
            series = {
                'name': y_column,
                'data': data[y_column].tolist(),
                'type': 'bar',
                'stack': 'stack' if self.stack else None,
                'label': {
                    'show': self.show_values,
                    'position': 'top' if self.orientation == 'vertical' else 'right'
                }
            }
            
            # Add color if specified
            if color:
                series['itemStyle'] = {'color': color}
            
            chart_data['series'].append(series)
        
        # Add annotations
        if self.annotations:
            chart_data['annotations'] = self.annotations
        
        # Set axis configuration based on orientation
        if self.orientation == 'vertical':
            chart_data['xAxis'] = {
                'type': 'category',
                'data': categories,
                'name': self.x_label or self.x_column,
                'axisLabel': {
                    'rotate': 45 if len(categories) > 10 else 0
                }
            }
            
            chart_data['yAxis'] = {
                'type': 'value',
                'name': self.y_label
            }
        else:  # horizontal
            chart_data['yAxis'] = {
                'type': 'category',
                'data': categories,
                'name': self.x_label or self.x_column
            }
            
            chart_data['xAxis'] = {
                'type': 'value',
                'name': self.y_label
            }
        
        # Add grid configuration
        chart_data['grid'] = {
            'show': self.grid,
            'containLabel': True,
            'left': '3%',
            'right': '4%',
            'bottom': '3%'
        }
        
        # Add legend configuration
        chart_data['legend'] = {
            'show': self.show_legend
        }
        
        # Add title and description
        chart_data['title'] = {
            'text': self.title,
            'subtext': self.description
        }
        
        # Add tooltip configuration
        chart_data['tooltip'] = {
            'trigger': 'axis',
            'axisPointer': {
                'type': 'shadow'
            }
        }
        
        # Add toolbox configuration
        chart_data['toolbox'] = {
            'feature': {
                'saveAsImage': {},
                'dataZoom': {},
                'dataView': {},
                'restore': {}
            }
        }
        
        # Update metadata
        self.metadata = {
            'type': 'bar_chart',
            'x_column': self.x_column,
            'y_columns': self.y_columns,
            'orientation': self.orientation,
            'stack': self.stack,
            'data_points': len(data)
        }
        
        return {
            'type': 'echarts',
            'data': chart_data,
            'metadata': self.get_metadata()
        }
    
    def get_type(self) -> str:
        """
        Get the type of visualization.
        
        Returns
        -------
        str
            Type of visualization
        """
        return 'bar_chart'
