import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV file
df = pd.read_csv('your_file.csv')

# Strip whitespace from column names
df.columns = df.columns.str.strip()

# Use the correct column names
name_column = df.columns[0]
entity_column = df.columns[1]
finding_column = df.columns[2]

# Create hierarchical data structure
hierarchy = df.groupby([name_column, entity_column, finding_column]).size().unstack(finding_column, fill_value=0)

# Set up colors using discrete color maps
name_cmap = plt.colormaps['Set1']
entity_cmap = plt.colormaps['Set2']
finding_cmap = plt.colormaps['Set3']

name_colors = [name_cmap(i) for i in range(len(hierarchy.index.get_level_values(name_column).unique()))]
entity_colors = [entity_cmap(i) for i in range(len(hierarchy.index.get_level_values(entity_column).unique()))]
finding_colors = [finding_cmap(i) for i in range(len(hierarchy.columns))]

# Create the figure and axis
fig, ax = plt.subplots(figsize=(12, 8))

# Create the inner circle (Name)
name_sizes = hierarchy.groupby(level=0).sum().sum(axis=1)
inner_wedges, _ = ax.pie(name_sizes, radius=0.5, colors=name_colors, wedgeprops=dict(width=0.3, edgecolor='w'))

# Create the middle circle (Entity)
entity_sizes = hierarchy.groupby(level=1).sum().values.flatten()
entity_colors_repeated = [entity_colors[i % len(entity_colors)] for i in range(len(entity_sizes))]
middle_wedges, _ = ax.pie(entity_sizes, radius=0.8, colors=entity_colors_repeated, wedgeprops=dict(width=0.3, edgecolor='w'))

# Create the outer circle (Finding)
finding_sizes = hierarchy.values.flatten()
finding_colors_repeated = [finding_colors[i % len(finding_colors)] for i in range(len(finding_sizes))]
outer_wedges, _ = ax.pie(finding_sizes, radius=1.1, colors=finding_colors_repeated, wedgeprops=dict(width=0.3, edgecolor='w'))

# Add labels for the outer circle
for i, wedge in enumerate(outer_wedges):
    ang = (wedge.theta2 + wedge.theta1) / 2
    x = np.cos(np.deg2rad(ang))
    y = np.sin(np.deg2rad(ang))
    ha = 'left' if x >= 0 else 'right'
    va = 'bottom' if y >= 0 else 'top'
    
    label = hierarchy.columns[i % len(hierarchy.columns)]
    ax.text(x*1.2, y*1.2, label, ha=ha, va=va, rotation=ang if ha == 'left' else ang+180)

# Add legend
legend_elements = (
    [plt.Rectangle((0,0),1,1, fc=c) for c in name_colors] +
    [plt.Rectangle((0,0),1,1, fc=c) for c in entity_colors] +
    [plt.Rectangle((0,0),1,1, fc=c) for c in finding_colors]
)
legend_labels = (
    list(hierarchy.index.get_level_values(name_column).unique()) + 
    list(hierarchy.index.get_level_values(entity_column).unique()) + 
    list(hierarchy.columns)
)
ax.legend(legend_elements, legend_labels, loc='center left', bbox_to_anchor=(1, 0.5), ncol=1)

# plt.title('Multilevel Pie Chart')
plt.axis('equal')
plt.tight_layout()
plt.show()
