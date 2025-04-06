import streamlit as st
import pickle
from difflib import get_close_matches
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Spotify API setup
client_id = "30706e60ea9c4b55a1c6e495f136321b"
client_secret = "a161bd80c33c4e41b8167e4ab627cd47"

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load preprocessed data
df = pickle.load(open("df.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# Function to recommend songs
def recommend(song_name):
    song_list = df['song'].fillna('').str.lower().tolist()
    close_matches = get_close_matches(song_name.lower(), song_list, n=1)
    if not close_matches:
        return []

    match_index = df[df['song'].str.lower() == close_matches[0]].index[0]
    song_scores = sorted(list(enumerate(similarity[match_index])), key=lambda x: x[1], reverse=True)[1:6]
    recommended_songs = [df.iloc[i[0]]['song'] for i in song_scores]
    return recommended_songs

# Function to get Spotify link and album cover
def get_spotify_link(song_name):
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        spotify_url = track['external_urls']['spotify']
        album_cover = track['album']['images'][1]['url']
        preview_url = track.get('preview_url')  # 30 sec audio preview
        return spotify_url, album_cover, preview_url
    else:
        return None, None, None

# Set Streamlit page config
st.set_page_config(page_title="🎵 AI Music Recommender", page_icon="🎶", layout="wide")

# Custom CSS for Spotify-style UI
st.markdown("""
    <style>
        body {background: linear-gradient(to bottom, #121212, #1e1e1e); color: white;}
        .stTextInput input {
            background-color: #121212;
            color: white;
            border: 1px solid #1db954;
        }
        .stButton>button {
            background-color: #1db954;
            color: white;
            border-radius: 30px;
            font-size: 18px;
        }
        .card {
            background-color: #181818;
            border-radius: 10px;
            padding: 20px;
            margin: 20px;
            text-align: center;
            color: white;
            box-shadow: 0px 0px 15px rgba(0,0,0,0.3);
            display: inline-block;
            width: 180px;
        }
        .card img {
            width: 150px;
            height: 150px;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🎵 AI Music Recommender")

user_input = st.text_input("Enter a song name:")

if st.button("Recommend"):
    if user_input:
        results = recommend(user_input)
        if results:
            st.subheader("Recommended Songs:")
            cols = st.columns(5)
            for i, song in enumerate(results):
                spotify_link, album_cover, preview_url = get_spotify_link(song)
                if spotify_link and album_cover:
                    with cols[i % 5]:
                        st.image(album_cover, width=150)
                        st.markdown(f"**{song}**")
                        st.markdown(f"[🔗 Listen on Spotify]({spotify_link})")
                        if preview_url:
                            st.audio(preview_url, format="audio/mp3")
                else:
                    st.write(f"🎶 {song} (No preview available)")
        else:
            st.warning("❌ Song not found in the database.")
