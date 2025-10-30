from typing import List


def set_labels(ax, variables: List[str]):
    """Set labels for x and y axes based on variables."""
    if len(variables) > 0:
        ax.set_xlabel(variables[0])
    if len(variables) > 1:
        ax.set_ylabel(variables[1])

