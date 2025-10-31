from typing import Callable, Dict, List, Optional, Any
import pandas as pd
from dataclasses import dataclass

@dataclass
class PlotRequirements():
    """Define constraints for a plot type."""
    min_variables: int = 1     # minimum required variables
    max_variables: int = 2     # maximum supported variables
    numeric_only: bool = True  # whether data must be numeric

class PlotTypeRegistry:
    """Central registry for all supported plot types."""

    def __init__(self):
        self._registry: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, requirements: PlotRequirements, generator: Callable):
        """Register a plot type and its generation function."""
        self._registry[name.lower()] = {
            "requirements": requirements,
            "generator": generator
        }

    def get_generator(self, name: str) -> Optional[Callable]:
        """Retrieve generator function by plot type name."""
        entry = self._registry.get(name.lower())
        return entry["generator"] if entry else None

    def validate(self, name: str, variables: List[str], df: pd.DataFrame) -> bool:
        """Check if given data fits the plot type requirements."""
        entry = self._registry.get(name.lower())
        if not entry:
            return False

        req = entry["requirements"]
        if not (req.min_variables <= len(variables) <= req.max_variables):
            return False

        if req.numeric_only:
            for var in variables:
                if not pd.api.types.is_numeric_dtype(df[var]):
                    return False
        return True

    def list_plot_types(self) -> List[str]:
        """List all registered plot types."""
        return list(self._registry.keys())

