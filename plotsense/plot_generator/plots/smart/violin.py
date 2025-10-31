import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def create_violin_plot(df: pd.DataFrame, variables, **kwargs):
    """Enhanced violin plot that handles both univariate and bivariate cases with NaN handling."""
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.setp(ax.get_xticklabels(), rotation=90, ha='center')

    if len(variables) == 1:
        # Univariate case - single numerical variable
        data = df[variables[0]].dropna()
        if data.empty:
            raise ValueError(f"No valid data remaining after dropping NaN values for {variables[0]}")
        ax.violinplot(data, **kwargs)
        ax.set_ylabel(variables[0])
        ax.set_title(f"Violin plot of {variables[0]}")
    elif len(variables) >= 2:
        # Bivariate case - numerical vs categorical
        num, cat = variables[0], variables[1]

        # Clean data - remove rows where either variable is NaN
        clean_data = df[[num, cat]].dropna()
        if clean_data.empty:
            raise ValueError(f"No valid data remaining after cleaning {num} and {cat}")

        # Group data by categorical variable
        grouped_data = [
            clean_data[clean_data[cat] == c][num]
            for c in clean_data[cat].unique()
        ]

        # Filter out empty groups
        grouped_data = [g for g in grouped_data if len(g) > 0]
        if not grouped_data:
            raise ValueError("No valid groups remaining after filtering")

        ax.violinplot(grouped_data, **kwargs)
        ax.set_xticks(np.arange(1, len(grouped_data) + 1))
        ax.set_xticklabels(clean_data[cat].unique())
        ax.set_xlabel(cat)
        ax.set_ylabel(num)
        ax.set_title(f"Violin plot of {num} by {cat}")
    else:
        raise ValueError("Violin plot requires at least one variable")

    return fig

