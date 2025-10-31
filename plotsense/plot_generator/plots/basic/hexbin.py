from typing import List
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

def create_hexbin_plot(df, variables: List[str], **kwargs) -> Figure:
    fig, ax = plt.subplots()
    ax.hexbin(df[variables[0]], df[variables[1]], **kwargs)
    df._set_labels(ax, variables)
    ax.set_title(f"Hexbin: {variables[0]} vs {variables[1]}")
    return fig

