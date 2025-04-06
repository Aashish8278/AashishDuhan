import pandas as pd
import pickle

# Load your CSV file (make sure the name is correct)
df = pd.read_csv('spotify_millsongdata 3.csv')  # adjust the file name if needed

# Save the dataframe as a pickle file
with open('df.pkl', 'wb') as f:
    pickle.dump(df, f)

print("✅ df.pkl created successfully!")
