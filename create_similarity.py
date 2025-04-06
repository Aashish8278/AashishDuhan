import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load the dataset
df = pd.read_csv('spotify_millsongdata 3.csv')

# Rename columns to lowercase (optional)
df.columns = [col.lower() for col in df.columns]

# Fill missing values in lyrics/text
df['text'] = df['text'].fillna('')

# Create TF-IDF matrix
vectorizer = TfidfVectorizer(stop_words='english')
tfidf = vectorizer.fit_transform(df['text'])

# Compute similarity
similarity = cosine_similarity(tfidf)

# Save both df and similarity
pickle.dump(df, open('df.pkl', 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))
