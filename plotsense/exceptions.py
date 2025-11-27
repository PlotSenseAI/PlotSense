
class PlotSenseError(Exception):
    """Base class for all PlotSense exceptions."""
    pass


class PlotSenseAPIError(ConnectionError):
    """Errors when calling external APIs (LLMs, services, etc.)."""
    pass


class PlotSenseDataError(ValueError):
    """Errors related to invalid or unusable user data."""
    pass


class PlotSenseConfigError(KeyError):
    """Errors related to configuration / missing API keys, etc."""

    def __str__(self):
        return str(self.args[0]) if self.args else super().__str__()
    pass
