import json
from unittest import TestCase
from unittest.mock import MagicMock

from flask import Flask

from invoicelytics.assistants.chat_assistant import ChatAssistant
from invoicelytics.blueprints.chat import ChatBlueprint
from tests import test_faker


class TestChatBlueprint(TestCase):
    def setUp(self):
        self._mock_chat_assistant = MagicMock(spec=ChatAssistant)
        self.app = Flask(__name__)
        self.chat_blueprint = ChatBlueprint(
            chat_assistant=self._mock_chat_assistant,
        )
        self.app.register_blueprint(self.chat_blueprint.blueprint)
        self.client = self.app.test_client()

    def test_message_and_get_response(self):
        message = test_faker.sentence()
        thread_id = test_faker.ssn()
        answer = test_faker.sentence()

        payload = {
            "message": message,
            "thread_id": thread_id,
        }

        self._mock_chat_assistant.ask_question.return_value = answer, thread_id

        response = self.client.post("/chat", data=json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["response"], answer)
        self.assertEqual(response.json["thread_id"], thread_id)

    def test_message_and_get_response_without_thread_id(self):
        message = test_faker.sentence()
        thread_id = test_faker.ssn()
        answer = test_faker.sentence()

        payload = {
            "message": message,
        }

        self._mock_chat_assistant.ask_question.return_value = answer, thread_id

        response = self.client.post("/chat", data=json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["response"], answer)
        self.assertEqual(response.json["thread_id"], thread_id)

    def test_message_and_get_response_without_message(self):
        thread_id = test_faker.ssn()
        answer = test_faker.sentence()

        payload = {
            "thread_id": thread_id,
        }

        self._mock_chat_assistant.ask_question.return_value = answer, thread_id

        response = self.client.post("/chat", data=json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"], "No message provided")
