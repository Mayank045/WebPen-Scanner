from flask import Flask

from .config import Config
from .database import init_db
from .routes.api import api_bp
from .routes.web import web_bp


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    init_db(app)
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    return app
