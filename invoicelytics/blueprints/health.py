import logging

from flask import Blueprint


class HealthBlueprint:
    def __init__(self):
        self.blueprint = Blueprint("health_bp", __name__)
        self.logger = logging.getLogger(__name__)
        self.add_routes()

    def add_routes(self):
        @self.blueprint.route("/health", methods=["GET"])
        def health_check():
            return {"health": "ok"}
