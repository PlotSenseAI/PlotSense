import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from plotsense.explanations.explanations import PlotExplainer
from PlotExplainer import refine_plot_explanation

# # Ensure the parent directory (PlotSenseAI) is in Python's path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the PlotExplainer class from explanations.py


def test_complex_plot_explanation():
    # Create a complex plot
    tips = sns.load_dataset('tips')
    fig, ax = plt.subplots()
    sns.boxplot(data=tips, x='day', y='total_bill', hue='sex', ax=ax)
    # Get explanation
    explanation = refine_plot_explanation(
        fig )
    print("Generated Explanation:")
    print(explanation)

test1 = test_complex_plot_explanation
print(test1)

# # Initialize PlotExplainer with the Groq API key
# explainer = PlotExplainer(api_keys={'groq': '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'})

# # Check available models
# print("Available models:", explainer.available_models)

# # Test the Groq model with a sample prompt
# prompt = "Explain this plot in detail."
# response = explainer.test_model('groq', prompt)

# # Print the response from the model
# print("Model Response:\n", response)
