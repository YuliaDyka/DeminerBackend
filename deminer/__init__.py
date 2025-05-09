import secrets

from flask_socketio import SocketIO, emit
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from flask_cors import CORS

from deminer.route import register_routes

SECRET_KEY = "SECRET_KEY"
SQLALCHEMY_DATABASE_URI = "SQLALCHEMY_DATABASE_URI"
MYSQL_ROOT_USER = "MYSQL_ROOT_USER"
MYSQL_ROOT_PASSWORD = "MYSQL_ROOT_PASSWORD"

# Database
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")

def create_app() -> Flask:
    """
    Creates Flask application
    :param db_uri: SQLAlchemy database
    :return: Flask application object
    """
    app = Flask(__name__)
    CORS(app)
    socketio.init_app(app)
    app.config["SECRET_KEY"] = secrets.token_hex(16)
    app.config[SQLALCHEMY_DATABASE_URI] = "mysql://user1:Ir-31013107606@localhost/deminer"
    app.json.sort_keys = False

    @app.route("/")
    def root():
        return "Welcome to the main page!"

    _init_db(app)
    register_routes(app)

    return app

def _init_db(app: Flask) -> None:
    """
    Initializes DB with SQLAlchemy
    :param app: Flask application object
    """
    db.init_app(app)

    if not database_exists(app.config[SQLALCHEMY_DATABASE_URI]):
        create_database(app.config[SQLALCHEMY_DATABASE_URI])

    import deminer.model
    with app.app_context():
        db.create_all()