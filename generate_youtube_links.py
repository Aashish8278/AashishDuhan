import pandas as pd
from youtubesearchpython import VideosSearch
import time

# Load dataset
df = pd.read_csv('spotify_millsongdata3.csv')

# Create a new column to store YouTube links
youtube_links = []

# Helper function to fetch YouTube link with error handling
def get_youtube_link(query):
    try:
        videosSearch = VideosSearch(query, limit=1)
        result = videosSearch.result()
        if result['result']:
            return result['result'][0]['link']
    except Exception as e:
        print(f"❌ Error for '{query}': {e}")
        time.sleep(1)  # short pause before moving on
    return None

# Loop through dataset and get YouTube links
for index, row in df.iterrows():
    title = row['song']
    artist = row['artist']
    query = f"{title} {artist} song"
    print(f"🔍 Searching: {query}")
    
    link = get_youtube_link(query)
    youtube_links.append(link)

    # Optional: slow down requests to avoid getting blocked
    time.sleep(0.5)

# Add YouTube links to the DataFrame
df['youtube_link'] = youtube_links

# Save updated dataset
df.to_csv('spotify_millsongdata_with_links.csv', index=False)
print("✅ Done! YouTube links saved to 'spotify_millsongdata_with_links.csv'")
