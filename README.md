# PlotSense
PlotSense is an AI-powered Python package that automatically suggests the best visualizations for your data. It leverages machine learning to select the most effective chart types based on dataset characteristics, providing explainable insights.

# PlotSense

**PlotSense** is an AI-powered Python package that provides intelligent data visualization suggestions. It helps data professionals automate the process of selecting the best visualizations based on data type, relationships, and user goals, making data exploration more efficient, insightful, and accessible.

## Features

- **AI-Powered Visualization Suggestions**: Automatically recommends the best visualizations based on data properties (e.g., numerical, categorical, correlations).
- **Explainability**: Explains why a specific visualization was chosen, helping users understand the rationale behind the suggestion.
- **Data Profiling**: Analyzes the dataset and provides key statistics, including data types, missing values, and correlations.
- **Customization**: Allows users to customize visualizations by adjusting colors, labels, and more.
- **Interactive Visualizations**: Leverages powerful libraries like `Plotly` for interactive charts.

## Installation

To install PlotSense, use pip:

```bash
pip install plotsense
import plotsense as ps
```
## Example 1: AI-Powered Visualisation Suggestions
```bash
# Load your dataset (e.g., pandas DataFrame)
import pandas as pd
df = pd.read_csv('your-dataset.csv')

# Get AI-powered visualization suggestions
suggestions = ps.suggest_visualizations(df)

# Plot the recommended visualization
suggestions['best_visualization'].plot()

# You can also provide additional user goals
suggestions = ps.suggest_visualizations(df, goal="compare two numerical variables")

# Get explanation for the suggested visualization
explanation = suggestions['best_visualization_explanation']
print(explanation)

```
# Contributing
We welcome contributions from the community! If you're interested in contributing to AutoViz, please follow these steps:

Fork the repository on GitHub.
Clone your fork and create a new branch for your feature or bugfix.
Commit your changes to the new branch, ensuring that you follow coding standards and write appropriate tests.
Push your changes to your fork on GitHub.
Submit a pull request to the main repository, detailing your changes and referencing any related issues.

Here’s how you can help:
- **Bug Reports**: Open an issue to report a bug.
- **Feature Requests**: Suggest new features by opening an issue.
- **Pull Requests**: Fork the repository, create a new branch, and submit a pull request.
Please ensure that you follow the code of conduct and include tests for new features.

