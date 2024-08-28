import os
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv
import isodate
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import gaussian_kde
import numpy as np

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv('YOUTUBE_API_KEY')

# Set up YouTube Data API
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Function to get trending videos
def get_trending_videos(region_code='IN', max_results=50):
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics,topicDetails",
        chart="mostPopular",
        regionCode=region_code,
        maxResults=max_results
    )
    response = request.execute()
    return response['items']

# Function to get channel details
def get_channel_details(channel_id):
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics,topicDetails",
        id=channel_id
    )
    response = request.execute()
    return response['items'][0] if response['items'] else None

# Fetch trending videos
videos = get_trending_videos()

# Prepare data
video_data = []

for video in videos:
    video_id = video['id']
    snippet = video['snippet']
    statistics = video['statistics']
    content_details = video['contentDetails']
    
    # Fetch channel details
    channel_id = snippet['channelId']
    channel_details = get_channel_details(channel_id)
    
    # Use "Unknown" if country is not available
    channel_country = channel_details['snippet'].get('country', 'Unknown') if channel_details else 'Unknown'
    
    # Convert duration from ISO 8601 format to seconds
    duration = isodate.parse_duration(content_details.get('duration')).total_seconds()
    
    video_data.append({
        "Video ID": video_id,
        "Title": snippet['title'],
        "Published At": snippet['publishedAt'],
        "Channel ID": channel_id,
        "Channel Title": snippet['channelTitle'],
        "Category ID": snippet.get('categoryId'),
        "Tags": snippet.get('tags'),
        "View Count": statistics.get('viewCount'),
        "Like Count": statistics.get('likeCount'),
        "Favorite Count": statistics.get('favoriteCount'),
        "Comment Count": statistics.get('commentCount'),
        "Duration (Seconds)": duration,  # Storing duration in seconds
        "Definition": content_details.get('definition'),
        "Caption": content_details.get('caption'),
        "Licensed Content": content_details.get('licensedContent'),
        "Region Restriction": content_details.get('regionRestriction'),
        "Channel Country": channel_country,  # Handling missing country info
        "Channel Subscriber Count": channel_details['statistics'].get('subscriberCount') if channel_details else None,
        "Channel Video Count": channel_details['statistics'].get('videoCount') if channel_details else None,
        "Channel View Count": channel_details['statistics'].get('viewCount') if channel_details else None,
    })

# Convert data to DataFrame
df = pd.DataFrame(video_data)

# Convert 'View Count' to numeric, coercing errors to NaN
df['View Count'] = pd.to_numeric(df['View Count'], errors='coerce')

# Drop rows with NaN values in 'View Count'
df = df.dropna(subset=['View Count'])

# Save DataFrame to Excel
output_path = 'output/trending_videos_india.xlsx'
df.to_excel(output_path, index=False)

print(f'Data saved to {output_path}')

# Convert 'View Count' and 'Comment Count' to numeric, coercing errors to NaN
df['View Count'] = pd.to_numeric(df['View Count'], errors='coerce')
df['Comment Count'] = pd.to_numeric(df['Comment Count'], errors='coerce')

# Drop rows with NaN values in 'View Count' and 'Comment Count'
df = df.dropna(subset=['View Count', 'Comment Count'])

# Convert 'Duration' to seconds if 'Duration (Seconds)' does not exist
if 'Duration (Seconds)' not in df.columns:
    def parse_duration(duration):
        import isodate
        try:
            return isodate.parse_duration(duration).total_seconds()
        except:
            return None

    df['Duration (Seconds)'] = df['Duration'].apply(parse_duration)

# Drop rows with NaN values in 'Duration (Seconds)'
df = df.dropna(subset=['Duration (Seconds)'])

# Bar plot for top 10 videos by view count
top_videos = df.nlargest(10, 'View Count')
fig_bar = px.bar(top_videos, 
                 x='View Count', 
                 y='Title', 
                 orientation='h', 
                 title='Top 10 Trending Videos by View Count')
fig_bar.update_layout(xaxis_title='View Count', yaxis_title='Video Title', margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="LightSteelBlue")
fig_bar.update_traces(marker_line_color='black', marker_line_width=1.5)
fig_bar.show()

# Histogram of video durations with KDE
fig_hist = px.histogram(df, 
                        x='Duration (Seconds)', 
                        nbins=30, 
                        title='Distribution of Video Durations')
fig_hist.update_layout(xaxis_title='Duration (Seconds)', yaxis_title='Frequency', margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="LightSteelBlue")
fig_hist.update_traces(marker_line_color='black', marker_line_width=1.5)

# Add KDE plot
duration = df['Duration (Seconds)'].dropna()
kde = gaussian_kde(duration)
x_range = np.linspace(duration.min(), duration.max(), 1000)
fig_hist.add_trace(go.Scatter(x=x_range, y=kde(x_range) * len(duration) * (duration.max() - duration.min()) / 30, mode='lines', name='KDE'))

fig_hist.show()

# Scatter plot of view count vs like count
fig_scatter = px.scatter(df, 
                         x='View Count', 
                         y='Like Count', 
                         size='Comment Count', 
                         color='Channel Title', 
                         hover_name='Title',  # Show video name on hover
                         hover_data={'Channel Title': True, 'View Count': True, 'Like Count': True, 'Comment Count': True, 'Channel Subscriber Count': True},  # Additional info on hover
                         log_x=True,  # Log scale for x-axis
                         log_y=True,  # Log scale for y-axis
                         title='View Count vs Like Count')
fig_scatter.update_layout(xaxis_title='View Count', yaxis_title='Like Count', margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="LightSteelBlue")
fig_scatter.update_traces(marker_line_color='black', marker_line_width=1.5)
fig_scatter.show()