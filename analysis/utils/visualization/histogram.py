"""
Histogram visualization.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Tuple

from .base import Visualization


class Histogram(Visualization):
    """
    Histogram visualization.
    
    This visualization displays the distribution of a dataset.
    It is useful for showing the shape and spread of continuous data.
    """
    
    def __init__(self, title: str = "", description: str = "", **kwargs):
        """
        Initialize the histogram.
        
        Parameters
        ----------
        title : str, optional
            Title of the visualization
        description : str, optional
            Description of the visualization
        **kwargs : dict
            Additional visualization-specific parameters:
            - column: str, column to visualize
            - bins: int, number of bins
            - bin_range: list, range of bins [min, max]
            - normalize: bool, whether to normalize the histogram
            - cumulative: bool, whether to show cumulative histogram
            - kde: bool, whether to show kernel density estimate
            - color: str, color of the histogram
            - x_label: str, label for x-axis
            - y_label: str, label for y-axis
            - show_statistics: bool, whether to show statistics
            - grid: bool, whether to show grid
            - annotations: list, annotations to add to the chart
        """
        super().__init__(title, description, **kwargs)
        self.column = kwargs.get('column')
        self.bins = kwargs.get('bins', 10)
        self.bin_range = kwargs.get('bin_range')
        self.normalize = kwargs.get('normalize', False)
        self.cumulative = kwargs.get('cumulative', False)
        self.kde = kwargs.get('kde', False)
        self.color = kwargs.get('color', '#5470c6')
        self.x_label = kwargs.get('x_label', '')
        self.y_label = kwargs.get('y_label', '')
        self.show_statistics = kwargs.get('show_statistics', True)
        self.grid = kwargs.get('grid', True)
        self.annotations = kwargs.get('annotations', [])
    
    def generate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate the histogram.
        
        Parameters
        ----------
        data : pd.DataFrame
            The data to visualize
            
        Returns
        -------
        Dict[str, Any]
            Histogram data in a format suitable for frontend rendering
            
        Raises
        ------
        ValueError
            If required parameters are missing or invalid
        """
        # Validate parameters
        if not self.column:
            raise ValueError("column is required")
        
        if self.column not in data.columns:
            raise ValueError(f"column '{self.column}' not found in data")
        
        # Get column data
        column_data = data[self.column].dropna()
        
        # Calculate histogram
        if self.bin_range:
            hist, bin_edges = np.histogram(column_data, bins=self.bins, range=self.bin_range)
        else:
            hist, bin_edges = np.histogram(column_data, bins=self.bins)
        
        # Normalize if requested
        if self.normalize:
            hist = hist / hist.sum()
        
        # Calculate cumulative if requested
        if self.cumulative:
            hist = np.cumsum(hist)
            if self.normalize:
                hist = hist / hist[-1]
        
        # Calculate bin centers
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # Prepare data
        chart_data = {
            'series': []
        }
        
        # Create histogram series
        histogram_series = {
            'name': self.column,
            'type': 'bar',
            'data': hist.tolist(),
            'itemStyle': {
                'color': self.color
            },
            'barWidth': '99%'  # Make bars touch each other
        }
        
        chart_data['series'].append(histogram_series)
        
        # Add KDE if requested
        if self.kde:
            # Calculate KDE
            from scipy.stats import gaussian_kde
            kde = gaussian_kde(column_data)
            
            # Create x values for KDE
            x_kde = np.linspace(bin_edges[0], bin_edges[-1], 100)
            
            # Calculate KDE values
            y_kde = kde(x_kde)
            
            # Scale KDE to match histogram
            if self.normalize:
                # KDE is already normalized
                pass
            else:
                # Scale KDE to match histogram area
                hist_area = np.sum(hist) * (bin_edges[1] - bin_edges[0])
                kde_area = np.trapz(y_kde, x_kde)
                y_kde = y_kde * (hist_area / kde_area)
            
            # Create KDE series
            kde_series = {
                'name': f"{self.column} KDE",
                'type': 'line',
                'data': [[x, y] for x, y in zip(x_kde, y_kde)],
                'smooth': True,
                'lineStyle': {
                    'width': 2
                },
                'itemStyle': {
                    'color': 'rgba(255, 0, 0, 0.8)'
                }
            }
            
            chart_data['series'].append(kde_series)
        
        # Add statistics if requested
        if self.show_statistics:
            # Calculate statistics
            mean = column_data.mean()
            median = column_data.median()
            std = column_data.std()
            min_val = column_data.min()
            max_val = column_data.max()
            
            # Add statistics as markLines
            markLines = {
                'data': [
                    {'name': 'Mean', 'xAxis': mean, 'lineStyle': {'color': 'green'}},
                    {'name': 'Median', 'xAxis': median, 'lineStyle': {'color': 'blue'}}
                ]
            }
            
            histogram_series['markLine'] = markLines
            
            # Add statistics to tooltip
            chart_data['tooltip'] = {
                'formatter': (
                    f'{{a}}<br>'
                    f'Bin: {{c}}<br>'
                    f'Mean: {mean:.4f}<br>'
                    f'Median: {median:.4f}<br>'
                    f'Std Dev: {std:.4f}<br>'
                    f'Min: {min_val:.4f}<br>'
                    f'Max: {max_val:.4f}'
                )
            }
        
        # Add annotations
        if self.annotations:
            chart_data['annotations'] = self.annotations
        
        # Add axis configuration
        chart_data['xAxis'] = {
            'type': 'category',
            'data': [f"{edge:.2f}" for edge in bin_centers],
            'name': self.x_label or self.column,
            'boundaryGap': False
        }
        
        chart_data['yAxis'] = {
            'type': 'value',
            'name': self.y_label or ('Frequency' if not self.normalize else 'Density')
        }
        
        # Add grid configuration
        chart_data['grid'] = {
            'show': self.grid
        }
        
        # Add title and description
        chart_data['title'] = {
            'text': self.title or f"Histogram of {self.column}",
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
            'type': 'histogram',
            'column': self.column,
            'bins': self.bins,
            'normalize': self.normalize,
            'cumulative': self.cumulative,
            'kde': self.kde,
            'data_points': len(column_data),
            'statistics': {
                'mean': float(column_data.mean()),
                'median': float(column_data.median()),
                'std': float(column_data.std()),
                'min': float(column_data.min()),
                'max': float(column_data.max()),
                'q1': float(column_data.quantile(0.25)),
                'q3': float(column_data.quantile(0.75))
            }
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
        return 'histogram'
