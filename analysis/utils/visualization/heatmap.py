"""
Heatmap visualization.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Tuple

from .base import Visualization


class Heatmap(Visualization):
    """
    Heatmap visualization.
    
    This visualization displays data as a colored grid.
    It is useful for showing patterns and correlations in 2D data.
    """
    
    def __init__(self, title: str = "", description: str = "", **kwargs):
        """
        Initialize the heatmap.
        
        Parameters
        ----------
        title : str, optional
            Title of the visualization
        description : str, optional
            Description of the visualization
        **kwargs : dict
            Additional visualization-specific parameters:
            - data_type: str, type of data to visualize ('correlation', 'values', 'pivot')
            - x_column: str, column to use for x-axis (for pivot)
            - y_column: str, column to use for y-axis (for pivot)
            - value_column: str, column to use for values (for pivot)
            - columns: list, columns to include (for correlation)
            - color_map: str, color map to use
            - show_values: bool, whether to show values in cells
            - value_format: str, format for values
            - x_label: str, label for x-axis
            - y_label: str, label for y-axis
            - min_value: float, minimum value for color scale
            - max_value: float, maximum value for color scale
            - annotations: list, annotations to add to the chart
        """
        super().__init__(title, description, **kwargs)
        self.data_type = kwargs.get('data_type', 'correlation')
        self.x_column = kwargs.get('x_column')
        self.y_column = kwargs.get('y_column')
        self.value_column = kwargs.get('value_column')
        self.columns = kwargs.get('columns', [])
        self.color_map = kwargs.get('color_map', 'viridis')
        self.show_values = kwargs.get('show_values', True)
        self.value_format = kwargs.get('value_format', '.2f')
        self.x_label = kwargs.get('x_label', '')
        self.y_label = kwargs.get('y_label', '')
        self.min_value = kwargs.get('min_value')
        self.max_value = kwargs.get('max_value')
        self.annotations = kwargs.get('annotations', [])
    
    def generate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate the heatmap.
        
        Parameters
        ----------
        data : pd.DataFrame
            The data to visualize
            
        Returns
        -------
        Dict[str, Any]
            Heatmap data in a format suitable for frontend rendering
            
        Raises
        ------
        ValueError
            If required parameters are missing or invalid
        """
        # Prepare data based on data_type
        if self.data_type == 'correlation':
            # Calculate correlation matrix
            if self.columns:
                # Use specified columns
                missing_columns = [col for col in self.columns if col not in data.columns]
                if missing_columns:
                    raise ValueError(f"Columns {missing_columns} not found in data")
                
                # Select numeric columns
                numeric_columns = [col for col in self.columns if pd.api.types.is_numeric_dtype(data[col])]
                if not numeric_columns:
                    raise ValueError("No numeric columns found in the specified columns")
                
                # Calculate correlation matrix
                corr_matrix = data[numeric_columns].corr()
            else:
                # Use all numeric columns
                numeric_data = data.select_dtypes(include=np.number)
                if numeric_data.empty:
                    raise ValueError("No numeric columns found in the data")
                
                # Calculate correlation matrix
                corr_matrix = numeric_data.corr()
            
            # Set heatmap data
            heatmap_data = corr_matrix
            x_categories = heatmap_data.columns.tolist()
            y_categories = heatmap_data.index.tolist()
            
            # Set min and max values
            if self.min_value is None:
                self.min_value = -1
            if self.max_value is None:
                self.max_value = 1
            
            # Set title if not provided
            if not self.title:
                self.title = 'Correlation Matrix'
            
        elif self.data_type == 'values':
            # Use the data as is
            if self.columns:
                # Use specified columns
                missing_columns = [col for col in self.columns if col not in data.columns]
                if missing_columns:
                    raise ValueError(f"Columns {missing_columns} not found in data")
                
                # Select columns
                heatmap_data = data[self.columns]
            else:
                # Use all columns
                heatmap_data = data
            
            # Set categories
            x_categories = heatmap_data.columns.tolist()
            y_categories = heatmap_data.index.tolist()
            
            # Set min and max values if not provided
            if self.min_value is None:
                self.min_value = heatmap_data.min().min()
            if self.max_value is None:
                self.max_value = heatmap_data.max().max()
            
            # Set title if not provided
            if not self.title:
                self.title = 'Heatmap'
            
        elif self.data_type == 'pivot':
            # Create pivot table
            if not self.x_column or not self.y_column or not self.value_column:
                raise ValueError("x_column, y_column, and value_column are required for pivot heatmap")
            
            if self.x_column not in data.columns:
                raise ValueError(f"x_column '{self.x_column}' not found in data")
            
            if self.y_column not in data.columns:
                raise ValueError(f"y_column '{self.y_column}' not found in data")
            
            if self.value_column not in data.columns:
                raise ValueError(f"value_column '{self.value_column}' not found in data")
            
            # Create pivot table
            pivot_table = pd.pivot_table(
                data,
                values=self.value_column,
                index=self.y_column,
                columns=self.x_column,
                aggfunc='mean'
            )
            
            # Set heatmap data
            heatmap_data = pivot_table
            x_categories = heatmap_data.columns.tolist()
            y_categories = heatmap_data.index.tolist()
            
            # Set min and max values if not provided
            if self.min_value is None:
                self.min_value = heatmap_data.min().min()
            if self.max_value is None:
                self.max_value = heatmap_data.max().max()
            
            # Set title if not provided
            if not self.title:
                self.title = f'Heatmap of {self.value_column} by {self.x_column} and {self.y_column}'
            
        else:
            raise ValueError(f"Unknown data_type: {self.data_type}")
        
        # Convert heatmap data to list format for ECharts
        heatmap_values = []
        for i, row_idx in enumerate(heatmap_data.index):
            for j, col_idx in enumerate(heatmap_data.columns):
                value = heatmap_data.iloc[i, j]
                if not pd.isna(value):
                    heatmap_values.append([j, i, value])
        
        # Prepare chart data
        chart_data = {
            'series': [
                {
                    'name': 'Heatmap',
                    'type': 'heatmap',
                    'data': heatmap_values,
                    'label': {
                        'show': self.show_values,
                        'formatter': f'{{c:{self.value_format}}}'
                    },
                    'emphasis': {
                        'itemStyle': {
                            'shadowBlur': 10,
                            'shadowColor': 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }
            ]
        }
        
        # Add visual map for color scale
        chart_data['visualMap'] = {
            'min': self.min_value,
            'max': self.max_value,
            'calculable': True,
            'orient': 'horizontal',
            'left': 'center',
            'bottom': '5%',
            'inRange': {
                'color': self._get_color_map(self.color_map)
            }
        }
        
        # Add annotations
        if self.annotations:
            chart_data['annotations'] = self.annotations
        
        # Add axis configuration
        chart_data['xAxis'] = {
            'type': 'category',
            'data': x_categories,
            'name': self.x_label or (self.x_column if self.data_type == 'pivot' else ''),
            'splitArea': {
                'show': True
            },
            'axisLabel': {
                'rotate': 45 if len(x_categories) > 10 else 0
            }
        }
        
        chart_data['yAxis'] = {
            'type': 'category',
            'data': y_categories,
            'name': self.y_label or (self.y_column if self.data_type == 'pivot' else ''),
            'splitArea': {
                'show': True
            }
        }
        
        # Add grid configuration
        chart_data['grid'] = {
            'height': '60%',
            'top': '10%',
            'left': '10%',
            'right': '10%',
            'bottom': '20%'
        }
        
        # Add title and description
        chart_data['title'] = {
            'text': self.title,
            'subtext': self.description
        }
        
        # Add tooltip configuration
        chart_data['tooltip'] = {
            'position': 'top',
            'formatter': (
                f'{{a}}<br>'
                f'{{b0}}: {{b1}}<br>'
                f'{{c0}}: {{c1}}<br>'
                f'Value: {{c2:{self.value_format}}}'
            )
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
            'type': 'heatmap',
            'data_type': self.data_type,
            'x_column': self.x_column,
            'y_column': self.y_column,
            'value_column': self.value_column,
            'columns': self.columns,
            'min_value': self.min_value,
            'max_value': self.max_value
        }
        
        return {
            'type': 'echarts',
            'data': chart_data,
            'metadata': self.get_metadata()
        }
    
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
            'spectral': ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fee08b', '#ffffbf', '#e6f598', '#abdda4', '#66c2a5', '#3288bd', '#5e4fa2'],
            'coolwarm': ['#3b4cc0', '#6f91f2', '#a9c1f4', '#dddddd', '#f6b69b', '#e6745b', '#b40426'],
            'RdBu': ['#67001f', '#b2182b', '#d6604d', '#f4a582', '#fddbc7', '#f7f7f7', '#d1e5f0', '#92c5de', '#4393c3', '#2166ac', '#053061']
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
        return 'heatmap'
