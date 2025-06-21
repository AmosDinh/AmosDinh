import os
import sys
import pandas as pd
from datetime import datetime

# --- 1. DATA GATHERING ---

base_search_path = os.path.join('repo-stats-data', 'AmosDinh')
all_repo_data = []

print(f"Searching for repository data inside: {base_search_path}")

if not os.path.isdir(base_search_path):
    print(f"Error: The directory '{base_search_path}' does not exist. Please check the checkout path and repo structure.")
    sys.exit(1)

for repo_name in os.listdir(base_search_path):
    repo_path = os.path.join(base_search_path, repo_name)
    if os.path.isdir(repo_path):
        csv_path = os.path.join(repo_path, 'ghrs-data', 'views_clones_aggregate.csv')
        if os.path.exists(csv_path):
            print(f"Processing: {csv_path}")
            try:
                df = pd.read_csv(csv_path)
                df['repo'] = repo_name
                all_repo_data.append(df)
            except Exception as e:
                print(f"Could not read or process {csv_path}: {e}")
        else:
            print(f"Warning: No aggregate CSV found for repo '{repo_name}'")

if not all_repo_data:
    print("No data was found. README will not be updated.")
    sys.exit()

# --- 2. DATA AGGREGATION ---

full_df = pd.concat(all_repo_data, ignore_index=True)
full_df['time_iso8601'] = pd.to_datetime(full_df['time_iso8601'])

min_date = full_df['time_iso8601'].min()
start_date_str = min_date.strftime("%B %Y")

total_unique_clones = full_df['clones_unique'].sum()

# Get top 10 repos
top_10_repos = full_df.groupby('repo')['clones_unique'].sum().nlargest(10).reset_index()


# --- 3. README.md GENERATION ---

readme_content = f"""# Hello there, I am Amos.

Welcome to my GitHub profile. Here's a summary of my repository statistics, updated automatically.

---

### Repository Stats

My repositories have been cloned a total of **{int(total_unique_clones)}** unique times (since {start_date_str}).

### Top 10 Cloned Repositories

| Repository | Unique Clones |
|------------|---------------|
"""

# Loop to generate table rows without the Rank column
for index, row in top_10_repos.iterrows():
    readme_content += f"| [{row['repo']}](https://github.com/AmosDinh/{row['repo']}) | {int(row['clones_unique'])} |\n"

last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
readme_content += f"\n---\n\n*Last updated: {last_updated}*"

with open('README.md', 'w') as f:
    f.write(readme_content)

print("README.md has been updated successfully.")
