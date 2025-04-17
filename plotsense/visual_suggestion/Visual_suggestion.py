from abc import ABC, abstractmethod
from typing import List, Dict
import pandas as pd
import concurrent.futures
import textwrap
from groq import Groq


class BaseRecommender(ABC):
    def __init__(self, df: pd.DataFrame):
        self.df = df

    @abstractmethod
    def recommend_visualizations(self, n: int = 3) -> pd.DataFrame:
        """Abstract method to return visualization recommendations."""
        pass


class LLMVisualRecommender(BaseRecommender):
    def __init__(self, df: pd.DataFrame, api_keys: Dict[str, str]):
        super().__init__(df)
        self.api_keys = api_keys
        self.clients = {
            'groq': Groq(api_key=api_keys.get("groq"))
        }
        self.model_ids = {
            'llama3-70b': 'llama3-70b-8192',
            'llama3-8b': 'llama3-8b-8192',
            'llama3-versatile': 'llama-3.3-70b-versatile'
        }

    def recommend_visualizations(self, n: int = 3) -> pd.DataFrame:
        """Generate and return top-N visualization recommendations."""
        df_description = self._describe_dataframe()
        prompt = self._create_prompt(df_description)
        responses = self._query_all_models(prompt)

        parsed_recommendations = [
            rec for response in responses for rec in self._parse_llm_response(response)
        ]
        unique_recommendations = self._deduplicate(parsed_recommendations)

        return pd.DataFrame(unique_recommendations[:n])

    def _describe_dataframe(self) -> str:
        """Return a basic description of the DataFrame."""
        return (
            f"DataFrame Shape: {self.df.shape}\n"
            f"Columns: {', '.join(self.df.columns)}"
        )

    def _create_prompt(self, df_description: str) -> str:
        """Generate an LLM prompt based on DataFrame description."""
        return textwrap.dedent(f"""
            You are a data visualization expert analyzing this dataset:

            {df_description}

            Recommend 3 insightful visualizations for exploring this data.
            For each recommendation, provide:
            Plot Type: <type>
            Variables: <var1, var2, ...>
            Separate recommendations with '---'
        """)

    def _query_all_models(self, prompt: str) -> List[str]:
        """Query all configured models concurrently with the given prompt."""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._query_llm, model_id, prompt)
                for model_id in self.model_ids.values()
            ]
            return [future.result() for future in concurrent.futures.as_completed(futures)]

    def _query_llm(self, model_id: str, prompt: str) -> str:
        """Send a chat completion request to the specified model."""
        response = self.clients['groq'].chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content

    def _parse_llm_response(self, response: str) -> List[Dict[str, str]]:
        """Parse the LLM's response into structured recommendations."""
        recommendations = []

        for block in response.split('---'):
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            if not lines or not lines[0].lower().startswith("plot type"):
                continue

            try:
                plot_type = lines[0].split(":", 1)[1].strip().lower()
                variables = [
                    var.strip() for var in lines[1].split(":", 1)[1].split(',')
                ]
                valid_vars = [var for var in variables if var in self.df.columns]

                if valid_vars:
                    recommendations.append({
                        "Plot_Type": plot_type,
                        "Variables": ', '.join(valid_vars)
                    })
            except Exception:
                continue

        return recommendations

    def _deduplicate(self, items: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Remove duplicate visualization suggestions."""
        seen = set()
        unique = []

        for item in items:
            key = (item['Plot_Type'], item['Variables'])
            if key not in seen:
                seen.add(key)
                unique.append(item)

        return unique
