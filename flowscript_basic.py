import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy as np
import CONFIG as con

# ------------ AUTHENTICATION -------------
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=con.CLIENT_ID,
    client_secret=con.CLIENT_SECRET,
    redirect_uri=con.REDIRECT_URI,
    scope='playlist-modify-public playlist-modify-private playlist-read-private'
))

# ------------ FETCH TRACKS -------------
def get_all_tracks(playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

tracks = get_all_tracks(con.PLAYLIST_ID)
# Filter out local files and None tracks, keep only Spotify tracks
valid_tracks = []
for item in tracks:
    if item['track'] and item['track']['id'] and not item['track']['is_local']:
        valid_tracks.append(item)

print(f"Found {len(tracks)} total tracks, {len(valid_tracks)} are valid Spotify tracks")

if len(valid_tracks) == 0:
    print("Error: No valid tracks found. Cannot proceed with reordering.")
    exit(1)

# ------------ CREATE SIMILARITY FEATURES FROM AVAILABLE DATA -------------
def normalize(arr):
    arr = np.array(arr)
    if arr.max() == arr.min():
        return np.zeros_like(arr)
    return (arr - arr.min()) / (arr.max() - arr.min())

# Extract features from track metadata
track_popularity = normalize([item['track']['popularity'] for item in valid_tracks])
track_duration = normalize([item['track']['duration_ms'] for item in valid_tracks])
track_explicit = np.array([1.0 if item['track']['explicit'] else 0.0 for item in valid_tracks])

# Get artist info
artists = [item['track']['artists'][0]['id'] for item in valid_tracks]
artist_names = [item['track']['artists'][0]['name'] for item in valid_tracks]

# Get release dates for temporal grouping
release_years = []
for item in valid_tracks:
    album_date = item['track']['album']['release_date']
    if len(album_date) >= 4:
        year = int(album_date[:4])
    else:
        year = 2000  # Default year if date is missing
    release_years.append(year)

release_years = normalize(release_years)

print(f"Using basic track features for similarity matching...")

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
        
        # Create feature vector from available metadata
        v1 = np.array([track_popularity[curr], track_duration[curr], 
                      track_explicit[curr], release_years[curr]])
        v2 = np.array([track_popularity[i], track_duration[i], 
                      track_explicit[i], release_years[i]])
        
        dist = np.linalg.norm(v1 - v2) + artist_penalty * 0.3
        dists.append((dist, i))
    
    if not dists: break
    
    # Pick the closest track
    dists.sort()
    curr = dists[0][1]

# ------------ GENERATE NEW ORDER -------------
new_order_track_ids = [valid_tracks[i]['track']['id'] for i in ordered]

# ------------ REORDER PLAYLIST -------------
print("Updating playlist order...")
try:
    # Clear playlist first (Spotify API requires this for large playlists)
    sp.playlist_replace_items(con.PLAYLIST_ID, [])
    
    # Add tracks in batches of 100 (Spotify API limit)
    batch_size = 100
    for i in range(0, len(new_order_track_ids), batch_size):
        batch = new_order_track_ids[i:i+batch_size]
        if i == 0:
            # First batch replaces all items
            sp.playlist_replace_items(con.PLAYLIST_ID, batch)
        else:
            # Subsequent batches are added
            sp.playlist_add_items(con.PLAYLIST_ID, batch)
        print(f"Added batch {i//batch_size + 1}/{(len(new_order_track_ids) + batch_size - 1)//batch_size}")
    
    print("Playlist reordered using basic track similarity.")
except Exception as e:
    print(f"Error updating playlist: {e}")