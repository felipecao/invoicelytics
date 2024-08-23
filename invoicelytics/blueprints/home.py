import logging

from flask import Blueprint, redirect, url_for


class HomeBlueprint:
    def __init__(self):
        self.blueprint = Blueprint("home_bp", __name__)
        self.logger = logging.getLogger(__name__)
        self.add_routes()

    def add_routes(self):
        @self.blueprint.route("/", methods=["GET"])
        def home():
            return redirect(url_for("invoice_bp.list_processed_invoices"))
