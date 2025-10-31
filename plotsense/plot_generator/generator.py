import pandas as pd
from matplotlib.figure import Figure
from typing import Optional, Union, Callable

from plotsense.plot_generator.basic_generator import BasicPlotGenerator
from plotsense.plot_generator.smart_generator import SmartPlotGenerator
from plotsense.plot_generator.registry import PlotRequirements

# Global instance of the plot generator
_plot_generator_instance = None

_GENERATOR_MAP = {
    "basic": BasicPlotGenerator,
    "smart": SmartPlotGenerator
}

def plotgen(
    df: pd.DataFrame,
    suggestion: Union[int, pd.Series],
    suggestions_df: Optional[pd.DataFrame] = None,
    generator: str = "basic",
    plot_function: Optional[Callable] = None,
    plot_type: Optional[str] = None,
    plot_requirements: Optional[PlotRequirements] = None,
    **plot_kwargs
) -> Figure:
    """
    Generate a plot based on visualization suggestions.

    Users can also register a custom plot function temporarily by providing:
        plot_function: callable(df, variables, **kwargs) -> Figure
        plot_type: string name for the custom plot
        plot_requirements: optional PlotRequirements object

    Args:
        df: Input DataFrame containing the data to plot
        suggestion: Either an integer index or a pandas Series containing the suggestion row
        suggestions_df: DataFrame containing visualization suggestions (required if suggestion is an index)
        generator: String identifier for generator to use ("basic" or "smart")
        plot_function: Optional custom plot function
        plot_type: Name of the custom plot
        plot_requirements: Optional PlotRequirements for the custom plot
        **plot_kwargs: Additional arguments to pass to the plot function

    Returns:
        matplotlib.Figure: The generated figure
    """
    global _plot_generator_instance

    # Determine generator class from string
    generator_class = _GENERATOR_MAP.get(generator.lower(), BasicPlotGenerator)

    # Initialize generator instance if needed
    if _plot_generator_instance is None or not isinstance(
        _plot_generator_instance, generator_class
    ):
        # Handle case where suggestion is a row from recommendations
        if isinstance(suggestion, pd.Series):
            temp_df = pd.DataFrame([suggestion])
            _plot_generator_instance = generator_class(df, temp_df)
        # Handle case where suggestion is an index
        elif isinstance(suggestion, int):
            if suggestions_df is None:
                raise ValueError("suggestions_df must be provided when using an index")
            _plot_generator_instance = generator_class(df, suggestions_df)
    else:
        # Update data if it changed
        if not _plot_generator_instance.data.equals(df):
            _plot_generator_instance.data = df

    # If user provides a custom plot function, register it temporarily
    if plot_function is not None:
        if not plot_type:
            raise ValueError("plot_type name must be provided when registering a custom plot")
        if plot_requirements is None:
            plot_requirements = PlotRequirements(min_variables=1, max_variables=2, numeric_only=True)

        pg = _plot_generator_instance
        if pg is None:
            raise RuntimeError("Plot generator instance is not initialized")

        pg.registry.register(
            plot_type,
            plot_requirements,
            lambda variables,
                f=plot_function: f(pg.data, variables, **plot_kwargs)
        )

    # Extract suggestion row
    if isinstance(suggestion, pd.Series):
        suggestion_row = suggestion.copy()
    else:
        s_df = suggestions_df
        if s_df is None:
            raise ValueError("suggestions_df must be provided when using an index")
        suggestion_row = s_df.iloc[suggestion].copy()

    # Override variables if x/y/z provided
    variables = [v.strip() for v in str(suggestion_row['variables']).split(',')]
    if 'x' in plot_kwargs:
        variables[0] = plot_kwargs.pop('x')
    if 'y' in plot_kwargs and len(variables) > 1:
        variables[1] = plot_kwargs.pop('y')
    if 'z' in plot_kwargs and len(variables) > 2:
        variables[2] = plot_kwargs.pop('z')

    suggestion_row['variables'] = ','.join(variables)

    # Update the generator's suggestion DataFrame if using index
    if isinstance(suggestion, int):
        s_df = suggestions_df
        if s_df is None:
            raise ValueError("suggestions_df must be provided when using an index")
        s_df.iloc[suggestion] = suggestion_row
        _plot_generator_instance.suggestions = suggestions_df
    else:
        _plot_generator_instance.suggestions = pd.DataFrame([suggestion_row])

    # Determine plot_type to use
    active_plot_type = plot_type or str(suggestion_row['plot_type']).lower()

    # Generate the plot
    plot_func = _plot_generator_instance.registry.get_generator(active_plot_type)
    if not plot_func:
        raise ValueError(f"Plot type '{active_plot_type}' not supported")

    if not _plot_generator_instance.registry.validate(active_plot_type, variables, _plot_generator_instance.data):
        raise ValueError(f"Invalid variables for plot '{active_plot_type}'")

    return plot_func(variables, **plot_kwargs)

# fig = plotgen(df, 0, suggestions_df, generator="smart")
