# Media Renamer

A media file renaming tool with both CLI and Web interfaces. Renames movies, TV shows, and music files using online metadata.

**Output formats:**
- Movies: `Movie Name (Year).ext`
- TV Shows: `Show Name - S01E02 - Episode Title.ext`
- Music: `Artist - Track Title.ext`

## Web Application (Docker)

The easiest way to use Media Renamer is through the web interface running in Docker.

### Quick Start with Docker

1. Clone the repository and navigate to it:
   ```bash
   git clone <repository-url>
   cd file-renamer-server
   ```

2. Create a `.env` file (or copy from example):
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and set your configuration:
   ```bash
   TMDB_API_KEY=your_tmdb_api_key_here
   MEDIA_PATH=/path/to/your/media
   SECRET_KEY=your-secret-key-here
   ```

4. Build and run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

5. Access the web interface at: **http://localhost:5000**

### Docker Run (Alternative)

```bash
docker build -t media-renamer .

docker run -d \
  --name media-renamer \
  -p 5000:5000 \
  -e TMDB_API_KEY=your_api_key \
  -v /path/to/your/media:/media \
  media-renamer
```

### Web Interface Features

- **Visual file browser** - Navigate and select directories
- **File scanning** - Automatically detects movies, TV shows, and music
- **Search & match** - Search TMDB/MusicBrainz for correct metadata
- **Preview renames** - See what files will be renamed before applying
- **Batch operations** - Select multiple files and rename at once
- **Dry run mode** - Preview changes without actually renaming

## Command Line Usage

### Install Dependencies

```bash
sudo apt install curl jq   # Debian/Ubuntu
brew install curl jq       # macOS
```

### Interactive Launcher

```bash
./rename.sh
```

### Direct CLI Usage

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

## Project Structure

```
file-renamer-server/
├── app/                    # Flask web application
│   ├── __init__.py         # App factory
│   ├── routes.py           # API endpoints
│   ├── renamer.py          # Core renaming logic
│   ├── static/             # CSS and JavaScript
│   └── templates/          # HTML templates
├── file_renamer.sh         # Original bash script
├── rename.sh               # Interactive CLI launcher
├── run.py                  # Flask entry point
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose config
├── requirements.txt        # Python dependencies
└── .env.example            # Example environment config
```

See [DOCUMENTATION.md](DOCUMENTATION.md) for detailed CLI documentation.

## License

MIT License
