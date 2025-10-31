from typing import List
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def create_bar_plot(df: pd.DataFrame, variables: List[str], **kwargs):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Extract label-related kwargs if provided
    x_label = kwargs.pop('x_label', None)
    y_label = kwargs.pop('y_label', None)
    title = kwargs.pop('title', None)

    # Define font sizes
    tick_fontsize = kwargs.pop('tick_fontsize', 12)
    label_fontsize = kwargs.pop('label_fontsize', 14)
    title_fontsize = kwargs.pop('title_fontsize', 16)

    if len(variables) == 1:
        value_counts = df[variables[0]].value_counts().sort_values(ascending=False)
        ax.bar(
            value_counts.index.astype(str),
            np.asarray(value_counts.values, **kwargs)
        )
        ax.set_xlabel(variables[0] if x_label is None else x_label, fontsize=label_fontsize)
        ax.set_ylabel('Count' if y_label is None else y_label, fontsize=label_fontsize)
        ax.set_title(f"Bar plot of {variables[0]}" if title is None else title, fontsize=title_fontsize)
        ax.tick_params(axis='x', labelsize=tick_fontsize)
        ax.tick_params(axis='y', labelsize=tick_fontsize)
        if len(value_counts) > 10:
            fig.set_size_inches(max(12, len(value_counts)), 8)
            plt.setp(ax.get_xticklabels(), rotation=90, ha='center')
    else:
        grouped = df.groupby(variables[1])[variables[0]].mean()
        grouped = pd.Series(grouped).sort_values(ascending=False)
        ax.bar(grouped.index.astype(str), np.asarray(grouped.values), **kwargs)
        ax.set_xlabel(variables[1] if x_label is None else x_label, fontsize=label_fontsize)
        ax.set_ylabel(f"{variables[0]}" if y_label is None else y_label, fontsize=label_fontsize)
        ax.set_title(f"{variables[0]} by {variables[1]}" if title is None else title, fontsize=title_fontsize)
        ax.tick_params(axis='x', labelsize=tick_fontsize)
        ax.tick_params(axis='y', labelsize=tick_fontsize)
        if len(grouped) > 10:
            fig.set_size_inches(max(12, len(grouped)), 8)
            plt.setp(ax.get_xticklabels(), rotation=90, ha='center')
    return fig

