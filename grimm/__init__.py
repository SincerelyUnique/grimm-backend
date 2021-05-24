import logging
import os

from flask import Flask
from flask_compress import Compress
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_restx import Api
from sqlalchemy.engine import create_engine

from config import configuration

compress = Compress()
db = SQLAlchemy()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(filename)s:%(lineno)d:%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)
GrimmConfig = configuration['dev']
engine = create_engine(GrimmConfig.SQLALCHEMY_DATABASE_URI)
TOP_DIR = os.path.dirname(__file__) or "."
socketio = SocketIO(cors_allowed_origins='*', debug=True)
api = Api()


def create_app(config_file):
    app = Flask(__name__)
    app.config.from_object(GrimmConfig)
    compress.init_app(app)
    db.init_app(app)
    CORS(app)
    app.url_map.redirect_defaults = False
    socketio.init_app(app)
    api.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .activity import activity as activity_blueprint
    app.register_blueprint(activity_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    from .wxapp import wxapp as wxapp_blueprint
    app.register_blueprint(wxapp_blueprint)

    return app
