# -*- coding: utf-8 -*-
from flask import Flask, current_app
from flask_cors import CORS
from flask_caching import Cache
from backend.routes.bond_api import bond_bp

# Flask-Caching related config
CACHE_CONFIG = {
    'CACHE_TYPE': 'simple',  # Simple Cache for demonstration, use Redis or other backend for production
    'CACHE_DEFAULT_TIMEOUT': 300  # default timeout for cache in seconds
}

STATIC_FOLDER = 'static'
TEMPLATE_FOLDER = '../client/dist'

def create_app():
    app = Flask(__name__, static_url_path='', static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
    app.config.from_object('config')

    # Initialize Cache
    app.config.from_mapping(CACHE_CONFIG)
    cache = Cache(app)

    # Store cache in app config for later use in blueprints
    app.config['cache'] = cache

    CORS(app)

    app.register_blueprint(bond_bp, url_prefix='/api')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
