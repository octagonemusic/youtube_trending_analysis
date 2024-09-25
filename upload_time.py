import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta, timezone

# Load your dataset
df = pd.read_excel('output/trending_videos_usa.xlsx')

# Step 1: Preprocess the data
df['Published At'] = pd.to_datetime(df['Published At'])  # Ensure Published At is in datetime format
df['Hour'] = df['Published At'].dt.hour  # Extract hour
df['Day'] = df['Published At'].dt.day_name()  # Extract day of the week

# Step 2: Group by hour and day to calculate average views
hourly_views = df.groupby('Hour')['View Count'].mean().reset_index()
daily_views = df.groupby('Day')['View Count'].mean().reset_index()

# Step 3: Visualize hourly views using a heatmap
hourly_heatmap = df.pivot_table(index='Hour', columns='Day', values='View Count', aggfunc='mean')
plt.figure(figsize=(12, 6))
sns.heatmap(hourly_heatmap, cmap='YlGnBu', annot=True, fmt=".1f")
plt.title('Average Views by Hour and Day')
plt.xlabel('Day of the Week')
plt.ylabel('Hour of the Day')
plt.show()

# Step 4: Make Recommendations
optimal_hour = hourly_views.loc[hourly_views['View Count'].idxmax()]['Hour']
optimal_day = daily_views.loc[daily_views['View Count'].idxmax()]['Day']
print(f"Recommended upload time: {optimal_hour}:00 on {optimal_day}")

# Step 5: Analyze Upload Frequency
df['Upload Date'] = df['Published At'].dt.date  # Get just the date
upload_frequency = df.groupby('Upload Date').size().reset_index(name='Upload Count')

# Merge with view counts
frequency_view_data = pd.merge(upload_frequency, df.groupby('Upload Date')['View Count'].mean().reset_index(), on='Upload Date')

# Step 6: Visualize upload frequency vs average view count
fig, ax1 = plt.subplots(figsize=(10, 5))

# Plot average views
sns.lineplot(data=frequency_view_data, x='Upload Date', y='View Count', ax=ax1, label='Average Views', color='blue')
ax1.set_ylabel('Average Views', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Create a second y-axis for Upload Count
ax2 = ax1.twinx()
sns.lineplot(data=frequency_view_data, x='Upload Date', y='Upload Count', ax=ax2, label='Upload Count', color='orange')
ax2.set_ylabel('Upload Count', color='orange')
ax2.tick_params(axis='y', labelcolor='orange')

plt.title('Upload Frequency vs. Average View Count')
plt.xlabel('Date')
fig.tight_layout()  # To prevent clipping of ylabel
plt.show()
