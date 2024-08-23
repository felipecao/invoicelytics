import random
from unittest import TestCase
from unittest.mock import MagicMock

from openai.pagination import SyncCursorPage
from openai.types.beta.threads import Message

from invoicelytics.integrations.open_ai.message_client import MessageClient
from tests import test_faker
from tests.randoms import fake_object


class TestMessageClient(TestCase):

    def setUp(self):
        self.mock_page = MagicMock(spec=SyncCursorPage)
        self.mock_message = MagicMock(spec=Message)
        self.mock_messages = MagicMock()

        self.mock_messages.create.return_value = self.mock_message
        self.mock_messages.list.return_value = self.mock_page

        self.mock_client = fake_object({"beta": fake_object({"threads": fake_object({"messages": self.mock_messages})})})

        self.message_client = MessageClient(
            client=self.mock_client,
        )

    def test_create(self):
        thread_id = test_faker.word()
        prompt = test_faker.paragraph()
        role = random.choice(["user", "assistant"])
        attachments = []

        result = self.message_client.create(thread_id, prompt, role, attachments)

        self.assertEqual(result, self.mock_message)

    def test_list(self):
        thread_id = test_faker.word()

        result = self.message_client.list(thread_id)

        self.assertEqual(result, self.mock_page)
