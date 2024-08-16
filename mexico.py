import os
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv('YOUTUBE_API_KEY')

# Set up YouTube Data API
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Function to get trending videos
def get_trending_videos(region_code='MX', max_results=50):  # 'US' for United States
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
        "Duration": content_details.get('duration'),
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

# Save DataFrame to Excel
output_path = 'output/trending_videos_mexico.xlsx'
df.to_excel(output_path, index=False)

print(f'Data saved to {output_path}')