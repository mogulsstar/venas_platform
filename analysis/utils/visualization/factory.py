"""
Factory for creating visualizations.
"""

from typing import Dict, Any, Optional, List, Union, Type

from .base import Visualization
from .line_chart import LineChart
from .bar_chart import BarChart
from .scatter_plot import ScatterPlot
from .histogram import Histogram
from .box_plot import BoxPlot
from .heatmap import Heatmap
from .pie_chart import PieChart


class VisualizationFactory:
    """
    Factory class for creating visualizations.
    """
    
    # Registry of visualization types
    _visualizations = {
        'line_chart': LineChart,
        'bar_chart': BarChart,
        'scatter_plot': ScatterPlot,
        'histogram': Histogram,
        'box_plot': BoxPlot,
        'heatmap': Heatmap,
        'pie_chart': PieChart
    }
    
    @classmethod
    def create(cls, viz_type: str, **kwargs) -> Visualization:
        """
        Create a visualization of the specified type.
        
        Parameters
        ----------
        viz_type : str
            Type of visualization to create
        **kwargs : dict
            Additional parameters for the visualization
            
        Returns
        -------
        Visualization
            The created visualization
            
        Raises
        ------
        ValueError
            If the visualization type is not supported
        """
        if viz_type not in cls._visualizations:
            raise ValueError(f"Unsupported visualization type: {viz_type}")
        
        return cls._visualizations[viz_type](**kwargs)
    
    @classmethod
    def register(cls, viz_type: str, viz_class: Type[Visualization]) -> None:
        """
        Register a new visualization type.
        
        Parameters
        ----------
        viz_type : str
            Type of visualization
        viz_class : Type[Visualization]
            Visualization class
        """
        cls._visualizations[viz_type] = viz_class
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """
        Get a list of supported visualization types.
        
        Returns
        -------
        List[str]
            List of supported visualization types
        """
        return list(cls._visualizations.keys())
