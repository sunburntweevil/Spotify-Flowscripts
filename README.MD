# Spotify FlowScripts

This repository contains Python scripts to intelligently reorder Spotify playlists using various audio analysis algorithms and flow optimization techniques.

## Table of Contents
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Scripts](#scripts)
- [Usage](#usage)
- [Requirements](#requirements)

## Getting Started

1. Clone the repository:
    ```bash
    git clone https://github.com/sunburntweevil/Spotify-Flowscripts.git
    cd Spotify-Flowscripts/flowscripts
    ```

2. Install Python dependencies:
    ```bash
    pip install spotipy numpy requests beautifulsoup4
    ```

3. Set up Spotify API credentials (see Configuration section below)

## Requirements

- Python 3.6+
- spotipy
- numpy
- requests
- beautifulsoup4

## Configuration

The configuration is handled in `CONFIG.py`. You'll need to set up your Spotify API credentials:

```python
# Get these from https://developer.spotify.com/
CLIENT_ID = 'your-spotify-client-id'
CLIENT_SECRET = 'your-spotify-client-secret'

# Must match the redirect URI in your Spotify app settings
REDIRECT_URI = 'http://127.0.0.1:8888/callback'

# Get from your Spotify playlist URL: https://open.spotify.com/playlist/[PLAYLIST_ID]
PLAYLIST_ID = 'your-playlist-id-from-spotify-url'
```

### Setup Steps:
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/)
2. Create a new app
3. Copy your Client ID and Client Secret to `CONFIG.py`
4. Set redirect URI to `http://127.0.0.1:8888/callback` in your app settings
5. Get your playlist ID from any Spotify playlist URL
**⚠ WARNING: DO NOT COMMIT YOUR SPOTIFY API CONFIG FILE TO GITHUB. It contains sensitive credentials that can be exploited maliciously.**

### 1. `flowscript_basic.py`
Basic playlist reordering using simple audio feature analysis and flow optimization.

### 2. `flowscript_enhanced.py`
Enhanced playlist reordering with simulated advanced audio features and improved algorithms.

### 3. `flowscript_transitions.py`
Ultimate playlist reordering using multi-source scraped music data for superior flow transitions.

### 4. `test_auth.py`
Test script to verify your Spotify API authentication is working correctly.

### 5. `test_audio_features.py`
Test script to verify audio feature retrieval from Spotify API.

## Usage

### Example 1: Test Authentication
Before running any playlist scripts, test your authentication:
```bash
python test_auth.py
```

### Example 2: Basic Playlist Reordering
Run the basic flow optimization:
```bash
python flowscript_basic.py
```

### Example 3: Enhanced Playlist Reordering
Run the enhanced algorithm with simulated features:
```bash
python flowscript_enhanced.py
```

### Example 4: Ultimate Playlist Reordering
Run the most advanced algorithm with scraped music data:
```bash
python flowscript_transitions.py
```

### Example 5: Test Audio Features
Verify audio feature retrieval is working:
```bash
python test_audio_features.py
```

## How It Works

The scripts analyze your Spotify playlist and reorder tracks to create better "flow" by:
- Analyzing audio features (tempo, energy, valence, danceability, etc.)
- Calculating optimal transitions between songs
- Minimizing jarring changes in musical characteristics
- Creating smooth progressions throughout the playlist

Each script uses increasingly sophisticated algorithms:
- **Basic**: Simple audio feature analysis
- **Enhanced**: Advanced simulated features and improved algorithms  
- **Transitions**: Multi-source data scraping for ultimate optimization

## Contributing

Feel free to submit issues or pull requests to improve this project.

## License

This project is licensed under the [MIT License](LICENSE).