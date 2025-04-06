import streamlit as st
import pickle
from difflib import get_close_matches
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
import openai

# Spotify API setup
client_id = "30706e60ea9c4b55a1c6e495f136321b"
client_secret = "a161bd80c33c4e41b8167e4ab627cd47"
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# OpenAI API Key for Lyrics & Descriptions (replace with your key)
openai.api_key = "sk-REPLACE_WITH_YOUR_KEY"

# Load preprocessed data
df = pickle.load(open("df.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# Mood-based mapping
mood_map = {
    "Happy": ["Dance", "Pop", "Electronic"],
    "Sad": ["Acoustic", "Piano", "Indie"],
    "Energetic": ["EDM", "Hip-Hop", "Workout"],
    "Chill": ["Lo-fi", "Jazz", "Chillout"],
}

# Song recommender function
def recommend(song_name):
    song_list = df['song'].fillna('').str.lower().tolist()
    close_matches = get_close_matches(song_name.lower(), song_list, n=1)
    if not close_matches:
        return []
    match_index = df[df['song'].str.lower() == close_matches[0]].index[0]
    song_scores = sorted(list(enumerate(similarity[match_index])), key=lambda x: x[1], reverse=True)[1:6]
    return [df.iloc[i[0]]['song'] for i in song_scores]

# Get Spotify preview link & album art
def get_spotify_link(song_name):
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        url = track['external_urls']['spotify']
        cover = track['album']['images'][1]['url']
        return url, cover
    return None, None

# AI Lyric Generator
def generate_lyrics(theme):
    prompt = f"Write original lyrics about: {theme}."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

# AI Song Description
def generate_description(song_name):
    prompt = f"Describe the theme and vibe of the song '{song_name}' in 3 lines."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

# Playlist Generator
def generate_playlist(mood):
    tags = mood_map.get(mood, [])
    filtered = df[df['tags'].apply(lambda x: any(tag.lower() in x.lower() for tag in tags))]
    sample = filtered.sample(min(10, len(filtered)))
    return sample['song'].tolist()

# Streamlit UI
st.set_page_config(page_title="🎵 AI Music Assistant", layout="wide")

st.markdown("""
    <style>
    body {
        background: linear-gradient(to bottom, #121212, #1e1e1e);
        color: white;
    }
    .card {
        background-color: #181818;
        border-radius: 10px;
        padding: 15px;
        margin: 10px;
        text-align: center;
        color: white;
        display: inline-block;
        width: 180px;
    }
    .card img {
        width: 150px;
        height: 150px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎶 AI Music Assistant")
st.markdown("Your all-in-one intelligent music companion 🎧")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Song Recommender", "📜 AI Lyrics", "🎭 Mood Playlist", "📖 Song Summary"])

with tab1:
    song_name = st.text_input("Enter a song:")
    if st.button("Recommend"):
        if song_name:
            results = recommend(song_name)
            st.subheader("Recommended Songs:")
            cols = st.columns(5)
            for i, song in enumerate(results):
                link, cover = get_spotify_link(song)
                with cols[i % 5]:
                    if link:
                        st.markdown(f"<div class='card'><img src='{cover}'/><p><b>{song}</b></p><a href='{link}' target='_blank'>🎧 Listen</a></div>", unsafe_allow_html=True)
                    else:
                        st.write(f"🎶 {song}")

with tab2:
    theme = st.text_input("Generate lyrics about (mood, topic, genre):")
    if st.button("Generate Lyrics"):
        lyrics = generate_lyrics(theme)
        st.text_area("🎤 AI Generated Lyrics", value=lyrics, height=300)

with tab3:
    mood = st.selectbox("Choose a mood:", list(mood_map.keys()))
    if st.button("Generate Playlist"):
        songs = generate_playlist(mood)
        st.subheader(f"🎧 Playlist for '{mood}' mood")
        for song in songs:
            link, _ = get_spotify_link(song)
            if link:
                st.markdown(f"[{song}]({link})")
            else:
                st.write(f"🎵 {song}")

with tab4:
    song_input = st.text_input("Enter a song to summarize:")
    if st.button("Get Summary"):
        summary = generate_description(song_input)
        st.write("📝", summary)
