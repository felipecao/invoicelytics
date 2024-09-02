import logging

from flask import Blueprint, render_template
from flask_login import login_required


class HomeBlueprint:
    def __init__(self):
        self.blueprint = Blueprint("home_bp", __name__)
        self.logger = logging.getLogger(__name__)
        self.add_routes()

    def add_routes(self):
        @self.blueprint.route("/", methods=["GET"])
        @login_required
        def home():
            return render_template("home.html")
