from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd
import concurrent.futures
import textwrap
import numpy as np
from groq import Groq  


class BaseRecommender(ABC):
    def __init__(self, df: pd.DataFrame):
        self.df = df

    @abstractmethod
    def recommend_visualizations(self, n: int = 3) -> pd.DataFrame:
        pass


class LLMVisualRecommender(BaseRecommender):
    def __init__(self, df: pd.DataFrame, api_keys: dict):
        super().__init__(df)
        self.api_keys = api_keys
        self._init_llm_clients()

    
        self.model_weights = {
            'llama3-70b': 0.5,
            'llama3-8b': 0.3,
            'llama3-versatile': 0.2
        }

    def _init_llm_clients(self):
        self.clients = {
            'groq': Groq(api_key=self.api_keys.get("groq"))
        }

    def recommend_visualizations(self, n: int = 3) -> pd.DataFrame:
        all_recs = self._get_llm_recommendations()
        ranked_recs = self._rank_recommendations(all_recs, n)
        return self._create_recommendation_df(ranked_recs)

    def _get_llm_recommendations(self) -> List[Dict]:
        df_description = self._describe_dataframe()
        prompt = self._create_prompt(df_description)

        recommendations = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for model_name in self.model_weights.keys():
                futures.append(executor.submit(
                    self._query_llm,
                    model_name=model_name,
                    prompt=prompt
                ))

            for future in concurrent.futures.as_completed(futures):
                try:
                    model_recs = future.result()
                    recommendations.extend(model_recs)
                except Exception as e:
                    print(f"Error getting recommendations: {e}")

        return recommendations

    def _describe_dataframe(self) -> str:
        desc = [
            f"DataFrame Shape: {self.df.shape}",
            f"Columns: {', '.join(self.df.columns)}"
        ]

        num_cols = self.df.select_dtypes(include=np.number).columns.tolist()
        if num_cols:
            desc.append("\nNumeric Columns:")
            for col in num_cols:
                stats = self.df[col].describe()
                desc.append(
                    f"  {col}: min={stats['min']:.2f}, max={stats['max']:.2f}, "
                    f"mean={stats['mean']:.2f}, std={stats['std']:.2f}"
                )

        cat_cols = self.df.select_dtypes(exclude=np.number).columns.tolist()
        if cat_cols:
            desc.append("\nCategorical Columns:")
            for col in cat_cols:
                unique_vals = self.df[col].nunique()
                sample = ', '.join(map(str, self.df[col].dropna().unique()[:3]))
                desc.append(f"  {col}: {unique_vals} unique values (e.g., {sample})")

        return '\n'.join(desc)

    def _create_prompt(self, df_description: str) -> str:
        return textwrap.dedent(f"""
        You are a data visualization expert analyzing this dataset:

        {df_description}

        Recommend 3-5 insightful visualizations for exploring this data.
        For each recommendation, provide:
        1. Plot type (choose appropriate visualization types)
        2. Variables to visualize (1-3 relevant variables)
        3. Brief reasoning why this visualization would be insightful
        4. Confidence score (0-1)

        Format each recommendation as:
        Plot Type: <type>
        Variables: <var1, var2, ...>
        Reasoning: <text>
        Confidence: <score>

        Separate recommendations with '---'
        """)

    def _query_llm(self, model_name: str, prompt: str) -> List[Dict]:
        model_ids = {
            'llama3-70b': 'llama3-70b-8192',
            'llama3-8b': 'llama3-8b-8192',
            'llama3-versatile': 'llama-3.3-70b-versatile'
        }

        model_id = model_ids.get(model_name)
        if not model_id:
            raise ValueError(f"Unknown model: {model_name}")

        response = self.clients['groq'].chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        content = response.choices[0].message.content
        return self._parse_llm_response(content, model_name)

    def _parse_llm_response(self, response: str, model_name: str) -> List[Dict]:
        recommendations = []

        for rec in response.split('---'):
            lines = [line.strip() for line in rec.split('\n') if line.strip()]
            if len(lines) < 4:
                continue

            try:
                plot_type = lines[0].replace('Plot Type:', '').strip().lower()
                variables = [v.strip() for v in lines[1].replace('Variables:', '').split(',')]
                reasoning = lines[2].replace('Reasoning:', '').strip()
                confidence = float(lines[3].replace('Confidence:', '').strip())

                valid_vars = [v for v in variables if v in self.df.columns]
                if not valid_vars:
                    continue

                recommendations.append({
                    'plot_type': plot_type,
                    'variables': valid_vars,
                    'reasoning': reasoning,
                    'confidence': confidence * self.model_weights[model_name],
                    'source_model': model_name
                })
            except Exception:
                continue

        return recommendations

    def _rank_recommendations(self, all_recs: List[Dict], n: int) -> List[Dict]:
        grouped = {}
        for rec in all_recs:
            key = (rec['plot_type'], tuple(sorted(rec['variables'])))
            if key not in grouped:
                grouped[key] = {
                    'confidence_sum': 0,
                    'count': 0,
                    'reasonings': [],
                    'sources': set()
                }
            grouped[key]['confidence_sum'] += rec['confidence']
            grouped[key]['count'] += 1
            grouped[key]['reasonings'].append(rec['reasoning'])
            grouped[key]['sources'].add(rec['source_model'])

        ranked = []
        for (plot_type, variables), data in grouped.items():
            ranked.append({
                'plot_type': plot_type,
                'variables': list(variables),
                'confidence': data['confidence_sum'] / data['count'],
                'reasoning': ' | '.join(data['reasonings'][:2]),
                'source_models': ', '.join(data['sources'])
            })

        return sorted(ranked, key=lambda x: -x['confidence'])[:n]

    def _create_recommendation_df(self, ranked_recs: List[Dict]) -> pd.DataFrame:
        """Create DataFrame of recommendations (no plot code)"""
        records = []
        for i, rec in enumerate(ranked_recs, 1):
            records.append({
                'Rank': i,
                'Plot_Type': rec['plot_type'],
                'Variables': ', '.join(rec['variables']),
                'Reasoning': rec['reasoning'],
                'Confidence': f"{rec['confidence']:.0%}",
                'Source_Models': rec['source_models']
            })

        return pd.DataFrame(records)
