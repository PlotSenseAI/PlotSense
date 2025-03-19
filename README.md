# PlotSense

**PlotSense** is an AI-powered Python package that provides intelligent data visualization suggestions. It helps data professionals automate the process of selecting the best visualizations based on data type, relationships, and user goals, making data exploration more efficient, insightful, and accessible.

## Features

- **AI-Powered Visualization Suggestions**: Automatically recommends the best visualizations based on data properties (e.g., numerical, categorical, correlations).
- **Explainability**: Explains why a specific visualization was chosen, helping users understand the rationale behind the suggestion.
- **Customization**: Allows users to customize visualizations by adjusting colors, labels, and more.

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

# Create Plots
plot1 = ps.plot(df)
plot2 = ps.plot(df['x','y'])

# Get explanation for the suggested visualization
explain_plot1 = ps.explain(plot1)
explain_plot2 = ps.explain(plot2)

print(explain_plot1)

```
# Branching Strategy
- main: The stable production-ready version of PlotSense.
- dev: Development branch for ongoing features.
- feature/<feature-name>: Branches for specific features (e.g., feature/ai-visualization-suggestions).
- release branching:
-  
# Contributing
We welcome contributions from the community! If you're interested in contributing to PlotSense, please follow these steps:

Fork the repository on GitHub.
- Clone your fork and create a new branch (eg. feature/bug) for your feature or bugfix.
- Commit your changes to the new branch, ensuring that you follow coding standards and write appropriate tests.
- Push your changes to your fork on GitHub.
- Submit a pull request to the main repository, detailing your changes and referencing any related issues.

Here’s how you can help:
- **Bug Reports**: Open an issue to report a bug.
- **Feature Requests**: Suggest new features by opening an issue.
- **Pull Requests**: Fork the repository, create a new branch, and submit a pull request.
Please ensure that you follow the code of conduct and include tests for new features.



