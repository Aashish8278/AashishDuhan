import streamlit as st
import pickle
from difflib import get_close_matches
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

# Spotify API setup
client_id = "30706e60ea9c4b55a1c6e495f136321b"
client_secret = "a161bd80c33c4e41b8167e4ab627cd47"
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load preprocessed data
df = pickle.load(open("df.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# Recommend songs based on input
def recommend(song_name):
    song_list = df['song'].fillna('').str.lower().tolist()
    close_matches = get_close_matches(song_name.lower(), song_list, n=1)
    if not close_matches:
        return []
    match_index = df[df['song'].str.lower() == close_matches[0]].index[0]
    song_scores = sorted(list(enumerate(similarity[match_index])), key=lambda x: x[1], reverse=True)[1:6]
    return [df.iloc[i[0]]['song'] for i in song_scores]

# Fetch Spotify link, album cover, and popularity
def get_spotify_link(song_name):
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        spotify_url = track['external_urls']['spotify']
        album_cover = track['album']['images'][1]['url']
        popularity = track['popularity']
        artist = track['artists'][0]['name']
        return spotify_url, album_cover, popularity, artist
    return None, None, None, None

# Get lyrics using lyrics.ovh API
def get_lyrics(song_title, artist_name=""):
    try:
        response = requests.get(f"https://api.lyrics.ovh/v1/{artist_name}/{song_title}")
        data = response.json()
        return data.get('lyrics', 'Lyrics not found.')
    except:
        return "Error fetching lyrics."

# Page settings
st.set_page_config(page_title="🎵 AI Music Recommender", page_icon="🎶", layout="wide")

# Custom CSS for Spotify-like theme
st.markdown("""
    <style>
        body {
            background: linear-gradient(to bottom, #121212, #1e1e1e);
            color: white;
            font-family: 'Arial', sans-serif;
        }
        .css-ffhzg2, .css-1v3fvcr {
            background-color: transparent;
            color: white;
        }
        .stTitle { font-size: 40px; font-weight: bold; text-align: center; }
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
        .stButton>button:hover { background-color: #1ed760; }
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
            vertical-align: top;
        }
        .card:hover { transform: scale(1.05); }
        .card img {
            width: 150px;
            height: 150px;
            border-radius: 10px;
        }
        .stSubheader { font-size: 24px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🎵 AI Music Recommender")

search_by = st.radio("Search by:", ("Song Name",))
user_input = st.text_input(f"Enter {search_by.lower()}:")

if st.button("Recommend"):
    if user_input:
        results = recommend(user_input)
        if results:
            st.subheader("Recommended Songs:")
            cols = st.columns(5)
            for i, song in enumerate(results):
                spotify_link, album_cover, popularity, artist = get_spotify_link(song)
                col = cols[i % 5]
                if spotify_link and album_cover:
                    with col:
                        st.markdown(f"""
                            <div class="card">
                                <img src="{album_cover}" alt="{song}">
                                <h4>{song}</h4>
                                <p>Artist: {artist}</p>
                                <p>Popularity: {popularity}/100</p>
                                <a href="{spotify_link}" target="_blank" style="text-decoration: none; color: white; font-size: 14px; background-color: #1db954; padding: 5px 10px; border-radius: 20px;">Listen on Spotify</a>
                            </div>
                        """, unsafe_allow_html=True)

                        if st.button(f"Show Lyrics 🎤", key=f"lyrics_{i}"):
                            lyrics = get_lyrics(song, artist)
                            st.text_area("Lyrics", lyrics, height=300)
                else:
                    col.write(f"🎶 {song} (No Spotify link available)")

            # Download recommendation button
            st.download_button("Download Recommendations", "\n".join(results), file_name="recommendations.txt")
        else:
            st.warning("❌ Song not found in the database.")
