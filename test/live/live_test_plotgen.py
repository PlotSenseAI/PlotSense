import pandas as pd
import matplotlib.pyplot as plt

from plotsense.plot_generator.generator import plotgen

df = pd.DataFrame({
    "a": range(10),
    "b": range(10, 20)
})

suggestions_df = pd.DataFrame([
    {"plot_type": "scatter", "variables": "a,b"}
])

# Standard plot
fig1 = plotgen(df, 0, suggestions_df, generator="smart")

# ---------

# Custom plot
def my_custom_plot(df, vars, **kwargs):
    fig, ax = plt.subplots()
    ax.plot(df[vars[0]], df[vars[1]], color="red")
    return fig

fig2 = plotgen(
    df, 0, suggestions_df,
    generator="smart",
    plot_function=my_custom_plot,
    plot_type="my_line"
)

# ---------

# Create sample DataFrame
df = pd.DataFrame({
    "height": [165, 170, 175, 160, 172, 168, 180, 177, 169, 174]
})

# Simulate a recommendation DataFrame (just like your usual `suggestions_df`)
suggestions_df = pd.DataFrame([
    {"plot_type": "kde", "variables": "height"}
])

# Generate KDE Plot
fig_kde = plotgen(df, 0, suggestions_df, generator="smart")

# ---------

# Create sample DataFrame
df = pd.DataFrame({
    "scores": [60, 72, 85, 90, 66, 75, 88, 93, 70, 80]
})

# Simulate recommendation DataFrame
suggestions_df = pd.DataFrame([
    {"plot_type": "ecdf", "variables": "scores"}
])

# Generate ECDF Plot
fig_ecdf = plotgen(df, 0, suggestions_df, generator="smart")

plt.show()

