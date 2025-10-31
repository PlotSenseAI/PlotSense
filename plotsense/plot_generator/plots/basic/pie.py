from typing import List
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def create_pie_plot(df, variables: List[str], **kwargs) -> Figure:
    value_counts = df[variables[0]].value_counts()
    fig, ax = plt.subplots()
    ax.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', **kwargs)
    ax.set_title(f"Pie chart of {variables[0]}")
    return fig


