from typing import Dict, List, Tuple
import pandas as pd
from collections import defaultdict
from pprint import pprint
import textwrap

from plotsense.visual_suggestion.recommender.dataframe_analyzer import DataFrameAnalyzer


class EnsembleScorer:
    def __init__(
        self, df: pd.DataFrame, available_models: List[Tuple[str, str]],
        debug: bool = False
    ):
        self.df = df
        self.debug = debug
        self.available_models = available_models

    def apply_ensemble_scoring(
        self, all_recommendations: Dict[str, List[Dict]],
        weights: Dict[str, float]
    ) -> pd.DataFrame:
        output_columns = ['plot_type', 'variables', 'ensemble_score', 'model_agreement', 'source_models']
        
        if self.debug:
            print("\n[DEBUG] Applying ensemble scoring with weights:")
            pprint(weights)
        
        recommendation_weights = defaultdict(float)
        recommendation_details = {}

        for model, recs in all_recommendations.items():
            model_weight = weights.get(model, 0)
            if model_weight <= 0:
                continue

            for rec in recs:
                # Create a consistent key for the recommendation
                variables = rec['variables']
                if isinstance(variables, str):
                    variables = [v.strip() for v in variables.split(',')]
                
                # Filter variables to only those in the DataFrame
                valid_vars = [var for var in variables if var in self.df.columns]
                if not valid_vars:
                    if self.debug:
                        print(f"\n[DEBUG] Skipping recommendation from {model} with invalid variables: {variables}")
                    continue
                
                var_key = ', '.join(sorted(valid_vars))
                rec_key = (rec['plot_type'].lower(), var_key)
                
                model_score = rec.get('score', 1.0)
                total_weight = model_weight * model_score
                recommendation_weights[rec_key] += total_weight

                if rec_key not in recommendation_details:
                    recommendation_details[rec_key] = {
                        'plot_type': rec['plot_type'],
                        'variables': var_key,
                        'source_models': [model],
                        'raw_weight': total_weight
                    }
                else:
                    recommendation_details[rec_key]['source_models'].append(model)
                    recommendation_details[rec_key]['raw_weight'] += total_weight

        if not recommendation_details:
            if self.debug:
                print("\n[DEBUG] No valid recommendations after filtering")
            return pd.DataFrame(columns=output_columns)

        results = pd.DataFrame(list(recommendation_details.values()))

        if self.debug:
            print("\n[DEBUG] Recommendations before scoring:")
            print(results)

        if not results.empty:
            total_possible = sum(weights.values())
            results['ensemble_score'] = results['raw_weight'] / total_possible
            results['ensemble_score'] = results['ensemble_score'].round(2)
            results['model_agreement'] = results['source_models'].apply(len)
            results = results.sort_values(['ensemble_score', 'model_agreement'], ascending=[False, False]).reset_index(drop=True)
            return results[output_columns]

        return pd.DataFrame(columns=output_columns)

    def supplement_recommendations(self, existing: pd.DataFrame, target: int) -> pd.DataFrame:
        """Generate additional recommendations if we didn't get enough initially."""
        if len(existing) >= target:
            return existing.head(target)
        
        needed = target - len(existing)
        analyzer = DataFrameAnalyzer(self.df)
        df_description = analyzer.describe_dataframe()
        
        # Try to get more recommendations from the best-performing model
        best_model = existing.iloc[0]['source_models'][0] if not existing.empty else self.available_models[0]
        
        prompt = textwrap.dedent(f"""
            You already recommended these visualizations:
            {existing[['plot_type', 'variables']].to_string()}
            
            Please recommend {needed} ADDITIONAL different visualizations for:
            {df_description}
            
            Use the same format but ensure they're distinct from the above.
        """)
        
        try:
            response = self._query_llm(prompt, best_model)
            new_recs = self._parse_recommendations(response, f"{best_model}-supplement")
            
            # Combine with existing
            combined = pd.concat([existing, pd.DataFrame(new_recs)], ignore_index=True)
            combined = combined.drop_duplicates(subset=['plot_type', 'variables'])
            
            if self.debug:
                print(f"\n[DEBUG] Supplemented with {len(new_recs)} new recommendations")
            
            return combined.head(target)
        except Exception as e:
            if self.debug:
                print(f"\n[WARNING] Couldn't supplement recommendations: {str(e)}")
            return existing.head(target)  # Return what we have

