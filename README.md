# Media Renamer

A web-based media file renaming tool running in Docker. Renames movies, TV shows, and music files using online metadata.

**Output formats:**
- Movies: `Movie Name (Year).ext`
- TV Shows: `Show Name - S01E02 - Episode Title.ext`
- Music: `Artist - Track Title.ext`

## Quick Start with Docker

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd file-renamer-server
   ```

2. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and set your configuration:
   ```bash
   TMDB_API_KEY=your_tmdb_api_key_here
   MEDIA_PATH=/path/to/your/media
   SECRET_KEY=your-secret-key-here
   ```

4. Build and run:
   ```bash
   docker-compose up -d
   ```

5. Access the web interface at: **http://localhost:5000**

## Docker Run (Alternative)

```bash
docker build -t media-renamer .

docker run -d \
  --name media-renamer \
  -p 5000:5000 \
  -e TMDB_API_KEY=your_api_key \
  -v /path/to/your/media:/media \
  media-renamer
```

## Features

- **Visual file browser** - Navigate and select directories
- **File scanning** - Automatically detects movies, TV shows, and music
- **Search & match** - Search TMDB/MusicBrainz for correct metadata
- **Preview renames** - See what files will be renamed before applying
- **Batch operations** - Select multiple files and rename at once
- **Dry run mode** - Preview changes without actually renaming

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
├── run.py                  # Flask entry point
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose config
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment config
└── archive/                # Original CLI scripts (deprecated)
```

## License

MIT License
