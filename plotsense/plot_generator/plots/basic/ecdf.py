import matplotlib.pyplot as plt
import numpy as np

def create_ecdf_plot(df, variables, **kwargs):
    """Empirical Cumulative Distribution Function (ECDF) plot."""
    var = variables[0]
    data = df[var].dropna()
    if data.empty:
        raise ValueError(f"No valid data for {var}")

    sorted_data = np.sort(data)
    n = len(sorted_data)
    y = np.arange(1, n + 1) / n

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(sorted_data, y, marker='.', linestyle='none', **kwargs)
    ax.set_title(f"ECDF of {var}")
    ax.set_xlabel(var)
    ax.set_ylabel("Cumulative Probability")
    return fig

