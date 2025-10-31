from typing import List
import matplotlib.pyplot as plt

def create_scatter_plot(df, variables: List[str], **kwargs):
    """Scatter plot: requires at least 2 variables (x, y)."""
    if len(variables) < 2:
        raise ValueError("scatter requires at least 2 variables (x, y)")
    fig, ax = plt.subplots()
    ax.scatter(df[variables[0]], df[variables[1]], **kwargs)
    ax.set_xlabel(variables[0])
    ax.set_ylabel(variables[1])
    ax.set_title(f"Scatter: {variables[0]} vs {variables[1]}")
    return fig

