import logging
import os
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager


db = SQLAlchemy()
login_manager = LoginManager()


def _create_folder_if_not_exists(folder_path):
    path = Path(folder_path)
    path.mkdir(parents=True, exist_ok=True)


@login_manager.user_loader
def load_user(user_id):
    from invoicelytics.repository.user_repository import UserRepository

    return UserRepository.find_by_id(user_id)


def create_app():
    flask_app = Flask(__name__)

    logging.basicConfig(level=logging.INFO)

    from invoicelytics.blueprints.auth import AuthBlueprint
    from invoicelytics.blueprints.bootstrap import BootstrapBlueprint
    from invoicelytics.blueprints.chat import ChatBlueprint
    from invoicelytics.blueprints.health import HealthBlueprint
    from invoicelytics.blueprints.home import HomeBlueprint
    from invoicelytics.blueprints.invoice import InvoiceBlueprint

    flask_app.register_blueprint(AuthBlueprint().blueprint)
    flask_app.register_blueprint(BootstrapBlueprint().blueprint)
    flask_app.register_blueprint(ChatBlueprint().blueprint)
    flask_app.register_blueprint(HealthBlueprint().blueprint)
    flask_app.register_blueprint(HomeBlueprint().blueprint)
    flask_app.register_blueprint(InvoiceBlueprint().blueprint)

    flask_app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    flask_app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]
    flask_app.config["UPLOAD_FOLDER"] = os.environ["UPLOAD_FOLDER"]

    _create_folder_if_not_exists(os.environ["UPLOAD_FOLDER"])

    db.init_app(flask_app)
    login_manager.init_app(flask_app)
    login_manager.login_view = "auth_bp.login"

    return flask_app


if __name__ == "__main__":
    app = create_app()
    app.run()
