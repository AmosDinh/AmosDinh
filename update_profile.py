import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- 1. DATA GATHERING ---

stats_repo_path = 'repo-stats-data'
all_repo_data = []

print(f"Searching for stats in: {os.path.abspath(stats_repo_path)}")

# Walk through the stats directory to find all aggregate CSV files
for root, dirs, files in os.walk(stats_repo_path):
    if 'views_clones_aggregate.csv' in files:
        relative_path = os.path.relpath(root, stats_repo_path)
        repo_name = relative_path.split(os.sep)[0]

        if repo_name.startswith('.'):
            continue
        
        file_path = os.path.join(root, 'views_clones_aggregate.csv')
        print(f"Found data file: {file_path} -> Assigning to repo: '{repo_name}'")

        try:
            df = pd.read_csv(file_path)
            df['repo'] = repo_name
            all_repo_data.append(df)
        except Exception as e:
            print(f"Could not read {file_path}: {e}")

if not all_repo_data:
    print("No data was found. Exiting.")
    exit()

full_df = pd.concat(all_repo_data, ignore_index=True)
full_df['time_iso8601'] = pd.to_datetime(full_df['time_iso8601'])

# --- 2. DATA AGGREGATION ---

total_clones = full_df['clones_total'].sum()
top_5_repos = full_df.groupby('repo')['clones_total'].sum().nlargest(5).reset_index()
clones_over_time = full_df.groupby(pd.Grouper(key='time_iso8601', freq='D'))['clones_total'].sum().reset_index()
clones_over_time = clones_over_time.sort_values('time_iso8601')


# --- 3. PLOT GENERATION ---

plt.style.use('dark_background')
# --- CHANGE HERE: Changed figsize from (10, 5) to (10, 3) for a shorter graph ---
fig, ax = plt.subplots(figsize=(10, 3))

ax.plot(clones_over_time['time_iso8601'], clones_over_time['clones_total'], color='#4F9FEF', linewidth=2)
ax.fill_between(clones_over_time['time_iso8601'], clones_over_time['clones_total'], color='#4F9FEF', alpha=0.3)

ax.set_title('Total Repository Clones Over Time', fontsize=16, color='white')
ax.set_xlabel('Date', fontsize=12, color='white')
ax.set_ylabel('Number of Clones', fontsize=12, color='white')
ax.grid(axis='y', linestyle='--', alpha=0.3)
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
plt.setp(ax.spines.values(), color='white')

plt.savefig('clones_history.png', bbox_inches='tight', transparent=True)
print("Graph 'clones_history.png' created with smaller height.")


# --- 4. README.md GENERATION ---

readme_content = f"""# Hello, I'm Amos.

Welcome to my GitHub profile. Here's a summary of my repository statistics, updated automatically.

---

### Repository Stats

My repositories have been cloned **{int(total_clones)}** times in total (Since June 2025).

![Clone History](clones_history.png)

### Top 5 Cloned Repositories

| Rank | Repository | Total Clones |
|------|------------|--------------|
"""

for index, row in top_5_repos.iterrows():
    readme_content += f"| {index + 1} | [{row['repo']}](https://github.com/AmosDinh/{row['repo']}) | {int(row['clones_total'])} |\n"

last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
readme_content += f"\n---\n\n*Last updated: {last_updated}*"

with open('README.md', 'w') as f:
    f.write(readme_content)

print("README.md has been updated.")
