from typing import List
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

def create_scatter_plot(
    df, variables: List[str],
    size_scale: float = 100.0, **kwargs
) -> Figure:
    """
    Create a scatter plot with optional color and size dimensions.
    
    Parameters:
    -----------
    variables : List[str]
        - 2 variables: x, y
        - 3 variables: x, y, color
        - 4 variables: x, y, color, size
    size_scale : float
        Scaling factor for bubble sizes (default: 100)
    
    Returns:
    --------
    matplotlib.figure.Figure
    """
    if len(variables) < 2:
        raise ValueError("Scatter requires at least 2 variables (x, y)")
    if len(variables) > 4:
        raise ValueError("Scatter supports up to 4 variables (x, y, color, size)")

    # Check data types
    for var in variables[:2]:
        if not np.issubdtype(df[var].dtype, np.number):
            raise ValueError(f"Variable '{var}' must be numeric")

    fig, ax = plt.subplots()
    scatter_params = {"x": df[variables[0]], "y": df[variables[1]]}

    # Handle color (3rd variable)
    if len(variables) >= 3:
        color_data = df[variables[2]]
        if pd.api.types.is_numeric_dtype(color_data):
            # For numeric color data, use continuous colormap
            scatter_params["c"] = color_data
            kwargs.setdefault("cmap", "viridis")
        else:
            # For categorical data, convert to numeric codes
            scatter_params["c"] = pd.factorize(color_data)[0]
            kwargs.setdefault("cmap", "tab10")

    # Handle size (4th variable)
    if len(variables) == 4:
        size_data = df[variables[3]]
        if not pd.api.types.is_numeric_dtype(size_data):
            raise ValueError(f"Size variable '{variables[3]}' must be numeric")

        # Normalize and scale sizes
        sizes = np.abs(size_data)
        sizes = (sizes - sizes.min()) / (sizes.max() - sizes.min() + 1e-8) * size_scale
        scatter_params["s"] = sizes

    # Apply any additional kwargs
    scatter_params.update(kwargs)
    scatter = ax.scatter(**scatter_params)

    # Set labels and title
    ax.set_xlabel(variables[0])
    ax.set_ylabel(variables[1])
    title = f"Scatter: {variables[0]} vs {variables[1]}"
    if len(variables) >= 3:
        title += f" (colored by {variables[2]})"
        if pd.api.types.is_numeric_dtype(df[variables[2]]):
            fig.colorbar(scatter, ax=ax, label=variables[2])
    if len(variables) == 4:
        title += f" (sized by {variables[3]})"
    ax.set_title(title)
    return fig

