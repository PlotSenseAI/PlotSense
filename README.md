# 🌟 PlotSense: AI-Powered Data Visualization Assistant

## 📌 Overview

**PlotSense** is an AI-powered assistant that helps data professionals and analysts make smarter, faster, and more explainable data visualizations. Whether you're exploring a new dataset or building dashboards, PlotSense simplifies the process with:

- ✅ Smart Visualization Suggestions - Recommends the best plots based on your data structure and relationships.
- 🧠 Natural Language Explanations – Automatically explains charts in plain English.
- 🔗 Seamless Integration – Works out of the box with pandas, matplotlib, and seaborn.

Let AI supercharge your EDA (Exploratory Data Analysis).

## ⚡ Quickstart

### 🔧 Install the package

```bash
pip install plotsense
```

### 🧠 Import PlotSense:

```bash
import plotsense as ps
from plotsense import recommender, generate_plot, explainer, 
```
### 🔐 Authenticate with Groq API:
Get your free API key from Groq Cloud https://console.groq.com/home

```bash
import os
# Set GROQ_API_KEY environment variable
os.environ['GROQ_API_KEY'] = 'your-api-key-here'

#or

# Set API key (one-time setup)
ps.set_api_key("your-api-key-here")
```

## 🚀 Core Features
### 🎯 1. AI-Recommended Visualizations
Let PlotSense analyze your data and suggest optimal charts.

```bash
import pandas as pd
# Load your dataset (e.g., pandas DataFrame)
df = pd.read_csv("data.csv")

