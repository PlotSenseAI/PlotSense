from plotsense.plot_generator.base_generator import PlotGenerator
from plotsense.plot_generator.plots.smart.box import create_box_plot
from plotsense.plot_generator.plots.smart.ecdf import create_ecdf_plot
from plotsense.plot_generator.plots.smart.histogram import create_histogram_plot
from plotsense.plot_generator.plots.smart.kde import create_kde_plot
from plotsense.plot_generator.plots.smart.scatter import create_scatter_plot
from plotsense.plot_generator.plots.smart.violin import create_violin_plot


class SmartPlotGenerator(PlotGenerator):
    """
    An enhanced PlotGenerator with advanced plotting capabilities.
    """

    @property
    def _default_plots(self):
        return {
            'box': create_box_plot,
            'ecdf': create_ecdf_plot,
            'histogram': create_histogram_plot,
            'kde': create_kde_plot,
            'scatter': create_scatter_plot,
            'violin': create_violin_plot,
        }

