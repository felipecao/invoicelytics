import logging
from typing import Optional

from flask import Blueprint, request, flash, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required

from invoicelytics.repository.user_repository import UserRepository


class AuthBlueprint:
    def __init__(self, user_repository: Optional[UserRepository] = None):
        self._user_repository = user_repository or UserRepository()
        self.blueprint = Blueprint("auth_bp", __name__)
        self.logger = logging.getLogger(__name__)
        self.add_routes()

    def add_routes(self):
        @self.blueprint.route("/login", methods=["GET", "POST"])
        def login():
            if request.method == "POST":
                email = request.form["email"]
                password = request.form["password"]
                user = self._user_repository.find_by_email(email)

                if user and user.check_password(password):
                    login_user(user)
                    return redirect(url_for("home_bp.home"))

                flash("Invalid email or password")
            return render_template("login.html")

        @self.blueprint.route("/logout")
        @login_required
        def logout():
            logout_user()
            return redirect(url_for("auth_bp.login"))
