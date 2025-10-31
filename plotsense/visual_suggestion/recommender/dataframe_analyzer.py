from typing import List
import pandas as pd
import numpy as np


class DataFrameAnalyzer:
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    def describe_dataframe(self) -> str:
        num_cols = len(self.df.columns)
        sample_size = min(3, len(self.df))
        desc: List[str] = []

        # --- Basic Metadata ---
        desc.append(f"DataFrame Shape: {self.df.shape}")
        desc.append(f"Columns ({num_cols}): {', '.join(self.df.columns)}")
        desc.append("\nColumn Details:")

        # --- Column-Level Analysis ---
        for col in self.df.columns:
            # Determine semantic type (more granular than dtype)
            if pd.api.types.is_datetime64_dtype(self.df[col]):
                col_type = "datetime"
            elif pd.api.types.is_numeric_dtype(self.df[col]):
                col_type = "numerical"
            elif self.df[col].nunique() / len(self.df[col]) < 0.05:  # Low cardinality
                col_type = "categorical"
            else:
                col_type = "text/other"

            # Basic info
            unique_count = self.df[col].nunique()
            sample_values = self.df[col].dropna().head(sample_size).tolist()
            desc.append(
                f"- {col}: {col_type} ({unique_count} unique values), sample: {sample_values}"
            )

            # Add stats for numerical/datetime
            if col_type == "numerical":
                desc.append(
                    f"  Stats: min={self.df[col].min()}, max={self.df[col].max()}, "
                    f"mean={self.df[col].mean():.2f}, missing={self.df[col].isna().sum()}"
                )
            elif col_type == "datetime":
                desc.append(
                    f"  Range: {self.df[col].min()} to {self.df[col].max()}, "
                    f"missing={self.df[col].isna().sum()}"
                )

        # --- Relationship Analysis ---
        numerical_cols = self.df.select_dtypes(include=np.number).columns.tolist()
        if len(numerical_cols) > 1:
            desc.append("\nNumerical Variable Correlations (Pearson):")
            corr = self.df[numerical_cols].corr().round(2)
            desc.append(str(corr))

        # Categorical-numerical potential groupings
        categorical_cols = [
            col for col in self.df.columns 
            if self.df[col].nunique() / len(self.df[col]) < 0.05
        ]
        if categorical_cols and numerical_cols:
            desc.append("\nPotential Groupings (categorical vs numerical):")
            desc.append(f"  - Could group by: {categorical_cols}")
            desc.append(f"  - To analyze: {numerical_cols}")

        return "\n".join(desc)

