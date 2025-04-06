import pandas as pd
from fuzzywuzzy import fuzz

# Load your dataset (ensure the path is correct)
df = pd.read_csv('path_to_your_dataset/spotify_millsongdata 3.csv')  # Update this path

# Function to search for a song in the dataset
def search_song(song_name, df, threshold=80):
    song_name = song_name.lower()  # Convert input to lowercase for case-insensitive matching
    matches = []  # Store matched songs

    for index, row in df.iterrows():
        dataset_song = str(row['song_name']).lower()  # Update if column name is different (e.g., 'track_name')
        
        # Calculate similarity score
        similarity = fuzz.partial_ratio(song_name, dataset_song)
        
        # If similarity exceeds threshold, consider it a match
        if similarity >= threshold:
            matches.append((row['song_name'], row['artist_name'], similarity))  # Adjust if column names differ

    return matches

# Replace this with the song name you're searching for (could be dynamic in your project)
song_to_find = 'Andante, Andante'  # Example song name

# Perform the search
matched_songs = search_song(song_to_find, df)

# Output the result
if matched_songs:
    for song, artist, similarity in matched_songs:
        # This will display the match information in the Streamlit app or print to console
        print(f"Song: {song} | Artist: {artist} | Similarity: {similarity}%")
else:
    print(f"Song '{song_to_find}' not found in the dataset.")

# Fallback if no match is found
if not matched_songs:
    print("\nFallback: The song wasn't found. You might want to try searching it on YouTube or Spotify.")
