import seaborn as sns
import matplotlib.pyplot as plt

# This function draws a correlation heatmap for numeric columns
def correlation_analysis(data, variables=None, **kwargs):
    numeric_data = data.select_dtypes(include=["number"])
    corr = numeric_data.corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Matrix")

    # Return the figure so PlotGenerator can handle it
    return plt.gcf()

# This function returns all the plots in this plugin
def get_plots():
    return {
        "correlation_analysis": correlation_analysis
    }
