from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import pandas as pd

from plotsense.core.enums.strategy import StrategyName
from plotsense.visual_suggestion.recommender.visualization_recommender import VisualizationRecommender


load_dotenv()

# Package-level convenience function
_recommender_instance = None

def recommender(
    df: pd.DataFrame,
    n: int = 5,

    custom_weights: Optional[Dict[str, float]] = None,
    strategy: StrategyName = StrategyName.ROUND_ROBIN,
    selected_models: Optional[List[Tuple[str, str]]] = None,

    api_keys: Optional[Dict[str, str]] = None,
    interactive: bool = True,
    timeout: int = 30,
    debug: bool = False
) -> pd.DataFrame:
    """
    Generate visualization recommendations using weighted ensemble of LLMs.
    
    Args:
        df: Input DataFrame to analyze
        n: Number of recommendations to return (default: 3)
        api_keys: Dictionary of API keys
        custom_weights: Optional dictionary to override default model weights
        debug: Enable debug output
        
    Returns:
        pd.DataFrame: Recommended visualizations with ensemble scores
    """
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = VisualizationRecommender(
            api_keys=api_keys,
            strategy=strategy,
            selected_models=selected_models,
            timeout=timeout,
            interactive=interactive,
            debug=debug
        )
    
    _recommender_instance.set_dataframe(df)
    return _recommender_instance.recommend_visualizations(
        n=n,
        custom_weights=custom_weights
    )

