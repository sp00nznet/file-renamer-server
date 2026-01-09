# Media Renamer

A bash script that renames movies, TV shows, and music files using online metadata.

**Output formats:**
- Movies: `Movie Name (Year).ext`
- TV Shows: `Show Name - S01E02 - Episode Title.ext`
- Music: `Artist - Track Title.ext`

## Quick Start

1. Install dependencies:
   ```bash
   sudo apt install curl jq   # Debian/Ubuntu
   brew install curl jq       # macOS
   ```

2. Run the interactive launcher:
   ```bash
   ./rename.sh
   ```

   Or run directly:
   ```bash
   # Movies/TV (requires TMDB API key)
   ./file_renamer.sh -k YOUR_API_KEY /path/to/videos

   # Music (no API key needed)
   ./file_renamer.sh -m music /path/to/music
   ```

## Interactive Mode

Run `./rename.sh` for a guided experience:
- Choose media type (Movies, TV Shows, Music, or Auto-detect)
- Select target directory
- Enable dry run to preview changes
- Optionally enable logging

## Command Line Usage

```bash
./file_renamer.sh [options] [directory]
```

| Option | Description |
|--------|-------------|
| `-h` | Show help |
| `-k KEY` | Set TMDB API key (for movies/TV) |
| `-m MODE` | Mode: `movies`, `tv`, `music`, or `auto` |
| `-d` | Dry run (preview only) |
| `-l FILE` | Log operations to file |

**Examples:**
```bash
./file_renamer.sh /path/to/media              # Auto-detect all types
./file_renamer.sh -m movies /path/to/videos   # Movies only
./file_renamer.sh -m tv /path/to/videos       # TV shows only
./file_renamer.sh -m music /path/to/music     # Music only (no API key needed)
./file_renamer.sh -d /path/to/media           # Preview changes
```

## APIs Used

| Media Type | API | API Key Required |
|------------|-----|------------------|
| Movies | TMDB | Yes (free) |
| TV Shows | TMDB | Yes (free) |
| Music | MusicBrainz | No |

Get a free TMDB API key at: https://www.themoviedb.org/settings/api

## Supported Formats

**Video:** mkv, mp4, avi, mov, wmv, flv, webm, m4v, mpg, mpeg, ts, vob

**Audio:** mp3, flac, wav, aac, ogg, wma, m4a, opus, aiff, alac

**TV Patterns:** `S01E02`, `1x02`, `Season.1.Episode.2`

See [DOCUMENTATION.md](DOCUMENTATION.md) for detailed information.

## License

MIT License
