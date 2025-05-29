import secrets

from flask_socketio import SocketIO, emit
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from flask_cors import CORS
from flask import request, jsonify
import jwt
import datetime
from functools import wraps

from deminer.route import register_routes

SECRET_KEY = "SECRET_KEY"
SECRET_KEY_JWT = "16c67642bd495567497f6363c4478c9cf37d723c42f7d7326e938dd9cbf310cbb90894ece3ad79802629c57ed915e34dd25cedef8e2f31602dcd9b77a4b4365eb2a3f60c5d0b4cafa124cb19650e4feda7f1a39b47efbbab9e3b9d7b62d43c91"
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
    app.config[SQLALCHEMY_DATABASE_URI] = "mysql://platform:PL-31013107606@176.118.54.8:31606/platform"
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


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
            current_user = data['user']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated