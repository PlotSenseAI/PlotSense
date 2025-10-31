from typing import List
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

def create_barh_plot(df, variables: List[str], **kwargs) -> Figure:
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
        # Single variable - show value counts
        value_counts = df[variables[0]].value_counts()
        ax.barh(value_counts.index.astype(str), value_counts.values, **kwargs)
        ax.set_xlabel(variables[0] if x_label is None else x_label, fontsize=label_fontsize)
        ax.set_ylabel('Count' if y_label is None else y_label, fontsize=label_fontsize)
        ax.set_title(f"Bar plot of {variables[0]}" if title is None else title, fontsize=title_fontsize)
        ax.tick_params(axis='x', labelsize=tick_fontsize)
        ax.tick_params(axis='y', labelsize=tick_fontsize)

        if len(value_counts) > 10:
            fig.set_size_inches(max(12, len(value_counts)), 8)
            plt.setp(ax.get_xticklabels(), rotation=90, ha='center')
            
    else:
        # First variable is numeric, second is categorical
        grouped = df.groupby(variables[1])[variables[0]].mean()
        ax.barh(grouped.index.astype(str), grouped.values, **kwargs)
        ax.set_xlabel(variables[1] if x_label is None else x_label, fontsize=label_fontsize)
        ax.set_ylabel(f"{variables[0]}" if y_label is None else y_label, fontsize=label_fontsize)
        ax.set_title(f"{variables[0]} by {variables[1]}" if title is None else title, fontsize=title_fontsize)
        ax.tick_params(axis='x', labelsize=tick_fontsize)
        ax.tick_params(axis='y', labelsize=tick_fontsize)

        if len(grouped) > 10:
            fig.set_size_inches(max(12, len(grouped)), 8)
            plt.setp(ax.get_xticklabels(), rotation=90, ha='center')
        
    return fig

