"""
Flask routes for Media Renamer Web App
"""

import os
from flask import Blueprint, render_template, request, jsonify, current_app
from . import renamer

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@bp.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration."""
    return jsonify({
        'tmdb_api_key': bool(current_app.config.get('TMDB_API_KEY')),
        'media_dir': current_app.config.get('MEDIA_DIR', '/media')
    })


@bp.route('/api/config', methods=['POST'])
def set_config():
    """Update configuration."""
    data = request.json

    if 'tmdb_api_key' in data:
        current_app.config['TMDB_API_KEY'] = data['tmdb_api_key']

    if 'media_dir' in data:
        media_dir = data['media_dir']
        if os.path.isdir(media_dir):
            current_app.config['MEDIA_DIR'] = media_dir
        else:
            return jsonify({'error': f'Directory not found: {media_dir}'}), 400

    return jsonify({'success': True})


@bp.route('/api/scan', methods=['POST'])
def scan_files():
    """Scan directory for media files."""
    data = request.json or {}
    directory = data.get('directory', current_app.config.get('MEDIA_DIR', '/media'))
    mode = data.get('mode', 'auto')

    if not os.path.isdir(directory):
        return jsonify({'error': f'Directory not found: {directory}'}), 400

    files = renamer.scan_directory(directory, mode)

    return jsonify({
        'directory': directory,
        'mode': mode,
        'files': files,
        'count': len(files)
    })


@bp.route('/api/browse', methods=['GET'])
def browse_directory():
    """Browse directories."""
    path = request.args.get('path', '/')

    if not os.path.isdir(path):
        return jsonify({'error': 'Path not found'}), 404

    items = []
    try:
        for name in sorted(os.listdir(path)):
            full_path = os.path.join(path, name)
            if os.path.isdir(full_path):
                items.append({
                    'name': name,
                    'path': full_path,
                    'type': 'directory'
                })
    except PermissionError:
        return jsonify({'error': 'Permission denied'}), 403

    parent = os.path.dirname(path) if path != '/' else None

    return jsonify({
        'current': path,
        'parent': parent,
        'items': items
    })


@bp.route('/api/search/movie', methods=['POST'])
def search_movie():
    """Search for a movie on TMDB."""
    api_key = current_app.config.get('TMDB_API_KEY')
    if not api_key:
        return jsonify({'error': 'TMDB API key not configured'}), 400

    data = request.json
    query = data.get('query', '')
    year = data.get('year')

    if not query:
        return jsonify({'error': 'Query is required'}), 400

    try:
        client = renamer.TMDBClient(api_key)
        results = client.search_movie(query, year)

        # Format results for frontend
        movies = []
        for movie in results.get('results', [])[:5]:
            release_date = movie.get('release_date', '')
            year = release_date.split('-')[0] if release_date else ''
            movies.append({
                'id': movie.get('id'),
                'title': movie.get('title'),
                'year': year,
                'overview': movie.get('overview', '')[:150],
                'vote_average': movie.get('vote_average', 0)
            })

        return jsonify({
            'query': query,
            'results': movies,
            'total': results.get('total_results', 0)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/search/tv', methods=['POST'])
def search_tv():
    """Search for a TV show on TMDB."""
    api_key = current_app.config.get('TMDB_API_KEY')
    if not api_key:
        return jsonify({'error': 'TMDB API key not configured'}), 400

    data = request.json
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'Query is required'}), 400

    try:
        client = renamer.TMDBClient(api_key)
        results = client.search_tv(query)

        # Format results for frontend
        shows = []
        for show in results.get('results', [])[:5]:
            first_air_date = show.get('first_air_date', '')
            year = first_air_date.split('-')[0] if first_air_date else ''
            shows.append({
                'id': show.get('id'),
                'name': show.get('name'),
                'year': year,
                'overview': show.get('overview', '')[:150],
                'vote_average': show.get('vote_average', 0)
            })

        return jsonify({
            'query': query,
            'results': shows,
            'total': results.get('total_results', 0)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/search/tv/episode', methods=['POST'])
def get_episode():
    """Get episode details from TMDB."""
    api_key = current_app.config.get('TMDB_API_KEY')
    if not api_key:
        return jsonify({'error': 'TMDB API key not configured'}), 400

    data = request.json
    show_id = data.get('show_id')
    season = data.get('season')
    episode = data.get('episode')

    if not all([show_id, season, episode]):
        return jsonify({'error': 'show_id, season, and episode are required'}), 400

    try:
        client = renamer.TMDBClient(api_key)
        episode_title = client.get_episode_details(show_id, season, episode)

        return jsonify({
            'show_id': show_id,
            'season': season,
            'episode': episode,
            'title': episode_title
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/search/music', methods=['POST'])
def search_music():
    """Search for music on MusicBrainz."""
    data = request.json
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'Query is required'}), 400

    try:
        client = renamer.MusicBrainzClient()
        results = client.search_recording(query)

        # Format results for frontend
        recordings = []
        for rec in results.get('recordings', [])[:5]:
            artist_credit = rec.get('artist-credit', [{}])
            artist = artist_credit[0].get('name', 'Unknown Artist') if artist_credit else 'Unknown Artist'

            releases = rec.get('releases', [{}])
            album = releases[0].get('title', 'Unknown Album') if releases else 'Unknown Album'
            date = releases[0].get('date', '') if releases else ''
            year = date.split('-')[0] if date else ''

            recordings.append({
                'id': rec.get('id'),
                'title': rec.get('title'),
                'artist': artist,
                'album': album,
                'year': year,
                'score': rec.get('score', 0)
            })

        return jsonify({
            'query': query,
            'results': recordings
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/preview', methods=['POST'])
def preview_rename():
    """Preview what a file would be renamed to."""
    data = request.json
    file_type = data.get('type')
    filepath = data.get('filepath')

    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    extension = renamer.get_extension(os.path.basename(filepath))

    if file_type == 'movie':
        title = data.get('title')
        year = data.get('year')
        if not title or not year:
            return jsonify({'error': 'title and year are required'}), 400
        new_filename = renamer.get_movie_filename(title, year, extension)

    elif file_type == 'tv':
        show_name = data.get('show_name')
        season = data.get('season')
        episode = data.get('episode')
        episode_title = data.get('episode_title', '')
        if not show_name or not season or not episode:
            return jsonify({'error': 'show_name, season, and episode are required'}), 400
        new_filename = renamer.get_tv_filename(show_name, season, episode, episode_title, extension)

    elif file_type == 'music':
        artist = data.get('artist')
        title = data.get('title')
        if not artist or not title:
            return jsonify({'error': 'artist and title are required'}), 400
        new_filename = renamer.get_music_filename(artist, title, extension)

    else:
        return jsonify({'error': 'Invalid file type'}), 400

    directory = os.path.dirname(filepath)
    new_filepath = os.path.join(directory, new_filename)

    return jsonify({
        'original_filename': os.path.basename(filepath),
        'new_filename': new_filename,
        'new_filepath': new_filepath,
        'already_exists': os.path.exists(new_filepath)
    })


@bp.route('/api/rename', methods=['POST'])
def rename_file():
    """Rename a file."""
    data = request.json
    file_type = data.get('type')
    filepath = data.get('filepath')
    dry_run = data.get('dry_run', False)

    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    extension = renamer.get_extension(os.path.basename(filepath))

    if file_type == 'movie':
        title = data.get('title')
        year = data.get('year')
        if not title or not year:
            return jsonify({'error': 'title and year are required'}), 400
        new_filename = renamer.get_movie_filename(title, year, extension)

    elif file_type == 'tv':
        show_name = data.get('show_name')
        season = data.get('season')
        episode = data.get('episode')
        episode_title = data.get('episode_title', '')
        if not show_name or not season or not episode:
            return jsonify({'error': 'show_name, season, and episode are required'}), 400
        new_filename = renamer.get_tv_filename(show_name, season, episode, episode_title, extension)

    elif file_type == 'music':
        artist = data.get('artist')
        title = data.get('title')
        if not artist or not title:
            return jsonify({'error': 'artist and title are required'}), 400
        new_filename = renamer.get_music_filename(artist, title, extension)

    else:
        return jsonify({'error': 'Invalid file type'}), 400

    result = renamer.rename_file(filepath, new_filename, dry_run)

    return jsonify({
        'original_filename': os.path.basename(filepath),
        'new_filename': new_filename,
        **result
    })


@bp.route('/api/batch/rename', methods=['POST'])
def batch_rename():
    """Rename multiple files at once."""
    data = request.json
    files = data.get('files', [])
    dry_run = data.get('dry_run', False)

    results = []

    for file_data in files:
        file_type = file_data.get('type')
        filepath = file_data.get('filepath')

        if not filepath or not os.path.exists(filepath):
            results.append({
                'filepath': filepath,
                'success': False,
                'message': 'File not found'
            })
            continue

        extension = renamer.get_extension(os.path.basename(filepath))

        try:
            if file_type == 'movie':
                new_filename = renamer.get_movie_filename(
                    file_data.get('title'),
                    file_data.get('year'),
                    extension
                )
            elif file_type == 'tv':
                new_filename = renamer.get_tv_filename(
                    file_data.get('show_name'),
                    file_data.get('season'),
                    file_data.get('episode'),
                    file_data.get('episode_title', ''),
                    extension
                )
            elif file_type == 'music':
                new_filename = renamer.get_music_filename(
                    file_data.get('artist'),
                    file_data.get('title'),
                    extension
                )
            else:
                results.append({
                    'filepath': filepath,
                    'success': False,
                    'message': 'Invalid file type'
                })
                continue

            result = renamer.rename_file(filepath, new_filename, dry_run)
            results.append({
                'original_filename': os.path.basename(filepath),
                'new_filename': new_filename,
                **result
            })
        except Exception as e:
            results.append({
                'filepath': filepath,
                'success': False,
                'message': str(e)
            })

    success_count = sum(1 for r in results if r.get('success'))

    return jsonify({
        'results': results,
        'total': len(results),
        'success_count': success_count,
        'dry_run': dry_run
    })
