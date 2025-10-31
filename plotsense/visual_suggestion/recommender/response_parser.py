from typing import Dict, List
import pandas as pd
import warnings


class ResponseParser:
    def __init__(self, df: pd.DataFrame, debug: bool = False):
        self.df = df
        self.debug = debug

    def parse_recommendations(self, response: str, model: str) -> List[Dict]:
        """Parse the LLM response into structured recommendations"""
        recommendations = []

        # Split response into recommendation blocks
        blocks = [b.strip() for b in response.split('---') if b.strip()]
        
        if self.debug:
            print(f"\n[DEBUG] Parsing {len(blocks)} blocks from {model}")
        
        for block in blocks:
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            if not lines:
                continue
                
            try:
                rec = {'source_model': model}
                for line in lines:
                    if line.lower().startswith('plot type:'):
                        rec['plot_type'] = line.split(':', 1)[1].strip().lower()
                    elif line.lower().startswith('variables:'):
                        raw_vars = line.split(':', 1)[1].strip()
                        # Filter variables to only those that exist in DataFrame
                        variables = [
                            v.strip() for v in raw_vars.split(',') if v.strip() in self.df.columns
                        ]
                        rec['variables'] = ', '.join([
                            var for var in variables if var in self.df.columns
                        ])
                        #rec['variables'] = self._reorder_variables(', '.join(variables))  # Keep original order for now
                
                if 'plot_type' in rec and 'variables' in rec and rec['variables']:
                    recommendations.append(rec)
            except Exception as e:
                warnings.warn(f"Failed to parse recommendation from {model}: {str(e)}")
                continue
        
        return recommendations

    def validate_variable_order(self, recommendations: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and correct the order of variables in recommendations, 
        ensuring numerical variables come first.
        
        Args:
            recommendations: DataFrame of visualization recommendations
        
        Returns:
            DataFrame with corrected variable order
        """
        def _reorder_variables(row):
            # Split variables
            variables = [var.strip() for var in row['variables'].split(',')]
            
            # Identify numerical and non-numerical variables
            numerical_vars = [
                var for var in variables 
                if pd.api.types.is_numeric_dtype(self.df[var])
            ]

            date_vars = [
                var for var in variables 
                if pd.api.types.is_datetime64_any_dtype(self.df[var])
            ]

            non_numerical_vars = [
                var for var in variables 
                if var not in numerical_vars and var not in date_vars
            ]
            
            # Combine with numerical variables first
            corrected_vars = date_vars + numerical_vars + non_numerical_vars
            
            # Update the row with corrected variable order
            row['variables'] = ', '.join(corrected_vars)
            return row
        
        # Apply reordering
        corrected_recommendations = recommendations.apply(_reorder_variables, axis=1)
        
        if self.debug:
            print("\n[DEBUG] Variable Order Validation:")
            for orig, corrected in zip(recommendations['variables'], corrected_recommendations['variables']):
                if orig != corrected:
                    print(f"  Corrected: {orig} → {corrected}")
        
        return corrected_recommendations

