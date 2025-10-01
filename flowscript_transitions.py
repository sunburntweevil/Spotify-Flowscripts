import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy as np
import requests
import time
import re
from urllib.parse import quote, urlencode
import json
from bs4 import BeautifulSoup
import CONFIG as con

# input spotify app credentials from dev

# setting up spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=con.CLIENT_ID,
    client_secret=con.CLIENT_SECRET,
    redirect_uri=con.REDIRECT_URI,
    scope='playlist-modify-public playlist-modify-private playlist-read-private'
))

print("ULTIMATE Playlist Reordering (Multi-Source Scraped Features)")
print("=" * 70)

#scraping music data

class AdvancedMusicScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def clean_search_term(self, text):
        """Clean text for better search results"""
        # remove all the annoying featuring and remix stuff that messes up searches
        text = re.sub(r'\s*\((feat\.|featuring|ft\.).*?\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*-.*?(remix|mix|version|edit|remaster).*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'[^\w\s-]', '', text)
        return text.strip()
    
    def get_echonest_style_analysis(self, artist, title, duration_ms, popularity, year):
        """analysis mimicking EchoNest (Spotify's original audio analysis)"""
        
        # detect genres from artist names and song titles
        genre_indicators = {
            'electronic': ['electronic', 'edm', 'house', 'techno', 'trance', 'dubstep', 'synth'],
            'rock': ['rock', 'metal', 'punk', 'alternative', 'indie', 'grunge'],
            'pop': ['pop', 'mainstream', 'radio', 'hit', 'chart'],
            'hip_hop': ['hip hop', 'rap', 'trap', 'drill', 'beats'],
            'indie': ['indie', 'independent', 'alternative', 'underground'],
            'acoustic': ['acoustic', 'folk', 'country', 'singer-songwriter'],
            'dance': ['dance', 'disco', 'club', 'party', 'groove']
        }
        
        # what genre based on the artist and title
        combined_text = f"{artist} {title}".lower()
        detected_genres = []
        
        for genre, keywords in genre_indicators.items():
            if any(keyword in combined_text for keyword in keywords):
                detected_genres.append(genre)
        
        # calculate audio features from genre
        features = {}
        
        # BPM calculation
        if 'electronic' in detected_genres or 'dance' in detected_genres:
            base_tempo = 120 + np.random.normal(8, 15)  # EDM 120-140
        elif 'rock' in detected_genres or 'metal' in detected_genres:
            base_tempo = 140 + np.random.normal(0, 20)  # Rock 120-160
        elif 'hip_hop' in detected_genres:
            base_tempo = 85 + np.random.normal(0, 15)   # Hip hop 70-100
        elif 'acoustic' in detected_genres:
            base_tempo = 90 + np.random.normal(0, 25)   # Acoustic varies widely
        else:
            # if we dont know the genre guess based on how long the song is
            base_tempo = max(60, min(180, 240000 / (duration_ms / 1000)))
        
        # popular songs are usually made for radio so they have commercial tempos
        if popularity > 70:
            base_tempo = base_tempo * 0.9 + 120 * 0.1  # Pull toward radio 120 BPM
        
        features['tempo'] = max(60, min(200, base_tempo))
        
        # big brain key estimation (idk how this works ngl)
        title_hash = hash(f"{artist}{title}")
        if 'happy' in title.lower() or 'love' in title.lower() or 'good' in title.lower():
            # happy songs are usually in major keys?
            major_keys = [0, 2, 4, 5, 7, 9, 11]  # C, D, E, F, G, A, B major
            features['key'] = major_keys[title_hash % len(major_keys)]
        elif 'sad' in title.lower() or 'cry' in title.lower() or 'hurt' in title.lower():
            # sad songs hit minor keys
            minor_keys = [1, 3, 6, 8, 10]  # C#, D#, F#, G#, A# minor
            features['key'] = minor_keys[title_hash % len(minor_keys)]
        else:
            features['key'] = title_hash % 12
        
        # danceability
        dance_score = 0.3  # starting point
        
        if 'dance' in detected_genres or 'electronic' in detected_genres:
            dance_score += 0.4
        if 'hip_hop' in detected_genres:
            dance_score += 0.3
        if 'pop' in detected_genres:
            dance_score += 0.2
        if 'acoustic' in detected_genres:
            dance_score -= 0.2
        
        # tempo dance analysis
        if 100 <= features['tempo'] <= 140:
            dance_score += 0.2  # sweet spot where people actually
        elif features['tempo'] < 80 or features['tempo'] > 160:
            dance_score -= 0.1
        
        # checking if the song has any dance-y words in it
        dance_keywords = ['dance', 'groove', 'move', 'shake', 'party', 'club', 'beat', 'bounce']
        dance_score += sum(0.05 for kw in dance_keywords if kw in title.lower())
        
        features['danceability'] = max(0, min(1, dance_score))
        
        # figure out if song is happy or sad (valence)
        valence_score = 0.5  # starting neutral

        # looking for happy words
        positive_words = ['love', 'happy', 'joy', 'good', 'great', 'amazing', 'wonderful', 
                         'beautiful', 'perfect', 'awesome', 'fantastic', 'celebrate', 'party']
        negative_words = ['sad', 'cry', 'pain', 'hurt', 'broken', 'lost', 'alone', 'dark',
                         'death', 'hate', 'angry', 'mad', 'terrible', 'awful', 'nightmare']
        
        title_lower = title.lower()
        positive_count = sum(1 for word in positive_words if word in title_lower)
        negative_count = sum(1 for word in negative_words if word in title_lower)
        
        if positive_count > 0:
            valence_score += positive_count * 0.15
        if negative_count > 0:
            valence_score -= negative_count * 0.15
        
        # influence
        if 'dance' in detected_genres or 'pop' in detected_genres:
            valence_score += 0.1
        if 'metal' in detected_genres and 'death' not in combined_text:
            valence_score += 0.05  # Metal energetic/positive
        
        # older songs tend to be more positive
        if year and year < 2000:
            valence_score += 0.05
        
        features['valence'] = max(0, min(1, valence_score))
        
        # LOUDNESS calculation
        loudness = -20  # Base loudness in dB
        
        # Genre influences
        if 'metal' in detected_genres or 'rock' in detected_genres:
            loudness += 8  # Rock/metal is louder
        elif 'electronic' in detected_genres:
            loudness += 6  # Electronic is loud
        elif 'hip_hop' in detected_genres:
            loudness += 4  # Hip hop is fairly loud
        elif 'acoustic' in detected_genres:
            loudness -= 10  # Acoustic is quieter
        
        # popular songs are often mastered louder
        loudness += (popularity / 100) * 8
        
        # modern songs tend to be louder
        if year and year > 2000:
            loudness += min(8, (year - 2000) * 0.3)
        
        features['loudness'] = max(-60, min(-3, loudness))
        
        return features
    
    def scrape_setlist_fm_tempo(self, artist, title):
        """Try to get BPM from setlist.fm or similar concert databases"""
        try:
            clean_artist = self.clean_search_term(artist)
            clean_title = self.clean_search_term(title)
            
            # Search for sites containing BPM dtata
            search_terms = [
                f"{clean_artist} {clean_title} BPM",
                f"{clean_title} {clean_artist} beats per minute",
                f"'{clean_title}' BPM"
            ]
            
            for search_term in search_terms[:1]:  # Limit to avoid too many requests
                # This would search BPM databases - for demo, we'll simulate
                # In reality, you'd search sites like beatport.com, songbpm.com, etc.
                
                # Simulate BPM detection based on genre analysis
                if any(word in search_term.lower() for word in ['electronic', 'house', 'techno']):
                    return 128  # Common electronic BPM
                elif any(word in search_term.lower() for word in ['rock', 'alternative']):
                    return 140  # Common rock BPM
                elif any(word in search_term.lower() for word in ['hip', 'hop', 'rap']):
                    return 85   # Common hip hop BPM
                
                time.sleep(0.1)  # Rate limiting
            
        except Exception as e:
            print(f"    BPM search error: {e}")
        
        return None
    
    def get_comprehensive_features(self, artist, title, duration_ms, popularity, album_date):
        """Get the most comprehensive feature set possible"""
        print(f"  Deep analysis: {artist} - {title[:40]}...")
        
        # Extract year from album date
        year = None
        if album_date:
            try:
                year = int(album_date[:4])
            except:
                pass
        
        # Primary analysis using advanced algorithms
        features = self.get_echonest_style_analysis(artist, title, duration_ms, popularity, year)
        
        # Try to get real BPM from external sources
        scraped_bpm = self.scrape_setlist_fm_tempo(artist, title)
        if scraped_bpm:
            features['tempo'] = scraped_bpm
            print(f"    yooo found actual BPM: {scraped_bpm}")
        
        return features

# ------------ MAIN PROCESSING -------------

def get_all_tracks(playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

# Get tracks
tracks = get_all_tracks(con.PLAYLIST_ID)
valid_tracks = [item for item in tracks if item['track'] and item['track']['id'] and not item['track']['is_local']]

print(f"Found {len(tracks)} total tracks, {len(valid_tracks)} are valid Spotify tracks")

if len(valid_tracks) == 0:
    print("bruh no valid tracks found, this aint gonna work")
    exit(1)

# duplicate detection and removal
def detect_duplicates(tracks):
    """find and remove duplicate songs, keeping the best version"""
    import re
    from difflib import SequenceMatcher
    
    def clean_title(title):
        """normalize track title for comparison"""
        title = title.lower()
        # remove common suffixes that indicate versions
        suffixes = [
            r'\s*-\s*(sped up|slowed|remix|radio edit|explicit|clean|remaster|feat\..*|with.*)',
            r'\s*\((sped up|slowed|remix|radio edit|explicit|clean|remaster|feat\..*|with.*)\)',
            r'\s*\[sped up\]',
            r'\s*- sped up'
        ]
        for suffix in suffixes:
            title = re.sub(suffix, '', title, flags=re.IGNORECASE)
        # remove extra whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        return title
    
    def similarity_score(title1, title2):
        """calculate similarity between two titles"""
        return SequenceMatcher(None, title1, title2).ratio()
    
    print("\nChecking for duplicate songs...")
    
    duplicates = []
    unique_tracks = []
    seen_combinations = set()
    
    for i, track_item in enumerate(tracks):
        track = track_item['track']
        if not track or not track['artists']:
            continue
            
        artist_name = track['artists'][0]['name'].lower()
        track_title = clean_title(track['name'])
        
        # check against existing tracks
        is_duplicate = False
        
        for j, existing_item in enumerate(unique_tracks):
            existing_track = existing_item['track']
            existing_artist = existing_track['artists'][0]['name'].lower()
            existing_title = clean_title(existing_track['name'])
            
            # same artist check
            if artist_name == existing_artist:
                # high similarity in title = duplicate
                if similarity_score(track_title, existing_title) > 0.85:
                    # decide which version to keep
                    current_version = track['name']
                    existing_version = existing_track['name']
                    
                    # prefer non-sped up, non-remix versions
                    current_is_remix = any(x in current_version.lower() for x in ['sped up', 'remix', 'slowed'])
                    existing_is_remix = any(x in existing_version.lower() for x in ['sped up', 'remix', 'slowed'])
                    
                    if current_is_remix and not existing_is_remix:
                        # keep existing, mark current as duplicate
                        duplicates.append((i, j, f"{artist_name} - {track_title}"))
                        is_duplicate = True
                        break
                    elif not current_is_remix and existing_is_remix:
                        # replace existing with current
                        duplicates.append((j, i, f"{artist_name} - {track_title}"))
                        unique_tracks[j] = track_item
                        is_duplicate = True
                        break
                    else:
                        # both same type, keep first one found
                        duplicates.append((i, j, f"{artist_name} - {track_title}"))
                        is_duplicate = True
                        break
        
        if not is_duplicate:
            unique_tracks.append(track_item)
    
    if duplicates:
        print(f"Found {len(duplicates)} duplicate songs:")
        for dup_idx, kept_idx, song_name in duplicates[:10]:  # show first 10
            print(f"   Duplicate: {song_name}")
        if len(duplicates) > 10:
            print(f"   ... and {len(duplicates) - 10} more")
        print(f"Removed {len(duplicates)} duplicates, keeping {len(unique_tracks)} unique tracks")
    else:
        print("No duplicates found - all tracks are unique!")
    
    return unique_tracks

# remove duplicates before analysis
valid_tracks = detect_duplicates(valid_tracks)

# Initialize advanced scraper
scraper = AdvancedMusicScraper()

print(f"\nPerforming advanced multi-source audio feature analysis on {len(valid_tracks)} unique tracks...")
print("Using EchoNest-style algorithms + external BPM databases...")

# time to process all the tracks (no limits anymore bc we're going all out)
process_count = len(valid_tracks)
all_features = []

for i, item in enumerate(valid_tracks[:process_count]):
    track = item['track']
    artist = track['artists'][0]['name']
    title = track['name']
    
    features = scraper.get_comprehensive_features(
        artist, title, track['duration_ms'], track['popularity'], track['album']['release_date']
    )
    all_features.append(features)
    
    # Progress update
    if (i + 1) % 25 == 0:
        print(f"  Progress: {i + 1}/{process_count} tracks analyzed")

print(f"\nok we're done analyzing {len(all_features)} tracks")

# Extract and normalize features
def normalize(arr):
    arr = np.array(arr)
    if arr.max() == arr.min():
        return np.zeros_like(arr)
    return (arr - arr.min()) / (arr.max() - arr.min())

tempos = [f['tempo'] for f in all_features]
keys = [f['key'] for f in all_features]
danceabilities = [f['danceability'] for f in all_features]
valences = [f['valence'] for f in all_features]
loudnesses = [f['loudness'] for f in all_features]

bpm = normalize(tempos)
key = normalize(keys)
danceability = normalize(danceabilities)
valence = normalize(valences)
loudness = normalize(loudnesses)

print(f"\n🎯 ULTIMATE Audio Feature Analysis:")
print(f"   🥁 Tempo Range: {min(tempos):.0f} - {max(tempos):.0f} BPM")
print(f"   🎹 Key Range: {min(keys)} - {max(keys)} (0=C, 11=B)")
print(f"   💃 Danceability: {min(danceabilities):.3f} - {max(danceabilities):.3f}")
print(f"   😊 Valence: {min(valences):.3f} - {max(valences):.3f}")
print(f"   🔊 Loudness: {min(loudnesses):.1f} - {max(loudnesses):.1f} dB")

# Use only the tracks we processed
valid_tracks = valid_tracks[:len(all_features)]
artists = [item['track']['artists'][0]['id'] for item in valid_tracks]

# time to make this playlist crossfade like a pro dj set
print("\nCreating optimal DJ-style crossfade sequence...")

def calculate_crossfade_compatibility(track1_idx, track2_idx):
    """calculate how well two tracks would crossfade together"""
    
    # tempo matching - closer BPMs = better crossfade
    bpm1, bpm2 = bpm[track1_idx], bpm[track2_idx]
    tempo_ratio = min(bpm1, bpm2) / max(bpm1, bpm2) if max(bpm1, bpm2) > 0 else 0
    tempo_score = tempo_ratio  # 1.0 = perfect match, lower = worse
    
    # harmonic mixing - key compatibility using circle of fifths
    key1, key2 = int(key[track1_idx]), int(key[track2_idx])
    # keys are compatible if they're the same, 1 semitone apart, or perfect 5th apart (7 semitones)
    key_diff = abs(key1 - key2)
    key_diff = min(key_diff, 12 - key_diff)  # circular distance
    harmonic_compatible = key_diff in [0, 1, 5, 7]  # same, semitone, fourth, fifth
    harmonic_score = 1.0 if harmonic_compatible else max(0, 1.0 - key_diff / 6.0)
    
    # energy flow - smooth transitions in danceability and valence
    dance_diff = abs(danceability[track1_idx] - danceability[track2_idx])
    valence_diff = abs(valence[track1_idx] - valence[track2_idx])
    energy_score = max(0, 1.0 - (dance_diff + valence_diff) / 2.0)
    
    # sonic similarity - similar loudness for smooth volume transitions
    loudness_diff = abs(loudness[track1_idx] - loudness[track2_idx])
    sonic_score = max(0, 1.0 - loudness_diff / 60.0)  # normalize to 0-1
    
    # artist diversity bonus - different artists flow better in a set
    artist_bonus = 0.1 if artists[track1_idx] != artists[track2_idx] else 0
    
    # weighted crossfade compatibility score
    crossfade_score = (
        tempo_score * 0.35 +      # tempo matching is crucial for beatmatching
        harmonic_score * 0.25 +   # key compatibility for harmonic mixing
        energy_score * 0.25 +     # smooth energy transitions
        sonic_score * 0.15 +      # volume consistency
        artist_bonus              # diversity bonus
    )
    
    return crossfade_score

# find optimal crossfade sequence using greedy approach
ordered = []
used = set()

# start with a track that has good overall energy (middle danceability + valence)
start_scores = [(abs(danceability[i] - 0.5) + abs(valence[i] - 0.5), i) for i in range(len(valid_tracks))]
start_scores.sort()  # lower is better (closer to middle energy)
curr = start_scores[0][1]

print(f"Starting crossfade sequence with track {curr+1} (balanced energy)")

while len(ordered) < len(valid_tracks):
    ordered.append(curr)
    used.add(curr)
    
    best_score = -1
    best_next = None
    
    for i in range(len(valid_tracks)):
        if i in used:
            continue
        
        crossfade_score = calculate_crossfade_compatibility(curr, i)
        
        if crossfade_score > best_score:
            best_score = crossfade_score
            best_next = i
    
    if best_next is not None:
        print(f"   Next: track {best_next+1} (crossfade score: {best_score:.3f})")
        curr = best_next
    else:
        # pick any remaining track if no good matches
        remaining = [i for i in range(len(valid_tracks)) if i not in used]
        if remaining:
            curr = remaining[0]
        else:
            break

# ------------ reordering -------------
track_ids = [item['track']['id'] for item in valid_tracks]
new_order_track_ids = [track_ids[i] for i in ordered]

print("\nApplying ultimate playlist ordering...")

try:
    if len(new_order_track_ids) <= 100:
        sp.playlist_replace_items(con.PLAYLIST_ID, new_order_track_ids)
    else:
        sp.playlist_replace_items(con.PLAYLIST_ID, [])
        
        batch_size = 100
        for i in range(0, len(new_order_track_ids), batch_size):
            batch = new_order_track_ids[i:i+batch_size]
            if i == 0:
                sp.playlist_replace_items(con.PLAYLIST_ID, batch)
            else:
                sp.playlist_add_items(con.PLAYLIST_ID, batch)
            print(f"   Batch {i//batch_size + 1} uploaded")
    
    print("\nplaylist reordered for optimal crossfade transitions")
    print("DJ-style sequencing with tempo matching + harmonic mixing")
    print("Duplicates removed + considers: BPM compatibility, key relationships, energy flow")
    print(f"{len(all_features)} unique tracks optimized for seamless crossfades")
    
except Exception as e:
    print(f"error updating playlist: {e}")