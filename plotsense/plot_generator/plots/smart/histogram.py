from typing import List
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def create_histogram_plot(df: pd.DataFrame, variables: List[str], **kwargs) -> plt.Figure:
    """Enhanced histogram that can handle grouping by a second variable."""
    fig, ax = plt.subplots(figsize=(12, 8))

    if len(variables) == 1:
        # Simple histogram
        data = df[variables[0]].dropna()
        if data.empty:
            raise ValueError(f"No valid data remaining for {variables[0]}")
        ax.hist(data, **kwargs)
        ax.set_xlabel(variables[0])
        ax.set_ylabel("Frequency")
        ax.set_title(f"Histogram of {variables[0]}")
    elif len(variables) >= 2:
        # Grouped histogram
        num, cat = variables[0], variables[1]

        # Clean data - remove rows where either variable is NaN
        clean_data = df[[num, cat]].dropna()
        if clean_data.empty:
            raise ValueError(f"No valid data remaining after cleaning {num} and {cat}")

        # Get unique categories
        categories = clean_data[cat].unique()

        # Set default colors if not provided
        if 'color' in kwargs:
            colors = [kwargs['color']] * len(categories)
        elif 'colors' in kwargs:
            colors = kwargs['colors']
        else:
            colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

        # Plot each group
        for i, c in enumerate(categories):
            ax.hist(
                clean_data[clean_data[cat] == c][num],
                alpha=0.5,
                label=str(c),
                color=colors[i % len(colors)],
                **kwargs
            )
        ax.set_xlabel(num)
        ax.set_ylabel("Frequency")
        ax.set_title(f"Histogram of {num} by {cat}")
        ax.legend()
    else:
        raise ValueError("Histogram requires at least one variable")

    return fig

