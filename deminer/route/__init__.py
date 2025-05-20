from flask import Flask
from .error_handler import err_handler_bp

def register_routes(app: Flask) -> None:
    app.register_blueprint(err_handler_bp)

    from .user_route import user_bp
    from .session_route import sessions_bp
    from .commands_route import commands_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(commands_bp)