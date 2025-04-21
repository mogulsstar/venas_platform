"""
Line chart visualization.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Tuple

from .base import Visualization


class LineChart(Visualization):
    """
    Line chart visualization.
    
    This visualization displays data as a series of points connected by lines.
    It is useful for showing trends over time or continuous data.
    """
    
    def __init__(self, title: str = "", description: str = "", **kwargs):
        """
        Initialize the line chart.
        
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
            - colors: list, colors for each line
            - line_styles: list, line styles for each line
            - markers: list, markers for each line
            - show_points: bool, whether to show points
            - show_legend: bool, whether to show legend
            - grid: bool, whether to show grid
            - x_min: float, minimum value for x-axis
            - x_max: float, maximum value for x-axis
            - y_min: float, minimum value for y-axis
            - y_max: float, maximum value for y-axis
            - annotations: list, annotations to add to the chart
        """
        super().__init__(title, description, **kwargs)
        self.x_column = kwargs.get('x_column')
        self.y_columns = kwargs.get('y_columns', [])
        self.x_label = kwargs.get('x_label', '')
        self.y_label = kwargs.get('y_label', '')
        self.colors = kwargs.get('colors', [])
        self.line_styles = kwargs.get('line_styles', [])
        self.markers = kwargs.get('markers', [])
        self.show_points = kwargs.get('show_points', True)
        self.show_legend = kwargs.get('show_legend', True)
        self.grid = kwargs.get('grid', True)
        self.x_min = kwargs.get('x_min')
        self.x_max = kwargs.get('x_max')
        self.y_min = kwargs.get('y_min')
        self.y_max = kwargs.get('y_max')
        self.annotations = kwargs.get('annotations', [])
    
    def generate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate the line chart.
        
        Parameters
        ----------
        data : pd.DataFrame
            The data to visualize
            
        Returns
        -------
        Dict[str, Any]
            Line chart data in a format suitable for frontend rendering
            
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
        
        # Prepare data
        chart_data = {
            'x': data[self.x_column].tolist(),
            'series': []
        }
        
        # Add each y column as a series
        for i, y_column in enumerate(self.y_columns):
            # Get color, line style, and marker
            color = self.colors[i] if i < len(self.colors) else None
            line_style = self.line_styles[i] if i < len(self.line_styles) else 'solid'
            marker = self.markers[i] if i < len(self.markers) else 'circle'
            
            # Create series
            series = {
                'name': y_column,
                'data': data[y_column].tolist(),
                'type': 'line',
                'showSymbol': self.show_points,
                'lineStyle': {'type': line_style}
            }
            
            # Add color if specified
            if color:
                series['itemStyle'] = {'color': color}
            
            # Add marker if specified
            if marker:
                series['symbol'] = marker
            
            chart_data['series'].append(series)
        
        # Add annotations
        if self.annotations:
            chart_data['annotations'] = self.annotations
        
        # Add axis configuration
        chart_data['xAxis'] = {
            'name': self.x_label or self.x_column,
            'min': self.x_min,
            'max': self.x_max,
            'type': 'category' if pd.api.types.is_categorical_dtype(data[self.x_column]) else 'value'
        }
        
        chart_data['yAxis'] = {
            'name': self.y_label,
            'min': self.y_min,
            'max': self.y_max
        }
        
        # Add grid configuration
        chart_data['grid'] = {
            'show': self.grid
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
            'trigger': 'axis'
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
            'type': 'line_chart',
            'x_column': self.x_column,
            'y_columns': self.y_columns,
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
        return 'line_chart'
