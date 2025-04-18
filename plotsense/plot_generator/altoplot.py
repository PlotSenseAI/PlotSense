import inspect
import matplotlib.pyplot as plt


class PlotMatplot:

    def __init__(self, df):
        self.available_plots = self.discover_matplotlib_plots()
        self.df = df

    @staticmethod
    def discover_matplotlib_plots():
        """
        Dynamically discover plotting functions in matplotlib.pyplot by inspecting their signatures.
        A function is considered a plotting function if it has parameters like 'x', 'y', 'height', etc.
        """
        plot_functions = []
        for name, func in inspect.getmembers(plt, inspect.isfunction):
            if name.startswith('_'):
                continue

            try:
                signature = inspect.signature(func)
                params = signature.parameters.keys()
            except ValueError:
                # Some functions (e.g., C-based) may not have a signature
                continue

            # Characteristics of a plotting function:
            # - Has parameters like 'x', 'y', 'height', 'width', 'data', etc.
            # - Does not primarily deal with labels, titles, or axes (e.g., 'xlabel', 'title')
            plot_related_params = {'x', 'y', 'height', 'width', 'data', 'z', 'c', 's', 'vmin', 'vmax'}
            non_plot_indicators = {'label', 'fontsize', 'loc', 'ncol', 'nrows'}  # Common in non-plot functions

            # Check if the function has plot-related parameters
            has_plot_params = any(param in params for param in plot_related_params)
            # Check if the function is primarily a non-plot function (e.g., 'xlabel', 'title')
            is_non_plot = any(param in params for param in non_plot_indicators) and not has_plot_params

            if has_plot_params and not is_non_plot:
                plot_functions.append(name)

        return plot_functions
    
    def generate_plot(self, suggested_plot, x_col=None, y_col=None, **kwargs):
        if suggested_plot not in self.available_plots:
            raise ValueError(f"{suggested_plot} is not a recognized matplotlib plot function.")

        # Get the actual plot function
        plot_func = getattr(plt, suggested_plot)

        # Inspect accepted parameters for this plot function
        try:
            sig = inspect.signature(plot_func)
            valid_params = sig.parameters
        except ValueError:
            valid_params = {}

        # Build plot arguments dynamically
        plot_args = {}

        # Automatically pass x and y if they're in the function signature
        if 'x' in valid_params and x_col:
            plot_args['x'] = self.df[x_col]
        if 'y' in valid_params and y_col:
            plot_args['y'] = self.df[y_col]
        if 'height' in valid_params and y_col:
            plot_args['height'] = self.df[y_col]
        if 'width' in valid_params and x_col:
            plot_args['width'] = self.df[x_col]

        # Add additional keyword arguments if they match the function's parameters
        for key, value in kwargs.items():
            if key in valid_params:
                plot_args[key] = value

        # Plot it!
        plot_func(**plot_args)
        plt.title(f"{suggested_plot} of {x_col} vs {y_col}")
        plt.xlabel(x_col if x_col else '')
        plt.ylabel(y_col if y_col else '')
        plt.grid(True)
        plt.show()