import pandas as pd
from pprint import pprint
from typing import Dict, List, Optional, Tuple

from plotsense.core.ai_interface import AIModelInterface
from plotsense.core.enums.strategy import StrategyName
from plotsense.core.providers.provider_manager import ProviderManager
from plotsense.visual_suggestion.recommender.dataframe_analyzer import DataFrameAnalyzer
from plotsense.visual_suggestion.recommender.ensemble_scorer import EnsembleScorer
from plotsense.visual_suggestion.recommender.prompt_builder import PromptBuilder
from plotsense.visual_suggestion.recommender.response_parser import ResponseParser


class VisualizationRecommender:

    def __init__(
        self,
        api_keys: Optional[Dict[str, str]] = None,
        strategy: StrategyName = StrategyName.ROUND_ROBIN,
        selected_models: Optional[List[Tuple[str, str]]] = None,
        timeout: int = 30,
        interactive: bool = True,
        debug: bool = False,
    ):
        """
        Initialize VisualizationRecommender with API keys and configuration.
        
        Args:
            api_keys: Optional dictionary of API keys. If not provided,
                     keys will be loaded from environment variables.
            timeout: Timeout in seconds for API requests
            interactive: Whether to prompt for missing API keys
            debug: Enable debug output
        """
        self.api_keys = api_keys or {}

        self.timeout = timeout
        self.interactive = interactive
        self.debug = debug
        self.strategy_name = strategy

        selected_providers = {p for p, _ in (selected_models or [])}

        self.manager = ProviderManager(
            api_keys=self.api_keys,
            interactive=interactive,
            restrict_to=list(selected_providers) if selected_providers else None
        )
        self.ai_interface = AIModelInterface(self.manager, timeout=self.timeout)

        all_models = self.manager.list_all_models()
        self.available_models = [
            (provider, model)
            for provider, models in all_models.items()
            for model in models
        ]

        if not self.available_models:
            raise ValueError(
                "No available models detected — check API keys or selection input."
            )

        # initialize strategy instance
        self.strategy = self.ai_interface._init_strategy(
            self.strategy_name, self.available_models
        )

        self.df = None
        # model_weights will be lazily obtained from AIModelInterface if not provided
        self.model_weights = {}

        if self.debug:
            print("\n[DEBUG] Initialization Complete")
            print(f"Available models: {self.available_models}")
            print(f"Model weights: {self.model_weights}")

    def set_dataframe(self, df: pd.DataFrame):
        """Set the DataFrame to analyze and provide debug info"""
        self.df = df
        if self.debug:
            print("\n[DEBUG] DataFrame Info:")
            print(f"Shape: {df.shape}")
            print("Columns:", df.columns.tolist())
            print("\nSample data:")
            print(df.head(2))

    def recommend_visualizations(
        self, n: int = 5, custom_weights: Optional[Dict[str, float]] = None
    ) -> pd.DataFrame:
        """
        Generate visualization recommendations using weighted ensemble approach.
        
        Args:
            n: Number of recommendations to return (default: 3)
            custom_weights: Optional dictionary to override default model weights
            
        Returns:
            pd.DataFrame: Recommended visualizations with ensemble scores
            
        Raises:
            ValueError: If no DataFrame is set or no models are available
        """
        """Generate visualization recommendations using weighted ensemble approach."""
        self.n_to_request = max(n, 5)
        
        if self.df is None:
            raise ValueError("No DataFrame set. Call set_dataframe() first.")

        if not self.available_models:
            raise ValueError("No available models detected")

        if self.debug:
            print("\n[DEBUG] Starting recommendation process")
            print(f"Using models: {self.available_models}")
 
        # Use custom weights if provided, otherwise try self.model_weights then ai_interface weights
        if custom_weights:
            weights = custom_weights
        elif self.model_weights:
            weights = self.model_weights
        else:
            # Defer to AIModelInterface for default weights (keeps compatibility with provider-manager)
            weights = self.ai_interface.get_model_weights()

        # Get recommendations from all models in parallel via AIModelInterface
        analyzer = DataFrameAnalyzer(self.df)
        df_description = analyzer.describe_dataframe()
        prompt = PromptBuilder(self.n_to_request).build_prompt(df_description)

        if self.debug:
            print("\n[DEBUG] Prompt being sent to models:")
            print(prompt)

        # Expecting ai_interface.query_all_models to return dict { "provider:model": "raw text" }
        all_recommendations = self.ai_interface.query_all_models(
            prompt, self.debug
        )

        if self.debug:
            print("\n[DEBUG] Raw recommendations from models:")
            pprint(all_recommendations)

        # Parse model responses into structured recommendation lists
        parser = ResponseParser(self.df, debug=self.debug)
        parsed_recs = {
            model: parser.parse_recommendations(response, model)
            for model, response in all_recommendations.items()
        }

        if self.debug:
            print("\n[DEBUG] Applying ensemble scoring")

        scorer = EnsembleScorer(
            self.df, debug=self.debug,
            available_models=self.available_models
        )
        # Use weights determined above (which respects custom_weights)
        ensemble_df = scorer.apply_ensemble_scoring(parsed_recs, weights)

        final_df = pd.DataFrame()
        # Validate and correct variable order
        if not ensemble_df.empty:
            final_df = parser.validate_variable_order(ensemble_df)

        # If we don't have enough results, try to supplement (mirror original behavior)
        if len(final_df) < n:
            if self.debug:
                print(f"\n[DEBUG] Only got {len(final_df)} recommendations, trying to supplement")
            # Use the same ensemble_df context when supplementing, so the scorer/parser can access source_models
            supplemented = scorer.supplement_recommendations(ensemble_df, n)
            return supplemented
        
        if self.debug:
            print("\n[DEBUG] Ensemble results before filtering:")
            print(ensemble_df)
 
        # Return the validated & ordered results (top-n)
        return ensemble_df.head(n)

