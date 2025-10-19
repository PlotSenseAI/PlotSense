import matplotlib.pyplot as plt
import seaborn as sns

def _create_lineplot(data, variables, **kwargs):
    """
    Create a line plot using the first variable as x and the second as y.
    Example: variables = ["x_column", "y_column"]
    """
    if len(variables) < 2:
        raise ValueError("Lineplot requires at least two variables: x and y.")

    x_col, y_col = variables[0], variables[1]

    fig, ax = plt.subplots()
    sns.lineplot(data=data, x=x_col, y=y_col, ax=ax, **kwargs)
    ax.set_title(f"Line plot of {y_col} vs {x_col}")
    return fig

def get_plots():
    return {"lineplot": _create_lineplot}
