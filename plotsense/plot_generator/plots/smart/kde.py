from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns  # optional, for nicer KDE plots
from typing import List
import pandas as pd

from plotsense.plot_generator.helpers import set_labels

def create_kde_plot(df: pd.DataFrame, variables: List[str], **kwargs) -> Figure:
    """
    Enhanced KDE plot that handles univariate and grouped data with NaN handling.
    """
    if len(variables) == 0:
        raise ValueError("KDE plot requires at least 1 variable")
    
    var = variables[0]
    data: pd.DataFrame = pd.DataFrame(df[[var]].dropna())
    if data.empty:
        raise ValueError(f"No valid data for {var}")

    fig, ax = plt.subplots(figsize=(8, 5))

    if len(variables) == 1:
        # Univariate
        sns.kdeplot(data=data, ax=ax, **kwargs)
    else:
        # Bivariate / group-by
        group_var = variables[1]
        clean_data: pd.DataFrame = pd.DataFrame(df[[var, group_var]].dropna())
        if clean_data.empty:
            raise ValueError(f"No valid data after cleaning {var} and {group_var}")
        sns.kdeplot(data=clean_data, x=var, hue=group_var, ax=ax, **kwargs)

    ax.set_title(f"KDE Plot of {var}")
    set_labels(ax, variables[:2])  # x + y labels
    return fig

