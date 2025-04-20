# PlotSense: AI-Powered Data Visualization Assistant

## Overview
**PlotSense** is your AI copilot for data visualization, offering:

- Intelligent Visualization Suggestions - Recommends the best charts for your data
- Explanation Engine - Generates natural language explanations for any plot
- Seamless Integration - Works with Pandas, Matplotlib & Seaborn

It helps data professionals automate visualization selection based on data properties, relationships, and user goals, making EDA (Exploratory Data Analysis) faster and more insightful.

## Quick Setup 

Install via pip

```bash
pip install plotsense
import plotsense as ps
from plotsense import refine_plot_explanation, recommend_visualizations

```
Before using the package, you'll need to:

- Obtain a Groq API key from Groq Cloud https://console.groq.com/home
- Provide the API key when you first use the package

```bash
import os
os.environ['GROQ_API_KEY'] = 'your-api-key-here'
```
## Core Features
### Intelligent Visualization Suggestions

```bash
# Load your dataset (e.g., pandas DataFrame)
df = pd.read_csv("data.csv")

# Get AI-recommended visualizations
suggestions = ps.suggest_visualizations(df)

# Output
print(suggestions)

    plot_type	variables	        rationale	                                        ensemble_score
0	bar chart	survived, pclass	This visualization helps us understand the sur...	1.0
1	bar chart	survived, sex	    This visualization can reveal the difference i...	0.6
2	histogram	age	                This histogram provides a detailed view of the...	0.5
```

### One-Click Plot Generation using suggestion indexes

```bash
plot1 = ps.plot(df, suggestions[0]) # This will plot a bar chart with variables 'survived', 'pclass'
plot2 = ps.plot(df, suggestions[1]) # This will plot a bar chart with variables 'survived', 'sex'
plot3 = ps.plot(df, suggestions[2]) # This will plot a histogram with variable 'age'
```
You can also specify arguments
``` bash
plot1 = ps.plot(df, suggestions[0], x='pclass', y='survived') 
```
### Explanation Engine - AI-Powered Insights
``` bash
explanation = ps.refine_plot_explanation(plot1)

print(explanation)
```
### Advanced Explanation Engine Usage
- Custom Prompts: You can provide your own prompt to guide the explanation

``` bash
explanation = refine_plot_explanation(
    fig,
    prompt="Explain the key trends in this sales data visualization"
)
```
- Multiple Refinement Iterations: Increase the number of refinement cycles for more polished explanations:

```bash  
explanation = refine_plot_explanation(
    fig,
    iterations=3  # Default is 2
)
```
- Using Different Models: The package automatically selects the best available model, but you can specify models:

``` bash
explanation = refine_plot_explanation(
    fig,
    model_rotation=['llama-3.2-90b-vision-preview']  # Use only this model
)
``` 

## Combined Workflow: Suggest → Plot → Explain (Seamless Integration)
``` bash
# Get AI-recommended plot type
best_plot = ps.suggest_visualizations(df)["best_choice"]  

# Generate the plot
plot = ps.plot(df, x="date", y="sales", plot_type=best_plot)  

# Get AI explanation
insight = pe.refine_plot_explanation(plot, prompt="Explain key insights") 
```

## Contributing
We welcome contributions!

### Branching Strategy
- main: The stable production-ready version of PlotSense.
- dev: Active development
- feature/<feature-name>: Branches for specific features (e.g., feature/ai-visualization-suggestions).

### How to Help
- **Bug Reports**: Open an issue to report a bug.
- **Feature Requests**: Suggest new features by opening an issue.
- **Pull Requests**: Fork the repository, create a new branch, and submit a pull request.

### Roadmap
- More model integrations
- Automated insight highlighting
- Jupyter widget support

``` bash
pip install --upgrade plotsense  # Get the latest features!
```

#  Notes
- The API key is stored in memory during your Python session
- The key is only sent to Groq's API servers for processing
- Visual Suggestions and Explanation Engine require an internet connection for API access. All processing happens on Groq's servers.



