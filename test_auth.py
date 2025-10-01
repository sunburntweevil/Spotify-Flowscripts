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
    
    # Test basic API access
    print("Attempting to get user profile...")
    user_info = sp.current_user()
    print(f"✓ Authentication successful! User: {user_info['display_name']} (ID: {user_info['id']})")
    
    # Test playlist access
    print("Testing playlist access...")
    playlist_id = '1nrAKakBdaq6bZbZ9jMjBx'
    playlist = sp.playlist(playlist_id)
    print(f"✓ Playlist access successful: {playlist['name']}")
    
except Exception as e:
    print(f"✗ Authentication failed: {e}")
    print("\nPossible issues:")
    print("1. Invalid Client ID or Client Secret")
    print("2. App not properly configured in Spotify Developer Dashboard") 
    print("3. Redirect URI mismatch")
    print("4. Missing required scopes")