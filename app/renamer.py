"""
Media Renamer - Core Logic
Adapted from file_renamer.sh for web interface
"""

import os
import re
import time
import urllib.parse
import requests

# File extensions
VIDEO_EXTENSIONS = {'mkv', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'm4v',
                    'mpg', 'mpeg', 'ts', 'vob', 'divx', 'xvid'}
AUDIO_EXTENSIONS = {'mp3', 'flac', 'wav', 'aac', 'ogg', 'wma', 'm4a',
                    'opus', 'aiff', 'alac'}


def get_extension(filename):
    """Get file extension in lowercase."""
    return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''


def is_video_file(filename):
    """Check if file is a video file."""
    return get_extension(filename) in VIDEO_EXTENSIONS


def is_audio_file(filename):
    """Check if file is an audio file."""
    return get_extension(filename) in AUDIO_EXTENSIONS


def detect_tv_show(filename):
    """
    Detect if a filename is a TV show and extract season/episode info.
    Returns dict with show_name, season, episode or None if not a TV show.
    """
    name = os.path.splitext(filename)[0]

    # Pattern 1: S01E02 format (most common)
    match = re.search(r'[Ss](\d{1,2})[Ee](\d{1,2})', name)
    if match:
        season = match.group(1)
        episode = match.group(2)
        show_name = re.sub(r'[._-]?[Ss]\d{1,2}[Ee]\d{1,2}.*', '', name)
        show_name = re.sub(r'[._-]+', ' ', show_name).strip()
        return {'show_name': show_name, 'season': season, 'episode': episode}

    # Pattern 2: 1x02 format
    match = re.search(r'(\d{1,2})x(\d{1,2})', name)
    if match:
        season = match.group(1)
        episode = match.group(2)
        show_name = re.sub(r'[._-]?\d{1,2}x\d{1,2}.*', '', name)
        show_name = re.sub(r'[._-]+', ' ', show_name).strip()
        return {'show_name': show_name, 'season': season, 'episode': episode}

    # Pattern 3: Season 1 Episode 2 format
    match = re.search(r'[Ss]eason[._\s-]?(\d{1,2})[._\s-]?[Ee]pisode[._\s-]?(\d{1,2})', name)
    if match:
        season = match.group(1)
        episode = match.group(2)
        show_name = re.sub(r'[._-]?[Ss]eason.*', '', name, flags=re.IGNORECASE)
        show_name = re.sub(r'[._-]+', ' ', show_name).strip()
        return {'show_name': show_name, 'season': season, 'episode': episode}

    return None


def clean_movie_name(filename):
    """Extract searchable movie name from filename."""
    name = os.path.splitext(filename)[0]

    # Replace common separators with spaces
    name = re.sub(r'[._-]+', ' ', name)

    # Extract year if present
    year_match = re.search(r'\b(19|20)\d{2}\b', name)
    year = year_match.group(0) if year_match else None

    # Remove quality indicators
    patterns = [
        r'\b(720p|1080p|2160p|4k|uhd|hdr)\b',
        r'\b(bluray|brrip|bdrip|dvdrip|webrip|web-dl|webdl|hdtv)\b',
        r'\b(xvid|divx|x264|x265|h264|h265|hevc)\b',
        r'\b(aac|ac3|dts|5\.1|7\.1)\b',
        r'\b(proper|repack|extended|unrated|directors\s*cut|theatrical|remastered)\b',
        r'\b(yify|yts|rarbg|eztv|ettv|sparks|axxo|fgt|ctrlhd|ntb|mtb|publichd)\b',
    ]

    for pattern in patterns:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)

    # Remove year from search string (will use separately)
    if year:
        name = re.sub(r'\b' + year + r'\b', '', name)

    # Clean up whitespace
    name = re.sub(r'\s+', ' ', name).strip()

    return {'name': name, 'year': year}


def clean_show_name(name):
    """Clean a TV show name for searching."""
    # Replace common separators with spaces
    name = re.sub(r'[._-]+', ' ', name)

    # Remove year in parentheses/brackets
    name = re.sub(r'\([0-9]{4}\)', '', name)
    name = re.sub(r'\[[0-9]{4}\]', '', name)

    # Remove quality indicators
    patterns = [
        r'\b(720p|1080p|2160p|4k|uhd|hdr)\b',
        r'\b(bluray|brrip|bdrip|dvdrip|webrip|web-dl|webdl|hdtv)\b',
        r'\b(xvid|divx|x264|x265|h264|h265|hevc)\b',
        r'\b(aac|ac3|dts|5\.1|7\.1|proper|repack)\b',
    ]

    for pattern in patterns:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)

    # Remove common group names
    name = re.sub(r'\s+(yify|yts|rarbg|eztv|ettv|sparks|axxo|fgt|ctrlhd|ntb|mtb|publichd|lol|dimension|fleet|killers|fov|bamboozle).*$', '', name, flags=re.IGNORECASE)

    # Clean up whitespace
    name = re.sub(r'\s+', ' ', name).strip()

    return name


def clean_music_filename(filename):
    """Extract artist and track info from music filename."""
    name = os.path.splitext(filename)[0]

    # Replace common separators with spaces
    name = re.sub(r'[._-]+', ' ', name)

    # Remove track numbers at start
    name = re.sub(r'^[\d]{1,3}[\.\-\s]*', '', name)

    # Remove quality/format tags
    name = re.sub(r'\b(320kbps|256kbps|192kbps|128kbps|flac|mp3|wav|aac|ogg|lossless|cd|vinyl|remaster|remastered)\b', '', name, flags=re.IGNORECASE)

    # Remove brackets content
    name = re.sub(r'\[[^\]]*\]', '', name)
    name = re.sub(r'\([^\)]*\)', '', name)

    # Clean up whitespace
    name = re.sub(r'\s+', ' ', name).strip()

    return name


