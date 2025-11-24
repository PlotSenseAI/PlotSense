import pytest
from plotsense.exceptions import PlotSenseError, PlotSenseAPIError, PlotSenseDataError, PlotSenseConfigError


# Testing inheritance
err = PlotSenseAPIError("API failed")
assert isinstance(err, ConnectionError)

err = PlotSenseDataError("Invalid data")
assert isinstance(err, ValueError)

err = PlotSenseConfigError("Missing config")
assert isinstance(err, KeyError)

err = PlotSenseError("General error")
assert isinstance(err, Exception)
