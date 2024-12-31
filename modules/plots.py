import analyzer
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

sector = 'technology'
averages = pd.read_csv('../data/averages.csv')

ratio_index_map = {
    'current_ratio': 0,
    'quick_ratio': 1,
    'gross_profit': 2,
    'net_profit': 3,
    'roa': 4,
    'roe': 5,
    'asset_turnover': 6,
    'debt_to_equity': 7,
    'interest_cover': 8
}

datapoints = pd.read_csv('../data/datapoints.csv')
analysis = analyzer.FinancialAnalyzer('MSFT')
company_data = pd.DataFrame()
company_data = analysis.load_data(
    datapoints['balance_sheet'].tolist(),
    datapoints['income_statement'].dropna().tolist(),
    datapoints['cash_flow'].dropna().tolist()
)

ratios = analysis.analyze()
columns_to_plot = ['year', 'current_ratio', 'quick_ratio', 'debt_to_equity']
plot_df = ratios[columns_to_plot]

# Step 3: Create subplots

# Subplot configuration
ratios_to_plot = [
    ('current_ratio', 'Current Ratio', 'skyblue', 'Sector Avg - Current Ratio', 'blue'),
    ('quick_ratio', 'Quick Ratio', 'lightgreen', 'Sector Avg - Quick Ratio', 'green'),
    ('debt_to_equity', 'Debt to Equity', 'salmon', 'Sector Avg - Debt to Equity', 'red')
]

x = np.arange(len(plot_df.index))  # Positions for bars
width = 0.25  # Narrower bars to look more compact

# Step 3: Create the subplots with a vertical orientation
fig, axs = plt.subplots(3, 1, figsize=(6, 12))  # More vertical layout with increased height and reduced width

for i, (column, title, color, avg_label, avg_color) in enumerate(ratios_to_plot):
    ax = axs[i]  # Select subplot
    
    # Plot bars for each ratio
    ax.bar(x, plot_df[column], width, label=f'{title} (MSFT)', color=color)
    
    # Add horizontal line for the sector average
    avg_value = averages[sector].iloc[ratio_index_map[column]]
    for xpos in x:
        ax.hlines(
            y=avg_value,
            xmin=xpos - width / 2,  # Align horizontal line with narrower bars
            xmax=xpos + width / 2,
            color=avg_color,
            linestyle='--',
            label=avg_label if xpos == 0 else None
        )
    
    # Set labels and titles for each subplot
    ax.set_xlabel('Year')
    ax.set_ylabel('Value')
    ax.set_title(f'{title} vs Technology Sector Average')
    
    # Set the x-axis tick labels as integers (removing the decimal point)
    ax.set_xticks(x)
    ax.set_xticklabels(plot_df['year'].map(int))  # Use map(int) to remove the .0
    
    ax.legend(loc='upper right')

# Fine-tune the layout for a more compact, vertical appearance
plt.tight_layout()  # Automatically adjusts spacing between plots
plt.subplots_adjust(hspace=0.5)  # Optional: fine-tune the vertical space between subplots

# Save or show the plot
plt.savefig('msft_vertical_ratios.png', dpi=300)

growth_rates = analysis.growth_rates()
years = ['2022', '2023', '2024']
ratios_to_plot = growth_rates['ratio'].values  # Ratio names
ratios_growth = growth_rates.drop('ratio', axis=1).values  # Growth rate values for each ratio

# Plot all the growth rates on the same chart
plt.figure(figsize=(10, 6))

# Use matplotlib.colormaps to get a distinct colormap
colormap = plt.colormaps['tab10']  # Access the 'tab10' colormap
colors = [colormap(i / len(ratios_to_plot)) for i in range(len(ratios_to_plot))]  # Generate distinct colors

# Plot each ratio with a unique color
for i, (ratio, growth) in enumerate(zip(ratios_to_plot, ratios_growth)):
    plt.plot(years, growth, label=ratio, marker='o', color=colors[i])

# Set labels and title
plt.xlabel('Year')
plt.ylabel('Growth Rate (%)')
plt.title('Growth Rates of Financial Ratios Over Time')

# Add a legend to identify each ratio
plt.legend(loc='best')

# Add grid for better readability
plt.grid(True)

# Save the plot as a PNG (optional)
plt.savefig('ratios_growth_rate_all.png', dpi=300)