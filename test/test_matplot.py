import pandas as pd
import pytest
from plotsense.plot_generator.plt_matplot import PlotMatplot
from unittest.mock import patch


# Test for bar plot
@patch('matplotlib.pyplot.show')
def test_bar_plot(mock_show):
    sample_df = pd.DataFrame({'x': ['A', 'B', 'C'], 'y': [10, 20, 15]})
    plotter = PlotMatplot(sample_df)

    try:
        plotter.generate_barplot(x_col='x', y_col='y', color='red')
        print("Bar plot generated successfully")
    except Exception as e:
        print(f"Bar plot test failed: {e}")


# Test for line plot
@patch('matplotlib.pyplot.show')
def test_line_plot(mock_show):
    sample_df = pd.DataFrame({'x': [1, 2, 3], 'y': [10, 20, 15]})
    plotter = PlotMatplot(sample_df)

    try:
        plotter.generate_lineplot(x_col='x', y_col='y', color='green', marker='^', linestyle='--')
        print("Line plot generated successfully")
    except Exception as e:
        print(f"Line plot test failed: {e}")

# Test for scatter plot
@patch('matplotlib.pyplot.show')
def test_scatter_plot(mock_show):
    sample_df = pd.DataFrame({'x': [1, 2, 3], 'y': [10, 20, 15]})
    plotter = PlotMatplot(sample_df)

    try:
        plotter.generate_scatterplot(x_col='x', y_col='y', color='purple')
        print("Scatter plot generated successfully")
    except Exception as e:
        print(f"Scatter plot test failed: {e}")


# Test for histogram plot
@patch('matplotlib.pyplot.show')
def test_histogram_plot(mock_show):
    sample_df = pd.DataFrame({'values': [1, 2, 2, 3, 3, 3, 4, 4, 5]})
    plotter = PlotMatplot(sample_df)

    try:
        plotter.generate_histogram(y_col='values', color='orange', bins=5)
        print("Histogram plot generated successfully")
    except Exception as e:
        print(f"Histogram plot test failed: {e}")