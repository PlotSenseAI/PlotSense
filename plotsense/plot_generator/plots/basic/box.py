from typing import List
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


def create_box_plot(df, variables: List[str], **kwargs) -> Figure:
    fig, ax = plt.subplots(figsize=(10,6))
    plt.setp(ax.get_xticklabels(), rotation=90, ha='center')
    
    ax.boxplot(df[variables[0]], **kwargs)
    ax.set_ylabel(variables[0])
    ax.set_title(f"Box plot of {variables[0]}")

    return fig

