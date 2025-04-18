import matplotlib.pyplot as plt
import pandas as pd
from functools import wraps
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time} to execute")
        return result
    return wrapper

def logging_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            print(f"Error in {func.__name__}: {e}")
            return None
    return wrapper
             

class PlotMatplot:

    """
    Initialize the plot generator with a dataframe
    """
    
    def __init__(self, df):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input should be a pandas DataFrame")
        self.df = df

    @logging_decorator
    @timing_decorator
    def generate_barplot(self, x_col=None, y_col=None, **kwargs):
        """
        To generate a bar plot
        
        Parameters:
        - x_col (str): Column name for x-axis.
        - y_col (str): Column name for y-axis.
        - kwargs: Additional parameters to customize the plot.
        """
        
        if self.df is None or x_col is None or y_col is None:
            raise ValueError("Invalid input. Ensure DataFrame, x_col, and y_col are specified.")

        plt.figure(figsize=kwargs.get('figsize', (8, 5)))

        plt.bar(self.df[x_col], self.df[y_col], color=kwargs.get('color', 'skyblue'),
                edgecolor=kwargs.get('edgecolor', 'black'), linewidth=kwargs.get('linewidth', 1.5))

        plt.xlabel(kwargs.get('xlabel', x_col))
        plt.ylabel(kwargs.get('ylabel', y_col))
        plt.title(kwargs.get('title', "Bar Plot"))
        plt.grid(kwargs.get('grid', True))
        plt.show()
        
    @logging_decorator
    @timing_decorator
    def generate_lineplot(self, x_col=None, y_col=None, **kwargs):

        """
        To generate a line plot
        
        Parameters:
        - x_col (str): Column name for x-axis.
        - y_col (str): Column name for y-axis.
        - kwargs: Additional parameters to customize the plot.
        """

        if self.df is None or x_col is None or y_col is None:
            raise ValueError("Invalid input. Ensure DataFrame, x_col, and y_col are specified.")

        plt.figure(figsize=kwargs.get('figsize', (8, 5)))
        plt.plot(self.df[x_col], self.df[y_col], color=kwargs.get('color', 'blue'),
                        marker=kwargs.get('marker', 'o'), linestyle=kwargs.get('linestyle', '-'))

        plt.xlabel(kwargs.get('xlabel', x_col))
        plt.ylabel(kwargs.get('ylabel', y_col))
        plt.title(kwargs.get('title', "LinePlot"))
        plt.grid(kwargs.get('grid', True))
        plt.show()
        
    @logging_decorator
    @timing_decorator
    def generate_scatterplot(self, x_col=None, y_col=None, **kwargs):

        """
        To generate a scatter plot
        
        Parameters:
        - x_col (str): Column name for x-axis.
        - y_col (str): Column name for y-axis.
        - kwargs: Additional parameters to customize the plot.
        """

        if self.df is None or x_col is None or y_col is None:
            raise ValueError("Invalid input. Ensure DataFrame, x_col, and y_col are specified.")


        plt.figure(figsize=kwargs.get('figsize', (8, 5)))
        plt.scatter(self.df[x_col], self.df[y_col], color=kwargs.get('color', 'red'))

        plt.xlabel(kwargs.get('xlabel', x_col))
        plt.ylabel(kwargs.get('ylabel', y_col))
        plt.title(kwargs.get('title', "ScatterPlot"))
        plt.grid(kwargs.get('grid', True))
        plt.show()
        
    @logging_decorator
    @timing_decorator
    def generate_histogram(self, y_col=None, **kwargs):

        """
        To generate an  histogram plot
        
        Parameters:
        - y_col (str): Column name for histogram.
        - kwargs: Additional parameters to customize the plot.
        """

        if self.df is None or y_col is None:
            raise ValueError("Invalid input. Ensure DataFrame and y_col are specified.")

        plt.figure(figsize=kwargs.get('figsize', (8, 5)))
        plt.hist(self.df[y_col], bins=kwargs.get('bins', 10), color=kwargs.get('color', 'blue'),
                    edgecolor=kwargs.get('edgecolor', 'black'), alpha=kwargs.get('alpha', 0.7))
        
        plt.xlabel(kwargs.get('xlabel', 'Value'))
        plt.ylabel(kwargs.get('ylabel', y_col))
        plt.title(kwargs.get('title', "Histogram"))
        plt.grid(kwargs.get('grid', True))
        plt.show()

