import logging
from typing import Optional

from flask import Blueprint

from invoicelytics.services.openai_bootstrap_service import OpenAiBootstrapService


class BootstrapBlueprint:
    def __init__(self, openai_bootstrap_service: Optional[OpenAiBootstrapService] = None):
        self.blueprint = Blueprint("bootstrap_bp", __name__)
        self.logger = logging.getLogger(__name__)
        self._openai_bootstrap_service = openai_bootstrap_service or OpenAiBootstrapService()
        self.add_routes()

    def add_routes(self):
        @self.blueprint.route("/bootstrap", methods=["POST"])
        def start_bootstrap():
            self._openai_bootstrap_service.execute()
            return {"bootstrap": "ok"}
