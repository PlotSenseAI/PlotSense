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

# Raising and catching each exception
with pytest.raises(PlotSenseAPIError):
    raise PlotSenseAPIError("API error occurred")

with pytest.raises(PlotSenseDataError):
    raise PlotSenseDataError("Data error occurred")

with pytest.raises(PlotSenseConfigError):
    raise PlotSenseConfigError("Config error occurred")

with pytest.raises(PlotSenseError):
    raise PlotSenseError("error occurred")
