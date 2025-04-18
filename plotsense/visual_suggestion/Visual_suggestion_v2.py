import os
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import pandas as pd
import warnings
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import textwrap
from groq import Groq
import numpy as np
from collections import defaultdict

load_dotenv()

class VisualizationRecommender:
    DEFAULT_MODELS = {
        'groq': [
            ('llama3-70b-8192', 0.5),  # (model_name, weight)
            ('llama-3.3-70b-versatile', 0.3),
            ('llama3-8b-8192', 0.2)
        ],
        # Add other providers here
    }
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None, timeout: int = 30):
        """
        Initialize VisualizationRecommender with API keys and configuration.
        
        Args:
            api_keys: Optional dictionary of API keys. If not provided,
                     keys will be loaded from environment variables.
            timeout: Timeout in seconds for API requests
        """
        api_keys = api_keys or {}
        self.api_keys = {
            'groq': os.getenv('GROQ_API_KEY')
            # Add other services here
        }
        
        self.timeout = timeout
        self.clients = {}
        self.available_models = []
        self.df = None
        self.model_weights = {}
        
        self.api_keys.update(api_keys)
        
        self._validate_keys()
        self._initialize_clients()
        self._detect_available_models()
        self._initialize_model_weights()

    def _validate_keys(self):
        """Validate that required API keys are present"""
        for service in ['groq']:
            if not self.api_keys.get(service):
                self.api_keys[service] = input(f"Enter {service.upper()} API key: ").strip()
                if not self.api_keys[service]:
                    raise ValueError(f"{service.upper()} API key is required")

    def _initialize_clients(self):
        """Initialize API clients"""
        self.clients = {}
        if self.api_keys.get('groq'):
            try:
                self.clients['groq'] = Groq(api_key=self.api_keys['groq'])
            except ImportError:
                warnings.warn("Groq Python client not installed. pip install groq")
        
    def _detect_available_models(self):
        """Detect which models are available based on configured clients"""
        self.available_models = []
        for provider, client in self.clients.items():
            if client and provider in self.DEFAULT_MODELS:
                self.available_models.extend([m[0] for m in self.DEFAULT_MODELS[provider]])

    def _initialize_model_weights(self):
        """Initialize model weights based on availability"""
        total_weight = 0
        self.model_weights = {}
        
        # Only include weights for available models
        for provider in self.DEFAULT_MODELS:
            for model, weight in self.DEFAULT_MODELS[provider]:
                if model in self.available_models:
                    self.model_weights[model] = weight
                    total_weight += weight
        
        # Normalize weights to sum to 1
        if total_weight > 0:
            for model in self.model_weights:
                self.model_weights[model] /= total_weight

    def set_dataframe(self, df: pd.DataFrame):
        """Set the DataFrame to analyze"""
        self.df = df

    def recommend_visualizations(
        self,
        n: int = 3,
        custom_weights: Optional[Dict[str, float]] = None
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
        if self.df is None:
            raise ValueError("No DataFrame set. Call set_dataframe() first.")
        
        if not self.available_models:
            raise ValueError("No available models detected")
        
        # Use custom weights if provided, otherwise use defaults
        weights = custom_weights if custom_weights else self.model_weights
        
        # Get recommendations from all models in parallel
        all_recommendations = self._get_all_recommendations()
        
        # Apply weighted ensemble scoring
        ensemble_results = self._apply_ensemble_scoring(all_recommendations, weights)
        
        # Return top N recommendations
        return ensemble_results.head(n)

    def _get_all_recommendations(self) -> Dict[str, List[Dict]]:
        """Get recommendations from all available models in parallel"""
        df_description = self._describe_dataframe()
        prompt = self._create_prompt(df_description)
        
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self._get_model_recommendations, model, prompt): model
                for model in self.available_models
            }
            
            all_recommendations = {}
            for future in concurrent.futures.as_completed(futures):
                model = futures[future]
                try:
                    all_recommendations[model] = future.result()
                except Exception as e:
                    warnings.warn(f"Failed to get recommendations from {model}: {str(e)}")
        
        return all_recommendations

    def _get_model_recommendations(self, model: str, prompt: str) -> List[Dict]:
        """Get recommendations from a single model"""
        if model.startswith('llama'):
            response = self._query_llama(prompt, model)
        else:
            raise ValueError(f"Unsupported model: {model}")
        
        return self._parse_recommendations(response, model)

    def _apply_ensemble_scoring(
        self,
        all_recommendations: Dict[str, List[Dict]],
        weights: Dict[str, float]
    ) -> pd.DataFrame:
        """
        Apply weighted ensemble scoring to recommendations from all models.
        
        Args:
            all_recommendations: Dictionary of {model_name: recommendations}
            weights: Dictionary of {model_name: weight}
            
        Returns:
            pd.DataFrame: Recommendations with ensemble scores, sorted by score
        """
        # Create a mapping of recommendation keys to scores
        recommendation_scores = defaultdict(float)
        recommendation_details = {}
        
        for model, recs in all_recommendations.items():
            model_weight = weights.get(model, 0)
            if model_weight <= 0:
                continue
                
            for i, rec in enumerate(recs):
                # Create a unique key for each recommendation
                rec_key = (rec['plot_type'], rec['variables'])
                
                # Calculate position-based score (higher for earlier recommendations)
                position_score = 1 / (i + 1)
                
                # Add weighted score to ensemble
                recommendation_scores[rec_key] += model_weight * position_score
                
                # Store the best version of each recommendation
                if rec_key not in recommendation_details or position_score > recommendation_details[rec_key]['score']:
                    recommendation_details[rec_key] = {
                        'plot_type': rec['plot_type'],
                        'variables': rec['variables'],
                        'rationale': rec.get('rationale', ''),
                        'score': recommendation_scores[rec_key],
                       # 'contributing_models': recommendation_details.get(rec_key, {}).get('contributing_models', []) + [model]
                    }
        
        # Convert to DataFrame and sort by ensemble score
        results = pd.DataFrame(recommendation_details.values())
        results['ensemble_score'] = results['score'] / results['score'].max()  # Normalize to 0-1
        results = results.sort_values('ensemble_score', ascending=False)
        
        # Clean up columns
        results = results[['plot_type', 'variables', 'rationale', 'ensemble_score']]
        
        return results.reset_index(drop=True)

    def _describe_dataframe(self) -> str:
        """Generate a comprehensive description of the DataFrame"""
        num_cols = len(self.df.columns)
        sample_size = min(3, len(self.df))
        
        desc = [
            f"DataFrame Shape: {self.df.shape}",
            f"Columns ({num_cols}): {', '.join(self.df.columns)}",
            "\nColumn Details:",
        ]
        
        # Add column types and sample values
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            unique_count = self.df[col].nunique()
            sample_values = self.df[col].head(sample_size).tolist()
            
            desc.append(
                f"- {col}: {dtype} ({unique_count} unique values), sample: {sample_values}"
            )
        
        return "\n".join(desc)

    def _create_prompt(self, df_description: str) -> str:
        """Create the LLM prompt for visualization recommendations"""
        return textwrap.dedent(f"""
            You are a data visualization expert analyzing this dataset:

            {df_description}

            Recommend the most insightful and appropriate visualizations for exploring the dataset described below.

            For each recommendation, provide:
            - Plot Type: <specific chart type>
            - Variables: <comma-separated list of variables to visualize>
            - Rationale: <brief explanation of why this visualization is valuable>
            
            Focus on:
            1. Revealing meaningful patterns or relationships
            2. Appropriate chart types for the data types
            3. Avoiding misleading representations
            4. Practical actionable insights
            
            Provide exactly 5 recommendations, ordered by importance.
            Use this exact format for each recommendation:
            
            Plot Type: <type>
            Variables: <var1, var2, ...>
            Rationale: <explanation>
            ---
        """)

    def _query_llama(self, prompt: str, model: str) -> str:
        """Query a Llama model through Groq"""
        try:
            response = self.clients['groq'].chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            warnings.warn(f"Error calling Groq API with model {model}: {str(e)}")
            raise

    def _parse_recommendations(self, response: str, model: str) -> List[Dict]:
        """Parse the LLM response into structured recommendations"""
        recommendations = []
        
        for block in response.split('---'):
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            if not lines:
                continue
                
            try:
                rec = {'source_model': model}
                for line in lines:
                    if line.lower().startswith('plot type:'):
                        rec['plot_type'] = line.split(':', 1)[1].strip().lower()
                    elif line.lower().startswith('variables:'):
                        variables = [var.strip() for var in line.split(':', 1)[1].split(',')]
                        rec['variables'] = ', '.join([var for var in variables if var in self.df.columns])
                    elif line.lower().startswith('rationale:'):
                        rec['rationale'] = line.split(':', 1)[1].strip()
                
                if 'plot_type' in rec and 'variables' in rec and rec['variables']:
                    recommendations.append(rec)
            except Exception as e:
                warnings.warn(f"Failed to parse recommendation from {model}: {str(e)}")
                continue
        
        return recommendations

# Package-level convenience function
_recommender_instance = None

def recommend_visualizations(
    df: pd.DataFrame,
    n: int = 3,
    api_keys: dict = {},
    custom_weights: Optional[Dict[str, float]] = None
) -> pd.DataFrame:
    """
    Generate visualization recommendations using weighted ensemble of LLMs.
    
    Args:
        df: Input DataFrame to analyze
        n: Number of recommendations to return (default: 3)
        api_keys: Dictionary of API keys
        custom_weights: Optional dictionary to override default model weights
        
    Returns:
        pd.DataFrame: Recommended visualizations with ensemble scores
    """
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = VisualizationRecommender(api_keys)
    
    _recommender_instance.set_dataframe(df)
    return _recommender_instance.recommend_visualizations(
        n=n,
        custom_weights=custom_weights
    )