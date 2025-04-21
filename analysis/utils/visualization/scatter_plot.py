"""
Scatter plot visualization.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Tuple

from .base import Visualization


class ScatterPlot(Visualization):
    """
    Scatter plot visualization.
    
    This visualization displays data as points on a Cartesian coordinate system.
    It is useful for showing the relationship between two variables.
    """
    
    def __init__(self, title: str = "", description: str = "", **kwargs):
        """
        Initialize the scatter plot.
        
        Parameters
        ----------
        title : str, optional
            Title of the visualization
        description : str, optional
            Description of the visualization
        **kwargs : dict
            Additional visualization-specific parameters:
            - x_column: str, column to use for x-axis
            - y_column: str, column to use for y-axis
            - color_column: str, column to use for point colors
            - size_column: str, column to use for point sizes
            - x_label: str, label for x-axis
            - y_label: str, label for y-axis
            - color_label: str, label for color legend
            - size_label: str, label for size legend
            - color_map: str, color map to use
            - size_range: list, range of point sizes [min, max]
            - show_trend_line: bool, whether to show trend line
            - trend_line_type: str, type of trend line ('linear', 'polynomial', 'exponential')
            - trend_line_degree: int, degree of polynomial trend line
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
        self.y_column = kwargs.get('y_column')
        self.color_column = kwargs.get('color_column')
        self.size_column = kwargs.get('size_column')
        self.x_label = kwargs.get('x_label', '')
        self.y_label = kwargs.get('y_label', '')
        self.color_label = kwargs.get('color_label', '')
        self.size_label = kwargs.get('size_label', '')
        self.color_map = kwargs.get('color_map', 'viridis')
        self.size_range = kwargs.get('size_range', [4, 20])
        self.show_trend_line = kwargs.get('show_trend_line', False)
        self.trend_line_type = kwargs.get('trend_line_type', 'linear')
        self.trend_line_degree = kwargs.get('trend_line_degree', 2)
        self.show_legend = kwargs.get('show_legend', True)
        self.grid = kwargs.get('grid', True)
        self.x_min = kwargs.get('x_min')
        self.x_max = kwargs.get('x_max')
        self.y_min = kwargs.get('y_min')
        self.y_max = kwargs.get('y_max')
        self.annotations = kwargs.get('annotations', [])
    
    def generate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate the scatter plot.
        
        Parameters
        ----------
        data : pd.DataFrame
            The data to visualize
            
        Returns
        -------
        Dict[str, Any]
            Scatter plot data in a format suitable for frontend rendering
            
        Raises
        ------
        ValueError
            If required parameters are missing or invalid
        """
        # Validate parameters
        if not self.x_column:
            raise ValueError("x_column is required")
        
        if not self.y_column:
            raise ValueError("y_column is required")
        
        if self.x_column not in data.columns:
            raise ValueError(f"x_column '{self.x_column}' not found in data")
        
        if self.y_column not in data.columns:
            raise ValueError(f"y_column '{self.y_column}' not found in data")
        
        if self.color_column and self.color_column not in data.columns:
            raise ValueError(f"color_column '{self.color_column}' not found in data")
        
        if self.size_column and self.size_column not in data.columns:
            raise ValueError(f"size_column '{self.size_column}' not found in data")
        
        # Prepare data
        chart_data = {
            'series': []
        }
        
        # Create main scatter series
        scatter_data = []
        for i, row in data.iterrows():
            point = [row[self.x_column], row[self.y_column]]
            
            # Add color value if specified
            if self.color_column:
                point.append(row[self.color_column])
            
            # Add size value if specified
            if self.size_column:
                size_value = row[self.size_column]
                # Scale size to the specified range
                size = self.size_range[0] + (self.size_range[1] - self.size_range[0]) * (
                    (size_value - data[self.size_column].min()) / 
                    (data[self.size_column].max() - data[self.size_column].min())
                ) if data[self.size_column].max() > data[self.size_column].min() else self.size_range[0]
                point.append(size)
            
            scatter_data.append(point)
        
        # Create scatter series
        scatter_series = {
            'name': f"{self.y_column} vs {self.x_column}",
            'type': 'scatter',
            'data': scatter_data,
            'symbolSize': self.size_column is not None,  # Use symbolSize function if size_column is specified
            'itemStyle': {}
        }
        
        # Add color mapping if specified
        if self.color_column:
            scatter_series['visualMap'] = {
                'show': True,
                'dimension': 2,  # The third dimension (index 2) is the color value
                'min': data[self.color_column].min(),
                'max': data[self.color_column].max(),
                'text': [self.color_label or self.color_column],
                'inRange': {
                    'color': self._get_color_map(self.color_map)
                }
            }
        
        chart_data['series'].append(scatter_series)
        
        # Add trend line if requested
        if self.show_trend_line:
            trend_line = self._calculate_trend_line(data)
            if trend_line:
                chart_data['series'].append(trend_line)
        
        # Add annotations
        if self.annotations:
            chart_data['annotations'] = self.annotations
        
        # Add axis configuration
        chart_data['xAxis'] = {
            'name': self.x_label or self.x_column,
            'min': self.x_min,
            'max': self.x_max,
            'type': 'value',
            'scale': True
        }
        
        chart_data['yAxis'] = {
            'name': self.y_label or self.y_column,
            'min': self.y_min,
            'max': self.y_max,
            'type': 'value',
            'scale': True
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
        tooltip = {
            'trigger': 'item',
            'formatter': '{a}<br>{b}: ({c})'
        }
        
        # Customize tooltip based on columns
        if self.color_column and self.size_column:
            tooltip['formatter'] = (
                f'{{a}}<br>'
                f'{self.x_column}: {{c[0]}}<br>'
                f'{self.y_column}: {{c[1]}}<br>'
                f'{self.color_column}: {{c[2]}}<br>'
                f'{self.size_column}: {{c[3]}}'
            )
        elif self.color_column:
            tooltip['formatter'] = (
                f'{{a}}<br>'
                f'{self.x_column}: {{c[0]}}<br>'
                f'{self.y_column}: {{c[1]}}<br>'
                f'{self.color_column}: {{c[2]}}'
            )
        elif self.size_column:
            tooltip['formatter'] = (
                f'{{a}}<br>'
                f'{self.x_column}: {{c[0]}}<br>'
                f'{self.y_column}: {{c[1]}}<br>'
                f'{self.size_column}: {{c[2]}}'
            )
        else:
            tooltip['formatter'] = (
                f'{{a}}<br>'
                f'{self.x_column}: {{c[0]}}<br>'
                f'{self.y_column}: {{c[1]}}'
            )
        
        chart_data['tooltip'] = tooltip
        
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
            'type': 'scatter_plot',
            'x_column': self.x_column,
            'y_column': self.y_column,
            'color_column': self.color_column,
            'size_column': self.size_column,
            'data_points': len(data)
        }
        
        return {
            'type': 'echarts',
            'data': chart_data,
            'metadata': self.get_metadata()
        }
    
    def _calculate_trend_line(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate trend line for the scatter plot.
        
        Parameters
        ----------
        data : pd.DataFrame
            The data to visualize
            
        Returns
        -------
        Dict[str, Any]
            Trend line series
        """
        try:
            # Get x and y values
            x = data[self.x_column].values
            y = data[self.y_column].values
            
            # Create x values for the trend line
            x_trend = np.linspace(x.min(), x.max(), 100)
            
            # Calculate trend line based on type
            if self.trend_line_type == 'linear':
                # Linear regression
                coeffs = np.polyfit(x, y, 1)
                y_trend = np.polyval(coeffs, x_trend)
                
                equation = f"y = {coeffs[0]:.4f}x + {coeffs[1]:.4f}"
                
            elif self.trend_line_type == 'polynomial':
                # Polynomial regression
                coeffs = np.polyfit(x, y, self.trend_line_degree)
                y_trend = np.polyval(coeffs, x_trend)
                
                # Create equation string
                equation = "y = "
                for i, coeff in enumerate(coeffs):
                    power = len(coeffs) - i - 1
                    if power > 1:
                        equation += f"{coeff:.4f}x^{power} + "
                    elif power == 1:
                        equation += f"{coeff:.4f}x + "
                    else:
                        equation += f"{coeff:.4f}"
                
            elif self.trend_line_type == 'exponential':
                # Exponential regression (y = a * e^(bx))
                # Take log of y values
                log_y = np.log(y)
                # Linear fit to log(y) = log(a) + bx
                coeffs = np.polyfit(x, log_y, 1)
                # Convert back to original form
                a = np.exp(coeffs[1])
                b = coeffs[0]
                y_trend = a * np.exp(b * x_trend)
                
                equation = f"y = {a:.4f} * e^({b:.4f}x)"
                
            else:
                raise ValueError(f"Unknown trend line type: {self.trend_line_type}")
            
            # Create trend line series
            trend_line = {
                'name': f"Trend Line ({self.trend_line_type})",
                'type': 'line',
                'data': [[x_val, y_val] for x_val, y_val in zip(x_trend, y_trend)],
                'smooth': True,
                'lineStyle': {
                    'width': 2,
                    'type': 'dashed'
                },
                'itemStyle': {
                    'color': 'rgba(255, 0, 0, 0.8)'
                },
                'tooltip': {
                    'formatter': f'{equation}'
                }
            }
            
            return trend_line
            
        except Exception as e:
            # If there's an error, return None
            return None
    
    def _get_color_map(self, color_map: str) -> List[str]:
        """
        Get colors for the specified color map.
        
        Parameters
        ----------
        color_map : str
            Name of the color map
            
        Returns
        -------
        List[str]
            List of colors
        """
        # Define some common color maps
        color_maps = {
            'viridis': ['#440154', '#414487', '#2a788e', '#22a884', '#7ad151', '#fde725'],
            'plasma': ['#0d0887', '#5302a3', '#8b0aa5', '#b83289', '#db5c68', '#f48849', '#febc2a'],
            'inferno': ['#000004', '#320a5a', '#781c6d', '#bb3754', '#ec6824', '#fbb41a'],
            'magma': ['#000004', '#2c115f', '#721f81', '#b73779', '#f0605d', '#febc2a'],
            'blues': ['#f7fbff', '#d0d1e6', '#a6bddb', '#74a9cf', '#3690c0', '#0570b0', '#034e7b'],
            'reds': ['#fff5f0', '#fee0d2', '#fcbba1', '#fc9272', '#fb6a4a', '#ef3b2c', '#cb181d', '#99000d'],
            'greens': ['#f7fcf5', '#e5f5e0', '#c7e9c0', '#a1d99b', '#74c476', '#41ab5d', '#238b45', '#005a32'],
            'spectral': ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fee08b', '#ffffbf', '#e6f598', '#abdda4', '#66c2a5', '#3288bd', '#5e4fa2']
        }
        
        # Return the specified color map or default to viridis
        return color_maps.get(color_map, color_maps['viridis'])
    
    def get_type(self) -> str:
        """
        Get the type of visualization.
        
        Returns
        -------
        str
            Type of visualization
        """
        return 'scatter_plot'
