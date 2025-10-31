from plotsense.visual_suggestion.suggestions import recommender
import pandas as pd

# Example: create a simple DataFrame
df = pd.DataFrame({
    "Year": [2020, 2021, 2022, 2023],
    "Sales": [150, 200, 250, 300],
    "Profit": [40, 50, 65, 80]
})

# Replace with your actual API keys
api_keys = {
    "groq": "gsk_xyz",
    "openai": "sk-proj-xyz-abc",
    "azure": "ghp_xyz",
}

# Run the recommender
recommendations = recommender(
    df,
    n=3,  # number of visualizations to recommend
    api_keys=api_keys,
    selected_models=[("azure", "openai/gpt-5")],
)

# Display the recommendations
print("📊 Recommended visualizations:")
print(recommendations)

