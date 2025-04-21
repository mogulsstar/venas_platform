"""
Box plot visualization.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Tuple

from .base import Visualization


class BoxPlot(Visualization):
    """
    Box plot visualization.
    
    This visualization displays the distribution of data based on a five-number summary.
    It is useful for showing the spread and skewness of data.
    """
    
    def __init__(self, title: str = "", description: str = "", **kwargs):
        """
        Initialize the box plot.
        
        Parameters
        ----------
        title : str, optional
            Title of the visualization
        description : str, optional
            Description of the visualization
        **kwargs : dict
            Additional visualization-specific parameters:
            - columns: list, columns to visualize
            - group_column: str, column to group by
            - orientation: str, orientation of the box plot ('vertical' or 'horizontal')
            - show_outliers: bool, whether to show outliers
            - show_mean: bool, whether to show mean
            - colors: list, colors for each box
            - x_label: str, label for x-axis
            - y_label: str, label for y-axis
            - show_legend: bool, whether to show legend
            - grid: bool, whether to show grid
            - annotations: list, annotations to add to the chart
        """
        super().__init__(title, description, **kwargs)
        self.columns = kwargs.get('columns', [])
        self.group_column = kwargs.get('group_column')
        self.orientation = kwargs.get('orientation', 'vertical')
        self.show_outliers = kwargs.get('show_outliers', True)
        self.show_mean = kwargs.get('show_mean', True)
        self.colors = kwargs.get('colors', [])
        self.x_label = kwargs.get('x_label', '')
        self.y_label = kwargs.get('y_label', '')
        self.show_legend = kwargs.get('show_legend', True)
        self.grid = kwargs.get('grid', True)
        self.annotations = kwargs.get('annotations', [])
    
    def generate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate the box plot.
        
        Parameters
        ----------
        data : pd.DataFrame
            The data to visualize
            
        Returns
        -------
        Dict[str, Any]
            Box plot data in a format suitable for frontend rendering
            
        Raises
        ------
        ValueError
            If required parameters are missing or invalid
        """
        # Validate parameters
        if not self.columns and not self.group_column:
            raise ValueError("Either columns or group_column is required")
        
        if self.columns:
            missing_columns = [col for col in self.columns if col not in data.columns]
            if missing_columns:
                raise ValueError(f"Columns {missing_columns} not found in data")
        
        if self.group_column and self.group_column not in data.columns:
            raise ValueError(f"Group column '{self.group_column}' not found in data")
        
        # Prepare data
        chart_data = {
            'series': []
        }
        
        # Process data based on grouping
        if self.group_column:
            # Group by the specified column
            groups = data.groupby(self.group_column)
            
            # If columns are not specified, use all numeric columns
            if not self.columns:
                self.columns = data.select_dtypes(include=np.number).columns.tolist()
                # Remove group column if it's numeric
                if self.group_column in self.columns:
                    self.columns.remove(self.group_column)
            
            # Create box plot data for each column
            for col in self.columns:
                box_data = []
                for group_name, group_data in groups:
                    # Calculate box plot statistics
                    col_data = group_data[col].dropna()
                    if len(col_data) > 0:
                        q1 = col_data.quantile(0.25)
                        median = col_data.median()
                        q3 = col_data.quantile(0.75)
                        iqr = q3 - q1
                        lower_fence = q1 - 1.5 * iqr
                        upper_fence = q3 + 1.5 * iqr
                        
                        # Find outliers
                        outliers = col_data[(col_data < lower_fence) | (col_data > upper_fence)]
                        
                        # Find min and max (excluding outliers)
                        non_outliers = col_data[(col_data >= lower_fence) & (col_data <= upper_fence)]
                        min_val = non_outliers.min() if len(non_outliers) > 0 else q1
                        max_val = non_outliers.max() if len(non_outliers) > 0 else q3
                        
                        # Calculate mean
                        mean = col_data.mean()
                        
                        # Add box plot data
                        box_data.append([min_val, q1, median, q3, max_val, mean, outliers.tolist()])
                
                # Create box plot series
                box_series = {
                    'name': col,
                    'type': 'boxplot',
                    'data': [[d[0], d[1], d[2], d[3], d[4]] for d in box_data],  # [min, q1, median, q3, max]
                    'itemStyle': {
                        'borderWidth': 2
                    },
                    'tooltip': {
                        'formatter': (
                            f'{{a}}<br>'
                            f'Min: {{c[0]}}<br>'
                            f'Q1: {{c[1]}}<br>'
                            f'Median: {{c[2]}}<br>'
                            f'Q3: {{c[3]}}<br>'
                            f'Max: {{c[4]}}'
                        )
                    }
                }
                
                # Add color if specified
                if self.colors and len(self.colors) > 0:
                    box_series['itemStyle']['color'] = self.colors[0]
                
                chart_data['series'].append(box_series)
                
                # Add mean if requested
                if self.show_mean:
                    mean_series = {
                        'name': f"{col} Mean",
                        'type': 'scatter',
                        'data': [[i, d[5]] for i, d in enumerate(box_data)],
                        'itemStyle': {
                            'color': 'red'
                        },
                        'tooltip': {
                            'formatter': f'{{a}}<br>Mean: {{c[1]}}'
                        }
                    }
                    
                    chart_data['series'].append(mean_series)
                
                # Add outliers if requested
                if self.show_outliers:
                    for i, d in enumerate(box_data):
                        if d[6]:  # If there are outliers
                            outlier_series = {
                                'name': f"{col} Outliers",
                                'type': 'scatter',
                                'data': [[i, o] for o in d[6]],
                                'itemStyle': {
                                    'color': 'red',
                                    'opacity': 0.5
                                },
                                'tooltip': {
                                    'formatter': f'{{a}}<br>Outlier: {{c[1]}}'
                                }
                            }
                            
                            chart_data['series'].append(outlier_series)
            
            # Set category data
            categories = list(groups.groups.keys())
            
        else:
            # Use specified columns
            box_data = []
            for col in self.columns:
                # Calculate box plot statistics
                col_data = data[col].dropna()
                if len(col_data) > 0:
                    q1 = col_data.quantile(0.25)
                    median = col_data.median()
                    q3 = col_data.quantile(0.75)
                    iqr = q3 - q1
                    lower_fence = q1 - 1.5 * iqr
                    upper_fence = q3 + 1.5 * iqr
                    
                    # Find outliers
                    outliers = col_data[(col_data < lower_fence) | (col_data > upper_fence)]
                    
                    # Find min and max (excluding outliers)
                    non_outliers = col_data[(col_data >= lower_fence) & (col_data <= upper_fence)]
                    min_val = non_outliers.min() if len(non_outliers) > 0 else q1
                    max_val = non_outliers.max() if len(non_outliers) > 0 else q3
                    
                    # Calculate mean
                    mean = col_data.mean()
                    
                    # Add box plot data
                    box_data.append([min_val, q1, median, q3, max_val, mean, outliers.tolist()])
            
            # Create box plot series
            box_series = {
                'name': 'Box Plot',
                'type': 'boxplot',
                'data': [[d[0], d[1], d[2], d[3], d[4]] for d in box_data],  # [min, q1, median, q3, max]
                'itemStyle': {
                    'borderWidth': 2
                },
                'tooltip': {
                    'formatter': (
                        f'{{a}}<br>'
                        f'Min: {{c[0]}}<br>'
                        f'Q1: {{c[1]}}<br>'
                        f'Median: {{c[2]}}<br>'
                        f'Q3: {{c[3]}}<br>'
                        f'Max: {{c[4]}}'
                    )
                }
            }
            
            # Add colors if specified
            if self.colors:
                box_series['itemStyle']['color'] = self.colors[0] if len(self.colors) > 0 else None
            
            chart_data['series'].append(box_series)
            
            # Add mean if requested
            if self.show_mean:
                mean_series = {
                    'name': 'Mean',
                    'type': 'scatter',
                    'data': [[i, d[5]] for i, d in enumerate(box_data)],
                    'itemStyle': {
                        'color': 'red'
                    },
                    'tooltip': {
                        'formatter': f'{{a}}<br>Mean: {{c[1]}}'
                    }
                }
                
                chart_data['series'].append(mean_series)
            
            # Add outliers if requested
            if self.show_outliers:
                for i, d in enumerate(box_data):
                    if d[6]:  # If there are outliers
                        outlier_series = {
                            'name': f"{self.columns[i]} Outliers",
                            'type': 'scatter',
                            'data': [[i, o] for o in d[6]],
                            'itemStyle': {
                                'color': 'red',
                                'opacity': 0.5
                            },
                            'tooltip': {
                                'formatter': f'{{a}}<br>Outlier: {{c[1]}}'
                            }
                        }
                        
                        chart_data['series'].append(outlier_series)
            
            # Set category data
            categories = self.columns
        
        # Add annotations
        if self.annotations:
            chart_data['annotations'] = self.annotations
        
        # Set axis configuration based on orientation
        if self.orientation == 'vertical':
            chart_data['xAxis'] = {
                'type': 'category',
                'data': categories,
                'name': self.x_label or (self.group_column if self.group_column else 'Columns'),
                'boundaryGap': True,
                'splitArea': {
                    'show': False
                },
                'axisLabel': {
                    'rotate': 45 if len(categories) > 5 else 0
                }
            }
            
            chart_data['yAxis'] = {
                'type': 'value',
                'name': self.y_label or 'Value',
                'splitArea': {
                    'show': True
                }
            }
        else:  # horizontal
            chart_data['yAxis'] = {
                'type': 'category',
                'data': categories,
                'name': self.y_label or (self.group_column if self.group_column else 'Columns'),
                'boundaryGap': True,
                'splitArea': {
                    'show': False
                }
            }
            
            chart_data['xAxis'] = {
                'type': 'value',
                'name': self.x_label or 'Value',
                'splitArea': {
                    'show': True
                }
            }
        
        # Add grid configuration
        chart_data['grid'] = {
            'show': self.grid,
            'left': '10%',
            'right': '10%',
            'bottom': '15%'
        }
        
        # Add legend configuration
        chart_data['legend'] = {
            'show': self.show_legend
        }
        
        # Add title and description
        chart_data['title'] = {
            'text': self.title or 'Box Plot',
            'subtext': self.description
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
            'type': 'box_plot',
            'columns': self.columns,
            'group_column': self.group_column,
            'orientation': self.orientation,
            'show_outliers': self.show_outliers,
            'show_mean': self.show_mean
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
        return 'box_plot'
