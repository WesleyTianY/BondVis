from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from .config import Config
from .routes.transaction_routes import transaction_bp

def create_app():
    app = Flask(__name__, static_url_path='', static_folder='server', template_folder='../client/dist')
    app.config.from_object(Config)
    CORS(app)

    # 注册蓝图
    app.register_blueprint(transaction_bp)

    return app
