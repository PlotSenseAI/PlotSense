import pandas as pd
import pytest
from plotsense.plot_generator.altoplot import PlotMatplot



def test_bar_plot():
    sample_df = pd.DataFrame({'x': ['A', 'B', 'C'], 'y': [10, 20, 15]})
    plotter = PlotMatplot(sample_df)

    try:
        plotter.generate_plot("bar", x_col='x', y_col='y', color='red')
        print("Bar plot generated successfully")
    except Exception as e:
        print(f"Bar plot test failed: {e}")

def test_line_plot():
    sample_df = pd.DataFrame({'x': [1, 2, 3], 'y': [10, 20, 15]})
    plotter = PlotMatplot(sample_df)

    try:
        plotter.generate_plot("plot", x_col='x', y_col='y', color='green', marker='^', linestyle='--')
        print("Line plot generated successfully")
    except Exception as e:
        print(f"Line plot test failed: {e}")



def test_scatter_plot():
    sample_df = pd.DataFrame({'x': [1, 2, 3], 'y': [10, 20, 15]})
    plotter = PlotMatplot(sample_df)

    try:
        plotter.generate_plot("scatter", x_col='x', y_col='y', color='purple')
        print("Scatter plot generated successfully")
    except Exception as e:
        print(f"Scatter plot test failed: {e}")

def test_histogram_plot():
    sample_df = pd.DataFrame({'values': [1, 2, 2, 3, 3, 3, 4, 4, 5]})
    plotter = PlotMatplot(sample_df)

    try:
        plotter.generate_plot("hist", x_col='values', color='red', bins=5)
        print("Histogram plot generated successfully")
    except Exception as e:
        print(f"Histogram plot test failed: {e}")

