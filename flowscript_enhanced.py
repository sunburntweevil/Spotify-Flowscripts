import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy as np
import math
import CONFIG as con
# ------------ AUTHENTICATION -------------
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=con.CLIENT_ID,
    client_secret=con.CLIENT_SECRET,
    redirect_uri=con.REDIRECT_URI,
    scope='playlist-modify-public playlist-modify-private playlist-read-private'
))

print(" Enhanced Playlist Reordering (Simulated Audio Features)")
print("=" * 60)

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
valid_tracks = [item for item in tracks if item['track'] and item['track']['id'] and not item['track']['is_local']]

print(f" Found {len(tracks)} total tracks, {len(valid_tracks)} are valid Spotify tracks")

if len(valid_tracks) == 0:
    print(" No valid tracks found. Cannot proceed.")
    exit(1)

# ------------ GET DETAILED TRACK INFO -------------
print(" Gathering detailed track information...")

# Get additional details for better feature simulation
track_details = []
for i in range(0, len(valid_tracks), 50):  # Process in batches to avoid rate limits
    batch_ids = [item['track']['id'] for item in valid_tracks[i:i+50]]
    tracks_info = sp.tracks(batch_ids)
    track_details.extend(tracks_info['tracks'])
    print(f"   Processed {min(i+50, len(valid_tracks))}/{len(valid_tracks)} tracks")

# ------------ SIMULATE AUDIO FEATURES -------------
def normalize(arr):
    arr = np.array(arr)
    if arr.max() == arr.min():
        return np.zeros_like(arr)
    return (arr - arr.min()) / (arr.max() - arr.min())

print(" Simulating audio features from available metadata...")

# Simulate TEMPO (BPM) based on duration and popularity
# Shorter, more popular songs tend to be faster
durations = [track['duration_ms'] for track in track_details]
popularities = [track['popularity'] for track in track_details]

simulated_tempo = []
for duration, popularity in zip(durations, popularities):
    # Base tempo calculation: shorter songs = higher tempo
    base_tempo = 200000 / (duration / 1000)  # Inverse relationship
    # Popular songs tend to be more energetic (higher tempo)
    popularity_boost = popularity * 0.5
    # Add some variation based on track position to avoid identical values
    tempo = base_tempo + popularity_boost + np.random.normal(0, 5)
    simulated_tempo.append(max(60, min(200, tempo)))  # Clamp to realistic BPM range

# Simulate KEY based on track name characteristics and artist
simulated_key = []
for i, (item, detail) in enumerate(zip(valid_tracks, track_details)):
    # Use hash of track name + artist to generate consistent key
    track_hash = hash(detail['name'] + detail['artists'][0]['name']) % 12
    simulated_key.append(track_hash)

# Simulate DANCEABILITY based on popularity and genre indicators
simulated_danceability = []
for detail in track_details:
    # Base danceability on popularity (popular songs often more danceable)
    base_dance = detail['popularity'] / 100.0
    
    # Analyze track name for dance-related keywords
    name_lower = detail['name'].lower()
    dance_keywords = ['dance', 'groove', 'beat', 'rhythm', 'party', 'club', 'remix', 'mix']
    keyword_boost = sum(0.1 for keyword in dance_keywords if keyword in name_lower)
    
    # Energy-related keywords suggest higher danceability
    energy_keywords = ['energy', 'power', 'pump', 'bounce', 'drop', 'bass']
    energy_boost = sum(0.05 for keyword in energy_keywords if keyword in name_lower)
    
    danceability = min(1.0, base_dance + keyword_boost + energy_boost + np.random.normal(0, 0.1))
    simulated_danceability.append(max(0.0, danceability))

# Simulate VALENCE (happiness) based on track name and explicit content
simulated_valence = []
for detail in track_details:
    # Start with neutral valence
    base_valence = 0.5
    
    # Happy/positive keywords increase valence
    happy_keywords = ['love', 'happy', 'joy', 'good', 'great', 'amazing', 'beautiful', 
                     'wonderful', 'fantastic', 'awesome', 'perfect', 'best']
    happy_boost = sum(0.05 for keyword in happy_keywords if keyword in detail['name'].lower())
    
    # Sad/negative keywords decrease valence
    sad_keywords = ['sad', 'cry', 'pain', 'hurt', 'broken', 'lost', 'alone', 'dark', 
                   'death', 'end', 'goodbye', 'farewell', 'miss', 'sorry']
    sad_penalty = sum(0.05 for keyword in sad_keywords if keyword in detail['name'].lower())
    
    # Explicit content might be less positive on average
    explicit_penalty = 0.1 if detail['explicit'] else 0.0
    
    valence = base_valence + happy_boost - sad_penalty - explicit_penalty + np.random.normal(0, 0.1)
    simulated_valence.append(max(0.0, min(1.0, valence)))

