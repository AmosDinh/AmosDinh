import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- 1. DATA GATHERING ---

# Path to the checked-out stats data
stats_repo_path = 'repo-stats-data'
all_repo_data = []

# Walk through the stats directory to find all aggregate CSV files
for root, dirs, files in os.walk(stats_repo_path):
    if 'views_clones_aggregate.csv' in files:
        # Extract repo name from the path. e.g., 'repo-stats-data/BikePricePredict/ghrs-data'
        parts = root.split(os.sep)
        if len(parts) > 1 and parts[1] != '.git': # Basic check to avoid .git folder etc.
            repo_name = parts[1]
            file_path = os.path.join(root, 'views_clones_aggregate.csv')
            try:
                df = pd.read_csv(file_path)
                # Add repo name for tracking
                df['repo'] = repo_name
                all_repo_data.append(df)
            except Exception as e:
                print(f"Could not read {file_path}: {e}")

# Combine all data into a single DataFrame
if not all_repo_data:
    print("No data found. Exiting.")
    exit()

full_df = pd.concat(all_repo_data, ignore_index=True)
full_df['time_iso8601'] = pd.to_datetime(full_df['time_iso8601'])

# --- 2. DATA AGGREGATION ---

# Total clones across all repositories
total_clones = full_df['clones_total'].sum()

# Top 5 repositories by total clones
top_5_repos = full_df.groupby('repo')['clones_total'].sum().nlargest(5).reset_index()

# Time series data for plotting
clones_over_time = full_df.groupby(pd.Grouper(key='time_iso8601', freq='D'))['clones_total'].sum().reset_index()
clones_over_time = clones_over_time.sort_values('time_iso8601')


# --- 3. PLOT GENERATION ---

plt.style.use('dark_background') # Use a GitHub-friendly style
fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(clones_over_time['time_iso8601'], clones_over_time['clones_total'], color='#4F9FEF', linewidth=2)
ax.fill_between(clones_over_time['time_iso8601'], clones_over_time['clones_total'], color='#4F9FEF', alpha=0.3)

# Formatting the plot
ax.set_title('Total Repository Clones Over Time', fontsize=16, color='white')
ax.set_xlabel('Date', fontsize=12, color='white')
ax.set_ylabel('Number of Clones', fontsize=12, color='white')
ax.grid(axis='y', linestyle='--', alpha=0.3)
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
plt.setp(ax.spines.values(), color='white')

# Save the plot to a file
plt.savefig('clones_history.png', bbox_inches='tight', transparent=True)
print("Graph 'clones_history.png' created.")


# --- 4. README.md GENERATION ---

readme_content = f"""
# Hi, I'm Amos

Welcome to my GitHub profile. Here's a summary of my repository statistics, updated automatically.

---

### Repository Stats

My repositories have been cloned **{int(total_clones)}** times in total.

![Clone History](clones_history.png)

### Top 5 Cloned Repositories

| Rank | Repository | Total Clones |
|------|------------|--------------|
"""

# Add top 5 repos to the table
for index, row in top_5_repos.iterrows():
    readme_content += f"| {index + 1} | [{row['repo']}](https://github.com/AmosDinh/{row['repo']}) | {int(row['clones_total'])} |\n"

# Add a timestamp
last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
readme_content += f"\n---\n\n*Last updated: {last_updated}*"

# Write the new content to README.md
with open('README.md', 'w') as f:
    f.write(readme_content)

print("README.md has been updated.")
