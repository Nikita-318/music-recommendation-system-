from flask import Flask, request, render_template
import numpy as np
import pandas as pd
import pickle
import requests  # To fetch images dynamically

# Loading models
df = pickle.load(open('df.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

def fetch_image(song_name):
    """Fetch song image using iTunes Search API."""
    query = requests.get(f"https://itunes.apple.com/search?term={song_name}&limit=1&media=music")
    if query.status_code == 200:
        data = query.json()
        if data['resultCount'] > 0:
            return data['results'][0]['artworkUrl100']  # Small artwork
    return None  # Return None if no image is found

def fetch_background_images():
    """Fetch multiple random images for the background."""
    songs = df['song'].sample(10).values  # Randomly sample 10 songs
    images = [fetch_image(song) for song in songs if fetch_image(song)]
    return images

def recommendation(song_name):
    """Recommend similar songs."""
    if song_name not in df['song'].values:
        return [("Song not found in the database.", None)]
    
    idx = df[df['song'] == song_name].index[0]
    distances = sorted(list(enumerate(similarity[idx])), reverse=True, key=lambda x: x[1])
    
    songs = []
    for m_id in distances[1:21]:
        recommended_song = df.iloc[m_id[0]].song
        image_url = fetch_image(recommended_song)  # Fetch image dynamically
        songs.append((recommended_song, image_url))
        
    return songs

# Flask app
app = Flask(__name__)

# Routes
@app.route('/')
def index():
    names = list(df['song'].values)
    background_images = fetch_background_images()  # Fetch images for background
    return render_template('index.html', names=names, selected_song=None, songs=None, background_images=background_images)

@app.route('/recom', methods=['POST'])
def mysong():
    user_song = request.form['names']
    songs = recommendation(user_song)
    names = list(df['song'].values)
    background_images = fetch_background_images()
    return render_template('index.html', names=names, selected_song=user_song, songs=songs, background_images=background_images)

if __name__ == "__main__":
    app.run(debug=True)
