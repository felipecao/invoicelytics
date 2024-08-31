import logging
import os
import threading
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def _create_folder_if_not_exists(folder_path):
    path = Path(folder_path)
    path.mkdir(parents=True, exist_ok=True)


def create_app():
    flask_app = Flask(__name__)

    logging.basicConfig(level=logging.INFO)

    from invoicelytics.blueprints.health import HealthBlueprint
    from invoicelytics.blueprints.home import HomeBlueprint
    from invoicelytics.blueprints.invoice import InvoiceBlueprint

    flask_app.register_blueprint(HealthBlueprint().blueprint)
    flask_app.register_blueprint(HomeBlueprint().blueprint)
    flask_app.register_blueprint(InvoiceBlueprint().blueprint)

    flask_app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    flask_app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]
    flask_app.config["UPLOAD_FOLDER"] = os.environ["UPLOAD_FOLDER"]

    _create_folder_if_not_exists(os.environ["UPLOAD_FOLDER"])

    db.init_app(flask_app)

    def initialize_chat_assistants():
        with flask_app.app_context():
            logging.info("Started initializing chat assistants")

            from invoicelytics.assistants.chat_assistant import ChatAssistant
            from invoicelytics.repository.tenant_repository import TenantRepository

            tenant_repository = TenantRepository()
            chat_assistant = ChatAssistant()

            for tenant in tenant_repository.find_all():
                chat_assistant.create_if_not_exists(tenant.id)

            logging.info("Finished initializing chat assistants")

    threading.Thread(target=initialize_chat_assistants).start()

    return flask_app


if __name__ == "__main__":
    app = create_app()
    app.run()
