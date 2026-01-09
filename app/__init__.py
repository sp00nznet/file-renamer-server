from flask import Flask
import os

def create_app():
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['TMDB_API_KEY'] = os.environ.get('TMDB_API_KEY', '')
    app.config['MEDIA_DIR'] = os.environ.get('MEDIA_DIR', '/media')

    from . import routes
    app.register_blueprint(routes.bp)

    return app
