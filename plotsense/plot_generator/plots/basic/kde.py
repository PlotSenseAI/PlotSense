import matplotlib.pyplot as plt

def create_kde_plot(df, variables, **kwargs):
    """Kernel Density Estimation plot for a numeric variable."""
    var = variables[0]
    data = df[var].dropna()
    if data.empty:
        raise ValueError(f"No valid data for {var}")

    fig, ax = plt.subplots(figsize=(8, 5))
    data.plot(kind='kde', ax=ax, **kwargs)
    ax.set_title(f"KDE Plot of {var}")
    ax.set_xlabel(var)
    ax.set_ylabel("Density")
    return fig

