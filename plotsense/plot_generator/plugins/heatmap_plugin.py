import seaborn as sns
import matplotlib.pyplot as plt

def _create_heatmap(data, variables, **kwargs):
    fig, ax = plt.subplots()
    sns.heatmap(
        data[variables].corr(),
        annot=True,
        cmap="coolwarm",
        ax=ax,
        **kwargs
    )
    ax.set_title("Heatmap")
    return fig

def get_plots():
    print("Heatmap plugin loaded!")
    return {"heatmap": _create_heatmap}
