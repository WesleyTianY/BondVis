# -*- coding: utf-8 -*-
from flask import Flask, current_app
from flask_cors import CORS
from flask_caching import Cache
from backend.routes.bond_api import bond_bp
from backend.routes.transaction_api import transaction_bp
from backend.routes.institution_api import institution_bp
from backend.routes.graph_data_api import graph_data_bp
from backend.routes.bond_pool_api import bond_pool_bp
from backend.routes.transactionChain_api import transactionChain_bp
from backend.routes.bondData_api import bondData_bp
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
    app.register_blueprint(transaction_bp, url_prefix='/api')
    app.register_blueprint(institution_bp, url_prefix='/api')
    app.register_blueprint(graph_data_bp, url_prefix='/api')
    app.register_blueprint(bond_pool_bp, url_prefix='/api')
    app.register_blueprint(transactionChain_bp, url_prefix='/api')
    app.register_blueprint(bondData_bp, url_prefix='/api')
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
