import streamlit as st
import pickle
from difflib import get_close_matches
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Spotify API setup
client_id = "30706e60ea9c4b55a1c6e495f136321b"  # Your Spotify client ID
client_secret = "a161bd80c33c4e41b8167e4ab627cd47"  # Your Spotify client secret

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load preprocessed data
df = pickle.load(open("df.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# Function to recommend songs
def recommend(song_name):
    song_list = df['song'].fillna('').str.lower().tolist()

    # Try to find close matches
    close_matches = get_close_matches(song_name.lower(), song_list, n=1)

    if not close_matches:
        return []

    match_index = df[df['song'].str.lower() == close_matches[0]].index[0]
    song_scores = sorted(list(enumerate(similarity[match_index])), key=lambda x: x[1], reverse=True)[1:6]

    recommended_songs = []
    for i in song_scores:
        recommended_songs.append(df.iloc[i[0]]['song'])

    return recommended_songs

# Function to get Spotify link for a song and album cover
def get_spotify_link(song_name):
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        spotify_url = track['external_urls']['spotify']
        album_cover = track['album']['images'][1]['url']  # Smaller image size (adjusted to index 1)
        return spotify_url, album_cover
    else:
        return None, None

# Streamlit UI - Customizing UI with Spotify-like Design
st.set_page_config(page_title="🎵 AI Music Recommender", page_icon="🎶", layout="wide")

# Set custom background and Spotify theme
st.markdown("""
    <style>
        /* Background styling to resemble Spotify */
        body {
            background: linear-gradient(to bottom, #121212, #1e1e1e);
            color: white;
            font-family: 'Arial', sans-serif;
        }

        .css-ffhzg2, .css-1v3fvcr {
            background-color: transparent;
            color: white;
        }

        /* Styling the header */
        .stTitle {
            font-size: 40px;
            font-weight: bold;
            margin-top: 40px;
            text-align: center;
        }

        /* Textbox Styling */
        .stTextInput input {
            background-color: #121212;
            color: white;
            border: 1px solid #1db954;
        }

        .stTextInput>div>input:focus {
            border-color: #1db954;
            box-shadow: 0 0 5px #1db954;
        }

        /* Button Styling */
        .stButton>button {
            background-color: #1db954;
            color: white;
            border-radius: 30px;
            font-size: 18px;
        }

        .stButton>button:hover {
            background-color: #1ed760;
        }

        /* Song Cards */
        .card {
            background-color: #181818;
            border-radius: 10px;
            padding: 20px;
            margin: 20px;
            text-align: center;
            color: white;
            box-shadow: 0px 0px 15px rgba(0,0,0,0.3);
            transition: transform 0.3s ease-in-out;
            display: inline-block;
            width: 180px; /* Set width of the card */
            vertical-align: top;
        }

        .card:hover {
            transform: scale(1.05);
        }

        .card img {
            width: 150px; /* Adjust size of the image */
            height: 150px; /* Keep aspect ratio */
            border-radius: 10px;
        }

        .stSubheader {
            font-size: 24px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Title for the app
st.title("🎵 AI Music Recommender")

# Input box for song search
user_input = st.text_input("Enter a song name:")

# Recommend button
if st.button("Recommend"):
    if user_input:
        results = recommend(user_input)
        if results:
            st.subheader("Recommended Songs:")
            # Display song recommendations
            cols = st.columns(5)  # Create 5 columns for better layout
            for i, song in enumerate(results):
                spotify_link, album_cover = get_spotify_link(song)
                if spotify_link and album_cover:
                    col = cols[i % 5]  # Distribute the cards across 5 columns
                    col.markdown(f"""
                        <div class="card">
                            <img src="{album_cover}" alt="{song}">
                            <h3>{song}</h3>
                            <a href="{spotify_link}" target="_blank" style="text-decoration: none; color: white; font-size: 18px; background-color: #1db954; padding: 10px 20px; border-radius: 20px;">Listen on Spotify</a>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.write(f"🎶 {song} (No Spotify link available)")
        else:
            st.warning("❌ Song not found in the database.")
