import pandas as pd
from generator import PlotGenerator

df = pd.DataFrame({
    "age": [23, 45, 31, 22, 36, 28],
    "fare": [7.25, 71.83, 8.05, 8.05, 53.10, 8.05],
    "pclass": [3, 1, 3, 3, 1, 3]
})

suggestions = pd.DataFrame([
    {"plot_type": "heatmap", "variables": ["age", "fare", "pclass"]},
    {"plot_type": "lineplot", "variables": ["age", "fare"]},
    {"plot_type": "correlation_analysis", "variables": ""} 
])

gen = PlotGenerator(df, suggestions)

# Heatmap
gen.generate_plot(0).show()

# Lineplot
gen.generate_plot(1).show()

# Correlation analysis
gen.generate_plot(2).show()

input("Press Enter to exit...")
