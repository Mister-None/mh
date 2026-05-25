# OpusDB Manager
OpusDB Manager is a powerful Python utility for managing, identifying, and organizing large collections of `.opus` audio files. It integrates a SQLite backend with audio recognition technology to keep your music library clean, tagged, and easily playable.

## Features
The script provides a multi-functional CLI interface:
- **Automatic Recognition:** Uses `SongRec` (Shazam API) to identify tracks and fetch metadata (Artist, Title, Genre, Album, etc.).
- **Database Management:** Maintains a SQLite database for fast searching and filtering.
- **Smart Cleanup:** Removes metadata from files to maintain a "clean" local state and deletes duplicate tracks based on Artist/Title matching.
- **Interactive Playback:** Search and play music by Artist, Genre, Title, or Year using `mpv`.
- **Playlist Generation:** Automatically creates `.m3u8` playlists based on genres.
- **Batch Processing:** Normalize database strings or update existing metadata for specific tracks.
- **Excel Integration:** Import track lists from external Excel spreadsheets.

## Prerequisites

### System Dependencies
This script is designed for Linux-based systems. You must have the following tools installed:
- [FFmpeg](https://ffmpeg.org/): For audio processing and metadata stripping.
- [SongRec](https://github.com/marin-m/SongRec): CLI Shazam client for track recognition.
- [mpv](https://mpv.io/): For audio playback.

### Python Libraries
1. Install the required Python packages:
```bash
pip install requests pandas moviepy python-dotenv colorama tqdm openpyxl
```
2. Use `ms_data_template.db` for storing data about track

## Usage
For listing options run:
```bash
python mh_bot.py
#output
1 ==> add to base
2 ==> clean metadata
3 ==> play by arist/title/genre/year
4 ==> normalize
5 ==> remove duplicactes
6 ==> update base
7 ==> remove from base
8 ==> create playlists
9 ==> add specific base
```
