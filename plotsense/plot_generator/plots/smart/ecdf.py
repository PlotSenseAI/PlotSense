import matplotlib.pyplot as plt
import numpy as np
from typing import List
import pandas as pd
from matplotlib.figure import Figure

from plotsense.plot_generator.helpers import set_labels

def create_ecdf_plot(df: pd.DataFrame, variables: List[str], **kwargs) -> Figure:
    """
    Enhanced ECDF plot that handles univariate and grouped data with NaN handling.
    """
    if len(variables) == 0:
        raise ValueError("ECDF plot requires at least 1 variable")
    
    var = variables[0]
    fig, ax = plt.subplots(figsize=(8, 5))

    if len(variables) == 1:
        data = df[var].dropna()
        if data.empty:
            raise ValueError(f"No valid data for {var}")
        sorted_data = np.sort(data)
        n = len(sorted_data)
        y = np.arange(1, n + 1) / n
        ax.plot(sorted_data, y, marker='.', linestyle='none', **kwargs)
    else:
        # Grouped ECDF
        group_var = variables[1]
        clean_data = df[[var, group_var]].dropna()
        if clean_data.empty:
            raise ValueError(f"No valid data after cleaning {var} and {group_var}")
        for cat, group in clean_data.groupby(group_var):
            sorted_data = np.sort(group[var])
            n = len(sorted_data)
            y = np.arange(1, n + 1) / n
            ax.plot(sorted_data, y, marker='.', linestyle='none', label=str(cat), **kwargs)
        ax.legend(title=group_var)

    ax.set_title(f"ECDF of {var}")
    set_labels(ax, variables[:2])
    ax.set_ylabel("Cumulative Probability")
    return fig