# Simulate LOUDNESS based on popularity and energy indicators
simulated_loudness = []
for detail in track_details:
    # Popular songs tend to be louder (mastered for radio)
    base_loudness = -60 + (detail['popularity'] * 0.5)  # dB range roughly -60 to -10
    
    # Rock/metal/electronic keywords suggest louder tracks
    loud_keywords = ['rock', 'metal', 'electronic', 'edm', 'house', 'techno', 'loud', 
                    'scream', 'shout', 'bang', 'crash', 'thunder']
    loud_boost = sum(2 for keyword in loud_keywords if keyword in detail['name'].lower())
    
    # Acoustic/quiet keywords suggest quieter tracks
    quiet_keywords = ['acoustic', 'quiet', 'soft', 'gentle', 'whisper', 'calm', 'peaceful']
    quiet_penalty = sum(3 for keyword in quiet_keywords if keyword in detail['name'].lower())
    
    loudness = base_loudness + loud_boost - quiet_penalty + np.random.normal(0, 2)
    simulated_loudness.append(max(-60, min(-3, loudness)))

# Normalize all simulated features
bpm = normalize(simulated_tempo)
key = normalize(simulated_key)
danceability = normalize(simulated_danceability)
valence = normalize(simulated_valence)
loudness = normalize(simulated_loudness)

# Get artists for diversity
artists = [item['track']['artists'][0]['id'] for item in valid_tracks]

print(f" Generated simulated audio features:")
print(f"    Tempo (BPM): {min(simulated_tempo):.0f} - {max(simulated_tempo):.0f}")
print(f"    Key: 0-11 (musical keys)")
print(f"    Danceability: {min(simulated_danceability):.2f} - {max(simulated_danceability):.2f}")
print(f"    Valence (happiness): {min(simulated_valence):.2f} - {max(simulated_valence):.2f}")
print(f"    Loudness: {min(simulated_loudness):.1f} - {max(simulated_loudness):.1f} dB")

# ------------ SMOOTH SEQUENCING BY AUDIO FEATURES -------------
print("\n Ordering tracks by tempo, key, danceability, valence, and loudness...")

ordered = []
used = set()
curr = 0  # Start from first track

while len(ordered) < len(valid_tracks):
    ordered.append(curr)
    used.add(curr)
    
    # Find the most similar remaining track
    best_dist = float('inf')
    best_next = None
    
    for i in range(len(valid_tracks)):
        if i in used:
            continue
        
        # Penalize same artist to encourage diversity
        artist_penalty = 1.0 if artists[i] == artists[curr] else 0.0
        
        # Create feature vector using your requested features
        v1 = np.array([bpm[curr], key[curr], danceability[curr], valence[curr], loudness[curr]])
        v2 = np.array([bpm[i], key[i], danceability[i], valence[i], loudness[i]])
        
        # Calculate Euclidean distance + artist penalty
        dist = np.linalg.norm(v1 - v2) + artist_penalty * 0.3
        
        if dist < best_dist:
            best_dist = dist
            best_next = i
    
    if best_next is not None:
        curr = best_next
    else:
        break

# ------------ REORDER PLAYLIST -------------
track_ids = [item['track']['id'] for item in valid_tracks]
new_order_track_ids = [track_ids[i] for i in ordered]

print(f"\nGenerated smooth track order using simulated features")
print("Updating playlist...")

try:
    # Handle Spotify's batch size limit
    if len(new_order_track_ids) <= 100:
        sp.playlist_replace_items(con.PLAYLIST_ID, new_order_track_ids)
    else:
        # Clear and rebuild in batches
        sp.playlist_replace_items(con.PLAYLIST_ID, [])
        
        batch_size = 100
        for i in range(0, len(new_order_track_ids), batch_size):
            batch = new_order_track_ids[i:i+batch_size]
            if i == 0:
                sp.playlist_replace_items(con.PLAYLIST_ID, batch)
            else:
                sp.playlist_add_items(con.PLAYLIST_ID, batch)
            print(f"   Added batch {i//batch_size + 1}/{(len(new_order_track_ids) + batch_size - 1)//batch_size}")
    
    print("\n Playlist reordered by simulated tempo, key, danceability, valence, and loudness")
    
except Exception as e:
    print(f"Error updating playlist: {e}")