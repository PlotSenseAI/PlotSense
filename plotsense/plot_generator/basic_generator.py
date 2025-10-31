from plotsense.plot_generator.base_generator import PlotGenerator
from plotsense.plot_generator.plots.basic.kde import create_kde_plot
from plotsense.plot_generator.plots.basic.barh import create_barh_plot
from plotsense.plot_generator.plots.basic.box import create_box_plot
from plotsense.plot_generator.plots.basic.ecdf import create_ecdf_plot
from plotsense.plot_generator.plots.basic.hist import create_hist_plot
from plotsense.plot_generator.plots.basic.violin import create_violin_plot
from plotsense.plot_generator.plots.basic.bar import create_bar_plot
from plotsense.plot_generator.plots.basic.hexbin import create_hexbin_plot
from plotsense.plot_generator.plots.basic.pie import create_pie_plot
from plotsense.plot_generator.plots.basic.scatter import create_scatter_plot


class BasicPlotGenerator(PlotGenerator):
    @property
    def _default_plots(self):
        return {
            'bar': create_bar_plot,
            'barh': create_barh_plot,
            'box': create_box_plot,
            'ecdf': create_ecdf_plot,
            'hexbin': create_hexbin_plot,
            'hist': create_hist_plot,
            'kde': create_kde_plot,
            'pie': create_pie_plot,
            'scatter': create_scatter_plot,
            'violin': create_violin_plot,
        }

