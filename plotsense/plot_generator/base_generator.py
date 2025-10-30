import pandas as pd
from matplotlib.figure import Figure
from typing import Callable, Dict, Optional

from plotsense.plot_generator.registry import PlotRequirements, PlotTypeRegistry


class PlotGenerator:
    """
    A class to generate various types of plots based on suggestions. 
    It uses matplotlib for plotting and can handle both univariate and bivariate cases.
    """
    def __init__(self, data, suggestions: Optional[pd.DataFrame] = None):
        """
        Initialize with data and plot suggestions.
        
        Args:
            data: DataFrame containing the actual data
            suggestions: DataFrame with plot suggestions
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame")
        if data.empty:
            raise ValueError("DataFrame is empty")
        if not isinstance(suggestions, pd.DataFrame):
            raise TypeError("Suggestions must be a pandas DataFrame")
        if suggestions.empty:
            raise ValueError("Suggestions DataFrame is empty")
        if 'plot_type' not in suggestions.columns or 'variables' not in suggestions.columns:
            raise ValueError("Suggestions DataFrame must contain 'plot_type' and 'variables' columns")
        
        self.data = data.copy()
        self.suggestions = suggestions
        self.registry = PlotTypeRegistry()
        self._register_default_plots(self._default_plots)

    @property
    def _default_plots(self) -> Dict[str, Callable[..., Figure]]:
        """Subclasses override this to define plot type → function mapping."""
        return {}

    def _register_default_plots(
        self, plots_to_register: Dict[str, Callable[..., Figure]]
    ):
        for name, func in plots_to_register.items():
            self.registry.register(
                name,
                PlotRequirements(
                    min_variables=1, max_variables=2, numeric_only=True
                ),
                lambda variables, f=func: f(self.data, variables)
            )

    def generate_plot(self, suggestion_index: int, **kwargs) -> Figure:
        """
        Generate a plot based on the suggestion at given index.
        
        Args:
            suggestion_index: Index of the suggestion in dataframe
            **kwargs: Additional arguments for the plot
            
        Returns:
            matplotlib Figure object
        """
        suggestion = self.suggestions.iloc[suggestion_index]
        plot_type = suggestion['plot_type'].lower()
        variables = [v.strip() for v in suggestion['variables'].split(',')]

        plot_func = self.registry.get_generator(plot_type)
        if not plot_func:
            raise ValueError(f"Plot type '{plot_type}' not supported")

        if not self.registry.validate(plot_type, variables, self.data):
            raise ValueError(f"Invalid variables for plot '{plot_type}'")

        return plot_func(variables, **kwargs)
