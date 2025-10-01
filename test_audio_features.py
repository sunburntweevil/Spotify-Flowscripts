import spotipy
from spotipy.oauth2 import SpotifyOAuth
import CONFIG as con

try:
    # Initialize the auth manager
    auth_manager = SpotifyOAuth(
        client_id=con.CLIENT_ID,
        client_secret=con.CLIENT_SECRET,
        redirect_uri=con.REDIRECT_URI,
        scope='playlist-modify-public playlist-modify-private playlist-read-private'
    )
    
    # Initialize Spotify client
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # Test with a popular track (this should work if the app has proper permissions)
    test_track_id = '4uLU6hMCjMI75M1A2tKUQC'
    
    print(f"Testing audio features for track ID: {test_track_id}")
    features = sp.audio_features([test_track_id])
    
    if features[0]:
        print("✓ Audio features access successful!")
        print(f"  - Tempo: {features[0]['tempo']}")
        print(f"  - Danceability: {features[0]['danceability']}")
        print(f"  - Energy: {features[0]['energy']}")
    else:
        print("✗ Audio features returned None")
        
except Exception as e:
    print(f"✗ Audio features access failed: {e}")
    print("\nPossible causes:")
    print("1. Your Spotify app is in Development Mode with limited access")
    print("2. Your app doesn't have permission to access audio features")
    print("3. You need to request extended quota mode in Spotify Developer Dashboard")
    print("4. The specific tracks might be region-restricted")