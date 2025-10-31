from plotsense.explanations.explanations import explainer
from matplotlib import pyplot as plt

# Example: generate a simple plot
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])

# Replace with your actual API keys
api_keys = {
    "groq": "gsk_xyz",
    "openai": "sk-proj-xyz-abc"
}

# Run explainer
result = explainer(
    fig,
    prompt="Explain this simple line plot",
    api_keys=api_keys,
    selected_models=[("openai", "gpt-4.1")],
)
print(result)