def sanitize_filename(name):
    """Remove invalid characters from filename."""
    # Remove invalid filename characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Replace full-width colon
    name = name.replace('\uff1a', '-')
    return name


class TMDBClient:
    """Client for The Movie Database API."""

    BASE_URL = 'https://api.themoviedb.org/3'

    def __init__(self, api_key):
        self.api_key = api_key

    def search_movie(self, query, year=None):
        """Search for a movie."""
        params = {
            'api_key': self.api_key,
            'query': query,
            'language': 'en-US',
            'page': 1,
            'include_adult': 'false'
        }
        if year:
            params['year'] = year

        response = requests.get(f'{self.BASE_URL}/search/movie', params=params)
        response.raise_for_status()
        return response.json()

    def search_tv(self, query):
        """Search for a TV show."""
        params = {
            'api_key': self.api_key,
            'query': query,
            'language': 'en-US',
            'page': 1,
            'include_adult': 'false'
        }

        response = requests.get(f'{self.BASE_URL}/search/tv', params=params)
        response.raise_for_status()
        return response.json()

    def get_episode_details(self, show_id, season, episode):
        """Get episode title from TMDB."""
        season = int(season)
        episode = int(episode)

        params = {
            'api_key': self.api_key,
            'language': 'en-US'
        }

        url = f'{self.BASE_URL}/tv/{show_id}/season/{season}/episode/{episode}'
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            return data.get('name', '')
        return ''


class MusicBrainzClient:
    """Client for MusicBrainz API."""

    BASE_URL = 'https://musicbrainz.org/ws/2'
    USER_AGENT = 'MediaRenamer/1.0 (https://github.com/sp00nznet/file-renamer)'

    # Rate limiting - 1 request per second
    _last_request = 0

    def _rate_limit(self):
        """Ensure we don't exceed rate limits."""
        elapsed = time.time() - self._last_request
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        self._last_request = time.time()

    def search_recording(self, query):
        """Search for a music recording."""
        self._rate_limit()

        params = {
            'query': query,
            'fmt': 'json',
            'limit': 5
        }

        headers = {'User-Agent': self.USER_AGENT}

        response = requests.get(
            f'{self.BASE_URL}/recording',
            params=params,
            headers=headers
        )
        response.raise_for_status()
        return response.json()


def scan_directory(directory, mode='auto'):
    """
    Scan a directory for media files.
    Returns list of file info dicts.
    """
    files = []

    if not os.path.isdir(directory):
        return files

    for filename in sorted(os.listdir(directory)):
        filepath = os.path.join(directory, filename)

        if not os.path.isfile(filepath):
            continue

        ext = get_extension(filename)

        file_info = {
            'filename': filename,
            'filepath': filepath,
            'extension': ext,
            'type': None,
            'detected_info': None
        }

        if mode in ('auto', 'movies', 'tv') and is_video_file(filename):
            tv_info = detect_tv_show(filename)
            if tv_info and mode != 'movies':
                file_info['type'] = 'tv'
                file_info['detected_info'] = {
                    'show_name': clean_show_name(tv_info['show_name']),
                    'season': tv_info['season'],
                    'episode': tv_info['episode']
                }
            elif mode != 'tv':
                file_info['type'] = 'movie'
                cleaned = clean_movie_name(filename)
                file_info['detected_info'] = cleaned
            files.append(file_info)

        elif mode in ('auto', 'music') and is_audio_file(filename):
            file_info['type'] = 'music'
            file_info['detected_info'] = {
                'query': clean_music_filename(filename)
            }
            files.append(file_info)

    return files


def get_movie_filename(title, year, extension):
    """Create filename in 'Movie Name (Year).ext' format."""
    safe_title = sanitize_filename(title)
    return f"{safe_title} ({year}).{extension}"


def get_tv_filename(show_name, season, episode, episode_title, extension):
    """Create filename in 'Show Name - S01E02 - Episode Title.ext' format."""
    safe_show = sanitize_filename(show_name)
    formatted_season = str(int(season)).zfill(2)
    formatted_episode = str(int(episode)).zfill(2)

    if episode_title:
        safe_episode_title = sanitize_filename(episode_title)
        return f"{safe_show} - S{formatted_season}E{formatted_episode} - {safe_episode_title}.{extension}"
    else:
        return f"{safe_show} - S{formatted_season}E{formatted_episode}.{extension}"


def get_music_filename(artist, title, extension):
    """Create filename in 'Artist - Track Title.ext' format."""
    safe_artist = sanitize_filename(artist)
    safe_title = sanitize_filename(title)
    return f"{safe_artist} - {safe_title}.{extension}"


def rename_file(old_path, new_filename, dry_run=False):
    """
    Rename a file.
    Returns dict with success status and message.
    """
    directory = os.path.dirname(old_path)
    new_path = os.path.join(directory, new_filename)
    old_filename = os.path.basename(old_path)

    if old_filename == new_filename:
        return {
            'success': True,
            'message': 'File already has the correct name',
            'new_path': new_path
        }

    if os.path.exists(new_path):
        return {
            'success': False,
            'message': 'Destination file already exists',
            'new_path': new_path
        }

    if dry_run:
        return {
            'success': True,
            'message': 'Dry run - file would be renamed',
            'new_path': new_path,
            'dry_run': True
        }

    try:
        os.rename(old_path, new_path)
        return {
            'success': True,
            'message': 'File renamed successfully',
            'new_path': new_path
        }
    except OSError as e:
        return {
            'success': False,
            'message': f'Failed to rename file: {str(e)}',
            'new_path': new_path
        }
