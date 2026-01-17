#!/usr/bin/env python3
"""
Generate sample plots that represent PlotSense capabilities
Creates the 8 plot types that PlotSense supports with realistic data
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# Set style for professional looking plots
plt.style.use('default')
sns.set_palette("husl")

# Create sample datasets
np.random.seed(42)

def create_sample_data():
    """Create realistic sample datasets"""

    # Sales data
    sales_data = pd.DataFrame({
        'Product': ['Laptops', 'Phones', 'Tablets', 'Headphones', 'Monitors'],
        'Q1_Sales': [120, 230, 95, 180, 75],
        'Q2_Sales': [140, 210, 110, 165, 85],
        'Revenue': [45000, 67000, 28000, 18000, 22000]
    })

    # Customer satisfaction data
    satisfaction_data = pd.DataFrame({
        'Score': np.random.normal(7.5, 1.2, 500),
        'Department': np.random.choice(['Sales', 'Support', 'Product', 'Marketing'], 500),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], 500),
        'Response_Time': np.random.exponential(2.5, 500)
    })

    # Performance metrics
    performance_data = pd.DataFrame({
        'CPU_Usage': np.random.beta(2, 5, 1000) * 100,
        'Memory_Usage': np.random.gamma(2, 15, 1000),
        'Response_Time': np.random.lognormal(1, 0.5, 1000),
        'Server': np.random.choice(['Server-A', 'Server-B', 'Server-C'], 1000)
    })

    return sales_data, satisfaction_data, performance_data

def save_plot(filename, dpi=150, bbox_inches='tight'):
    """Save plot with consistent settings"""
    plt.savefig(f'public/plots/{filename}', dpi=dpi, bbox_inches=bbox_inches,
                facecolor='white', edgecolor='none')
    plt.close()

def generate_plots():
    """Generate all 8 plot types that PlotSense supports"""

    sales_data, satisfaction_data, performance_data = create_sample_data()

    # 1. Scatter Plot - CPU vs Memory Usage
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(performance_data['CPU_Usage'], performance_data['Memory_Usage'],
                         c=performance_data['Response_Time'], cmap='viridis', alpha=0.7, s=60)
    plt.colorbar(scatter, label='Response Time (ms)')
    plt.xlabel('CPU Usage (%)')
    plt.ylabel('Memory Usage (GB)')
    plt.title('System Performance: CPU vs Memory Usage', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    save_plot('scatter_performance.png')

    # 2. Bar Chart - Product Sales Comparison
    plt.figure(figsize=(10, 6))
    x = np.arange(len(sales_data['Product']))
    width = 0.35
    plt.bar(x - width/2, sales_data['Q1_Sales'], width, label='Q1 2024', color='#3498db')
    plt.bar(x + width/2, sales_data['Q2_Sales'], width, label='Q2 2024', color='#e74c3c')
    plt.xlabel('Products')
    plt.ylabel('Units Sold')
    plt.title('Quarterly Sales Performance by Product', fontsize=14, fontweight='bold')
    plt.xticks(x, sales_data['Product'], rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    save_plot('bar_sales.png')

    # 3. Horizontal Bar Chart - Revenue by Product
    plt.figure(figsize=(10, 6))
    plt.barh(sales_data['Product'], sales_data['Revenue'], color='#2ecc71')
    plt.xlabel('Revenue ($)')
    plt.ylabel('Products')
    plt.title('Product Revenue Distribution', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='x')
    # Add value labels
    for i, v in enumerate(sales_data['Revenue']):
        plt.text(v + 1000, i, f'${v:,}', va='center')
    save_plot('barh_revenue.png')

    # 4. Histogram - Customer Satisfaction Scores
    plt.figure(figsize=(10, 6))
    plt.hist(satisfaction_data['Score'], bins=25, color='#9b59b6', alpha=0.7, edgecolor='black')
    plt.xlabel('Satisfaction Score (1-10)')
    plt.ylabel('Number of Customers')
    plt.title('Customer Satisfaction Score Distribution', fontsize=14, fontweight='bold')
    plt.axvline(satisfaction_data['Score'].mean(), color='red', linestyle='--',
                label=f'Mean: {satisfaction_data["Score"].mean():.1f}')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    save_plot('histogram_satisfaction.png')

    # 5. Box Plot - Response Time by Department
    plt.figure(figsize=(10, 6))
    box_data = [satisfaction_data[satisfaction_data['Department'] == dept]['Response_Time']
                for dept in satisfaction_data['Department'].unique()]
    plt.boxplot(box_data, labels=satisfaction_data['Department'].unique(), patch_artist=True,
                boxprops=dict(facecolor='#f39c12', alpha=0.7))
    plt.ylabel('Response Time (hours)')
    plt.xlabel('Department')
    plt.title('Response Time Distribution by Department', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='y')
    save_plot('boxplot_response_time.png')

    # 6. Violin Plot - Performance Metrics by Server
    plt.figure(figsize=(10, 6))
    server_data = []
    server_labels = []
    for server in performance_data['Server'].unique():
        server_data.append(performance_data[performance_data['Server'] == server]['CPU_Usage'])
        server_labels.append(server)

    parts = plt.violinplot(server_data, positions=range(len(server_labels)),
                          showmeans=True, showmedians=True)
    for pc in parts['bodies']:
        pc.set_facecolor('#1abc9c')
        pc.set_alpha(0.7)
    plt.xticks(range(len(server_labels)), server_labels)
    plt.ylabel('CPU Usage (%)')
    plt.xlabel('Server')
    plt.title('CPU Usage Distribution by Server', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='y')
    save_plot('violin_cpu_usage.png')

    # 7. Pie Chart - Market Share by Region
    plt.figure(figsize=(8, 8))
    region_counts = satisfaction_data['Region'].value_counts()
    colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24']
    wedges, texts, autotexts = plt.pie(region_counts.values, labels=region_counts.index,
                                      autopct='%1.1f%%', colors=colors, startangle=90)
    plt.title('Customer Distribution by Region', fontsize=14, fontweight='bold')
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    save_plot('pie_region_distribution.png')

    # 8. Hexbin Plot - CPU vs Response Time Density
    plt.figure(figsize=(10, 6))
    plt.hexbin(performance_data['CPU_Usage'], performance_data['Response_Time'],
               gridsize=25, cmap='YlOrRd', mincnt=1)
    plt.colorbar(label='Count')
    plt.xlabel('CPU Usage (%)')
    plt.ylabel('Response Time (ms)')
    plt.title('CPU Usage vs Response Time Density', fontsize=14, fontweight='bold')
    save_plot('hexbin_cpu_response.png')

    print("✅ Generated 8 sample plots successfully!")
    print("📁 Plots saved in: public/plots/")
    plot_files = [
        'scatter_performance.png', 'bar_sales.png', 'barh_revenue.png',
        'histogram_satisfaction.png', 'boxplot_response_time.png',
        'violin_cpu_usage.png', 'pie_region_distribution.png', 'hexbin_cpu_response.png'
    ]
    for plot in plot_files:
        print(f"   • {plot}")

if __name__ == "__main__":
    generate_plots()
