import streamlit as st
import pickle
import random
from difflib import get_close_matches
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build

SPOTIFY_CLIENT_ID = "30706e60ea9c4b55a1c6e495f136321b"
SPOTIFY_CLIENT_SECRET = "a161bd80c33c4e41b8167e4ab627cd47"
YOUTUBE_API_KEY = "AIzaSyDvDYbr5Lwlt-pz_Ej2Ut0eLprDT7XKBP0"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

df = pickle.load(open("df.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

def recommend(song_name):
    song_list = df['song'].fillna('').str.lower().tolist()
    close_matches = get_close_matches(song_name.lower(), song_list, n=1)
    if not close_matches:
        return []
    match_index = df[df['song'].str.lower() == close_matches[0]].index[0]
    song_scores = sorted(list(enumerate(similarity[match_index])), key=lambda x: x[1], reverse=True)[1:6]
    return [df.iloc[i[0]]['song'] for i in song_scores]

def get_spotify_link(song_name):
    results = sp.search(q=song_name, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        spotify_url = track['external_urls']['spotify']
        album_cover = track['album']['images'][1]['url']
        return spotify_url, album_cover
    else:
        return None, None

def get_youtube_link(song_name):
    try:
        request = youtube.search().list(
            q=song_name + " song", part="snippet", maxResults=1, type="video")
        response = request.execute()
        if response["items"]:
            video_id = response["items"][0]["id"]["videoId"]
            return f"https://www.youtube.com/watch?v={video_id}"
        return None
    except Exception as e:
        print("YouTube API error:", e)
        return None

def generate_lyrics(theme):
    templates = [
        f"Under the sky of {theme}, the winds softly sigh,\nWhispers of dreams, they shimmer and fly.\nIn every heartbeat, the {theme} takes its place,\nPainting my soul with a gentle embrace.",
        f"The {theme} in my heart, it won't let go,\nThrough stormy nights and mornings aglow.\nEvery word I sing is drenched in {theme},\nLike rivers flowing in a vivid dream.",
        f"Let the world fade, but {theme} remain,\nA rhythm running deep like rain.\nThis melody's wrapped in {theme}'s spell,\nA tale only the moon can tell.",
        f"Chasing echoes of {theme} in the dark,\nLighting my path like a glowing spark.\nNo silence loud enough to break,\nThe promise {theme} dares to make."
    ]
    return random.choice(templates)

st.set_page_config(page_title="🎵 AI Music Recommender", page_icon="🎶", layout="wide")
st.title("🎵 AI Music Recommender")

option = st.sidebar.radio("Choose Feature", ["🔍 Recommend Songs", "✍️ Generate Lyrics"])

if option == "🔍 Recommend Songs":
    user_input = st.text_input("Enter a song name:")
    if st.button("Recommend"):
        if user_input:
            results = recommend(user_input)
            if results:
                st.subheader("Recommended Songs:")
                cols = st.columns(5)
                for i, song in enumerate(results):
                    link, cover = get_spotify_link(song)
                    youtube_link = get_youtube_link(song)
                    if link and cover:
                        cols[i % 5].markdown(f"""
                            <div style="background:#181818; padding:15px; border-radius:10px; text-align:center; color:white;">
                                <img src="{cover}" width="150" height="150" style="border-radius:10px;"><br>
                                <b>{song}</b><br>
                                <a href="{link}" target="_blank">🔗 Listen on Spotify</a><br>
                                {'<a href="' + youtube_link + '" target="_blank">▶️ Watch on YouTube</a>' if youtube_link else '❌ YouTube video not found'}
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning(f"🎶 {song} (No Spotify link)")
            else:
                st.error("❌ Song not found.")
elif option == "✍️ Generate Lyrics":
    theme = st.text_input("Enter a theme or mood (love, party, night, etc.):")
    if st.button("Generate Lyrics"):
        if theme:
            st.subheader(f"🎼 Lyrics about '{theme}':")
            st.text(generate_lyrics(theme))
        else:
            st.warning("Please enter a theme.")
