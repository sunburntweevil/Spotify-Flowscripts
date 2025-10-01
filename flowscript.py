import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy as np
import CONFIG as con

PLAYLIST_ID = con.PLAYLIST_ID

# ------------ AUTHENTICATION -------------
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=con.CLIENT_ID,
    client_secret=con.CLIENT_SECRET,
    redirect_uri=con.REDIRECT_URI,
    scope='playlist-modify-public playlist-modify-private playlist-read-private'
))

# ------------ FETCH TRACKS & FEATURES -------------
def get_all_tracks(playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

tracks = get_all_tracks(PLAYLIST_ID)
# Filter out local files and None tracks, keep only Spotify tracks
valid_tracks = []
track_ids = []
for item in tracks:
    if item['track'] and item['track']['id'] and item['track']['is_local'] == False:
        valid_tracks.append(item)
        track_ids.append(item['track']['id'])

print(f"Found {len(tracks)} total tracks, {len(valid_tracks)} are valid Spotify tracks")

# Try to get audio features with fallback strategy
features = []
successful_track_ids = []

print("Attempting to retrieve audio features...")

# First, try batch requests (this will likely fail due to 403 error)
batch_success = False
for i in range(0, len(track_ids), 100):
    batch = track_ids[i:i+100]
    try:
        batch_features = sp.audio_features(batch)
        # Filter out None results
        valid_features = [f for f in batch_features if f is not None]
        if valid_features:
            features.extend(valid_features)
            successful_track_ids.extend(batch[:len(valid_features)])
            print(f"✓ Retrieved features for batch {i//100 + 1}, got {len(valid_features)} valid features")
            batch_success = True
        else:
            print(f"⚠ Batch {i//100 + 1} returned no valid features")
    except Exception as e:
        print(f"✗ Batch {i//100 + 1} failed: {e}")
        
        # If batch fails, try individual requests as fallback
        print(f"  Trying individual requests for batch {i//100 + 1}...")
        for j, track_id in enumerate(batch):
            try:
                individual_features = sp.audio_features([track_id])
                if individual_features[0]:
                    features.append(individual_features[0])
                    successful_track_ids.append(track_id)
                    if j % 10 == 0:  # Progress update every 10 tracks
                        print(f"    Individual progress: {j+1}/{len(batch)}")
            except:
                continue  # Skip tracks that fail individually

print(f"Successfully retrieved audio features for {len(features)} tracks")

# ------------ NORMALIZE FEATURES -------------
print(f"Processing {len(features)} tracks with valid audio features")

if len(features) == 0:
    print("Error: No audio features retrieved. Cannot proceed with reordering.")
    exit(1)

# Filter valid_tracks to only include those with successful audio features
final_valid_tracks = []
final_artists = []

for track_id in successful_track_ids:
    # Find the corresponding track in valid_tracks
    for item in valid_tracks:
        if item['track']['id'] == track_id:
            final_valid_tracks.append(item)
            final_artists.append(item['track']['artists'][0]['id'])
            break

# Update variables to use only tracks with features
valid_tracks = final_valid_tracks
track_ids = successful_track_ids
artists = final_artists

print(f"Final processing set: {len(features)} tracks with audio features")

def normalize(arr):
    arr = np.array(arr)
    return (arr - arr.min()) / (arr.max() - arr.min() + 1e-9)

bpm = normalize([f['tempo'] for f in features])
key = normalize([f['key'] for f in features])
danceability = normalize([f['danceability'] for f in features])
valence = normalize([f['valence'] for f in features])
loudness = normalize([f['loudness'] for f in features])

# ------------ SMOOTH SEQUENCING -------------
ordered = []
used = set()
curr = 0  # Start from first track

while len(ordered) < len(valid_tracks):
    ordered.append(curr)
    used.add(curr)
    # Compute distances to remaining tracks
    dists = []
    for i in range(len(valid_tracks)):
        if i in used: continue
        # Penalize same artist (but not at expense of smoothness)
        artist_penalty = 1.0 if artists[i] == artists[curr] else 0.0
        v1 = np.array([bpm[curr], key[curr], danceability[curr], valence[curr], loudness[curr]])
        v2 = np.array([bpm[i], key[i], danceability[i], valence[i], loudness[i]])
        dist = np.linalg.norm(v1 - v2) + artist_penalty * 0.3
        dists.append((dist, i))
    if not dists: break
    # Pick the closest track
    dists.sort()
    curr = dists[0][1]

# ------------ GENERATE NEW ORDER -------------
new_order_track_ids = [track_ids[i] for i in ordered if i < len(track_ids)]

# ------------ REORDER PLAYLIST -------------
print("Updating playlist order...")
try:
    # Handle Spotify's 100-track limit by using batches
    if len(new_order_track_ids) <= 100:
        sp.playlist_replace_items(PLAYLIST_ID, new_order_track_ids)
    else:
        # Clear playlist first, then add in batches
        sp.playlist_replace_items(PLAYLIST_ID, [])
        
        batch_size = 100
        for i in range(0, len(new_order_track_ids), batch_size):
            batch = new_order_track_ids[i:i+batch_size]
            if i == 0:
                sp.playlist_replace_items(PLAYLIST_ID, batch)
            else:
                sp.playlist_add_items(PLAYLIST_ID, batch)
            print(f"Added batch {i//batch_size + 1}/{(len(new_order_track_ids) + batch_size - 1)//batch_size}")
    
    print("✓ Done! Playlist reordered by tempo, key, danceability, valence, and loudness.")
except Exception as e:
    print(f"Error updating playlist: {e}")
