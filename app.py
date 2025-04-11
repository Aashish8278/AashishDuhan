import streamlit as st
import pickle
from difflib import get_close_matches
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
from googleapiclient.discovery import build

# Spotify credentials
client_id = "30706e60ea9c4b55a1c6e495f136321b"
client_secret = "a161bd80c33c4e41b8167e4ab627cd47"

# YouTube API Key
YOUTUBE_API_KEY = "AIzaSyDvDYbr5Lwlt-pz_Ej2Ut0eLprDT7XKBP0"

# Initialize Spotify
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load data
df = pickle.load(open("df.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# Recommendation engine
def recommend(song_name):
    song_list = df['song'].fillna('').str.lower().tolist()
    close_matches = get_close_matches(song_name.lower(), song_list, n=1)

    if not close_matches:
        return []

    match_index = df[df['song'].str.lower() == close_matches[0]].index[0]
    song_scores = sorted(list(enumerate(similarity[match_index])), key=lambda x: x[1], reverse=True)[1:6]
    return [df.iloc[i[0]]['song'] for i in song_scores]

# Get Spotify link and album cover
def get_spotify_link(song_name):
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        spotify_url = track['external_urls']['spotify']
        album_cover = track['album']['images'][1]['url']
        return spotify_url, album_cover
    else:
        return None, None

# Get YouTube link via YouTube Data API
def get_youtube_link(song_name):
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(
            part='snippet',
            q=song_name + " official audio",
            type='video',
            maxResults=1
        )
        response = request.execute()

        if response['items']:
            video_id = response['items'][0]['id']['videoId']
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            return youtube_url
        else:
            return None
    except Exception as e:
        print("YouTube API Error:", e)
        return None

# Generate lyrics
def generate_lyrics(theme):
    lines = [
        f"🎤 In the rhythm of {theme}, my soul takes flight,",
        f"🎶 Dancing with stars through the silent night.",
        f"💫 Every beat echoes {theme} so bright,",
        f"🌙 Lost in lyrics, chasing the light."
    ]
    random.shuffle(lines)
    return "\n".join(lines)

# Streamlit UI
st.set_page_config(page_title="🎵 AI Music Recommender", page_icon="🎶", layout="wide")
st.markdown("""
    <style>
        body { background-color: #121212; color: white; }
        .stTitle { font-size: 40px; font-weight: bold; text-align: center; }
        .stButton>button { background-color: #1db954; color: white; border-radius: 30px; font-size: 18px; }
        .card { background-color: #181818; border-radius: 10px; padding: 20px; margin: 20px; text-align: center; color: white; width: 200px; display: inline-block; }
        .card img { width: 150px; height: 150px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎵 AI Music Recommender")

# Sidebar options
option = st.sidebar.radio("Choose Feature", ["🔍 Recommend Songs", "✍️ Generate Lyrics"])

# Recommend songs section
if option == "🔍 Recommend Songs":
    user_input = st.text_input("Enter a song name:")
    if st.button("Recommend"):
        if user_input:
            results = recommend(user_input)
            if results:
                st.subheader("Recommended Songs:")
                cols = st.columns(5)
                for i, song in enumerate(results):
                    spotify_link, cover = get_spotify_link(song)
                    youtube_link = get_youtube_link(song)
                    with cols[i % 5]:
                        if cover:
                            st.image(cover, caption=song, use_container_width=True)
                        st.markdown(f"[🎧 Listen on Spotify]({spotify_link})", unsafe_allow_html=True)
                        if youtube_link:
                            st.markdown(f"[▶️ Watch on YouTube]({youtube_link})", unsafe_allow_html=True)
                        else:
                            st.write("❌ YouTube video not found.")
            else:
                st.warning("❌ Song not found.")
        else:
            st.warning("Please enter a song name.")

# Generate lyrics section
elif option == "✍️ Generate Lyrics":
    theme = st.text_input("Enter a theme or mood (love, party, night, etc.):")
    if st.button("Generate Lyrics"):
        if theme:
            st.subheader(f"🎼 Lyrics about '{theme}':")
            st.text(generate_lyrics(theme))
        else:
            st.warning("Please enter a theme.")
