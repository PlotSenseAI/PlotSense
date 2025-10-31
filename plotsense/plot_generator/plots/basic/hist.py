from typing import List
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

def create_hist_plot(df, variables: List[str], **kwargs) -> Figure:
    fig, ax = plt.subplots()
    ax.hist(df[variables[0]], **kwargs)
    ax.set_xlabel(variables[0])
    ax.set_ylabel('Frequency')
    ax.set_title(f"Histogram of {variables[0]}")
    return fig

