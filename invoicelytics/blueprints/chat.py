import logging
from typing import Optional
from uuid import UUID

from flask import Blueprint, request, render_template
from flask_login import login_required

from invoicelytics.assistants.chat_assistant import ChatAssistant


class ChatBlueprint:
    def __init__(
        self,
        chat_assistant: Optional[ChatAssistant] = None,
    ):
        # TODO remove this fixed tenant id. This should be fetched from the accounts table based on the logged user.
        self._TENANT_ID = UUID("123e4567-e89b-12d3-a456-426614174000")
        # end TODO

        self.blueprint = Blueprint("chat_bp", __name__)
        self._chat_assistant = chat_assistant or ChatAssistant()
        self.logger = logging.getLogger(__name__)
        self.add_routes()

    def add_routes(self):
        @self.blueprint.route("/chat", methods=["GET"])
        @login_required
        def load_page():
            return render_template("chat.html")

        @self.blueprint.route("/chat", methods=["POST"])
        @login_required
        def post_message_and_get_response():
            user_message = request.json.get("message")
            thread_id = request.json.get("thread_id")

            if user_message:
                response, thread_id = self._chat_assistant.ask_question(user_message, self._TENANT_ID, thread_id)
                return {"response": response, "thread_id": thread_id}
            return {"error": "No message provided"}, 400
