# Spotify FlowScripts

This repository contains configuration files and scripts to automate and enhance your Spotify experience.

## Table of Contents
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Scripts](#scripts)
- [Usage](#usage)

## Getting Started

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/spotify-flowscripts.git
    cd spotify-flowscripts
    ```

2. Install dependencies (if applicable):
    ```bash
    npm install
    ```

## Configuration

The configuration file `config.json` is used to customize the behavior of the scripts. Below is an example configuration:

```json
{
  "spotifyApiKey": "your-spotify-api-key",
  "defaultPlaylist": "My Favorite Songs",
  "logLevel": "info"
}
```

### Fields:
- `spotifyApiKey`: Your Spotify API key for authentication.
- `defaultPlaylist`: The name of the playlist to use by default.
- `logLevel`: The logging level (`info`, `debug`, `error`).

## Scripts

### 1. `create-playlist.js`
Creates a new playlist on your Spotify account.

### 2. `add-to-playlist.js`
Adds a song to a specified playlist.

### 3. `fetch-playlist.js`
Fetches and displays the songs in a playlist.

## Usage

### Example 1: Create a Playlist
Run the `create-playlist.js` script:
```bash
node scripts/create-playlist.js "Chill Vibes"
```

### Example 2: Add a Song to a Playlist
Run the `add-to-playlist.js` script:
```bash
node scripts/add-to-playlist.js "Chill Vibes" "Song Name - Artist"
```

### Example 3: Fetch Playlist Songs
Run the `fetch-playlist.js` script:
```bash
node scripts/fetch-playlist.js "Chill Vibes"
```

## Contributing

Feel free to submit issues or pull requests to improve this project.

## License

This project is licensed under the [MIT License](LICENSE).