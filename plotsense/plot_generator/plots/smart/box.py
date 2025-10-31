from typing import List
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

def create_box_plot(df: pd.DataFrame, variables: List[str], **kwargs) -> Figure:
    """Enhanced boxplot that handles both univariate and bivariate cases with NaN handling."""
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.setp(ax.get_xticklabels(), rotation=90, ha='center')
    
    if len(variables) == 1:
        # Univariate case - single numerical variable
        data = df[variables[0]].dropna()  # Remove NaN values
        if data.empty:
            raise ValueError(f"No valid data remaining after dropping NaN values for {variables[0]}")
        ax.boxplot(data, **kwargs)
        ax.set_ylabel(variables[0])
        ax.set_title(f"Box plot of {variables[0]}")
    elif len(variables) >= 2:
        # Bivariate case - numerical vs categorical
        numerical_var = variables[0]
        categorical_var = variables[1]
        
        # Clean data - remove rows where either variable is NaN
        clean_data = df[[numerical_var, categorical_var]].dropna()
        if clean_data.empty:
            raise ValueError(f"No valid data remaining after cleaning {numerical_var} and {categorical_var}")
        
        # Group data by categorical variable
        grouped_data = [
            clean_data[clean_data[categorical_var] == cat][numerical_var] 
            for cat in clean_data[categorical_var].unique()
        ]
        
        # Filter out empty groups
        grouped_data = [group for group in grouped_data if len(group) > 0]
        if not grouped_data:
            raise ValueError("No valid groups remaining after filtering")
            
        ax.boxplot(grouped_data, **kwargs)
        ax.set_xticklabels(clean_data[categorical_var].unique())
        ax.set_xlabel(categorical_var)
        ax.set_ylabel(numerical_var)
        ax.set_title(f"Box plot of {numerical_var} by {categorical_var}")
    else:
        raise ValueError("Box plot requires at least 1 variable")
        
    return fig

