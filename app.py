import streamlit as st
import pickle
from difflib import get_close_matches
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import random

# --- Spotify API Credentials ---
client_id = "30706e60ea9c4b55a1c6e495f136321b"
client_secret = "a161bd80c33c4e41b8167e4ab627cd47"

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# --- Load Data ---
df = pickle.load(open("df.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# --- In-Memory Playlist ---
playlist = []

# --- Recommend Songs Logic ---
def recommend(song_name):
    song_list = df['song'].fillna('').str.lower().tolist()
    close_matches = get_close_matches(song_name.lower(), song_list, n=1)

    if not close_matches:
        return []

    match_index = df[df['song'].str.lower() == close_matches[0]].index[0]
    song_scores = sorted(list(enumerate(similarity[match_index])), key=lambda x: x[1], reverse=True)[1:6]
    return [df.iloc[i[0]]['song'] for i in song_scores]

# --- YouTube Link Fetcher using yt_dlp ---
def get_youtube_link(song_name):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
        'default_search': 'ytsearch1',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(song_name, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                return f"https://www.youtube.com/watch?v={info['entries'][0]['id']}"
        except Exception as e:
            return None
    return None

# --- Get Spotify Link ---
def get_spotify_link(song_name):
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        spotify_url = track['external_urls']['spotify']
        album_cover = track['album']['images'][1]['url']
        return spotify_url, album_cover
    else:
        return None, None

# --- AI Lyrics Generator ---
def generate_lyrics(theme):
    lines = [
        f"In the rhythm of {theme}, my soul takes flight,",
        f"Dancing with stars through the silent night.",
        f"Every beat echoes {theme} so bright,",
        f"Lost in lyrics, chasing the light."
    ]
    random.shuffle(lines)
    return "\n".join(lines)

# --- Streamlit UI ---
st.set_page_config(page_title="🎵 AI Music Assistant", page_icon="🎧", layout="wide")
st.title("🎧 AI Music Assistant")

feature = st.sidebar.radio("Choose Feature", ["🎶 Recommend Songs", "📝 Generate Lyrics", "📂 Playlist"])

# --- Recommend Songs UI ---
if feature == "🎶 Recommend Songs":
    mood = st.text_input("Enter a song or mood:")
    if st.button("Get Recommendations"):
        if mood:
            songs = recommend(mood)
            if songs:
                st.subheader("Recommended Songs:")
                for song in songs:
                    youtube_link = get_youtube_link(song)
                    st.markdown(f"**🎵 {song}**")
                    if youtube_link:
                        st.video(youtube_link)
                        if st.button(f"➕ Add '{song}' to Playlist", key=song):
                            if song not in playlist:
                                playlist.append(song)
                                st.success(f"'{song}' added to your playlist!")
                    st.markdown("---")
            else:
                st.warning("Song not found!")

# --- Lyrics UI ---
elif feature == "📝 Generate Lyrics":
    theme = st.text_input("Enter a theme (e.g. love, night, party):")
    if st.button("Generate Lyrics"):
        if theme:
            st.subheader(f"🎼 Lyrics about '{theme}':")
            st.text(generate_lyrics(theme))
        else:
            st.warning("Please enter a theme.")

# --- Playlist UI ---
elif feature == "📂 Playlist":
    st.subheader("📀 Your Playlist")
    if playlist:
        for song in playlist:
            st.markdown(f"**🎵 {song}**")
            youtube_link = get_youtube_link(song)
            if youtube_link:
                st.video(youtube_link)
    else:
        st.info("Your playlist is empty!")
