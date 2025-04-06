import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from explanations import refine_plot_explanation

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

