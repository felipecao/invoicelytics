from unittest import TestCase

from invoicelytics.integrations.open_ai.thread_client import ThreadClient
from tests import test_faker
from tests.randoms import fake_object

thread_id = test_faker.word()


class MockThreads:
    @staticmethod
    def create():
        return fake_object({"id": thread_id})


class TestThreadClient(TestCase):

    def test_create_thread(self):
        mock_client = fake_object({"beta": fake_object({"threads": MockThreads()})})
        thread_client = ThreadClient(client=mock_client)

        result = thread_client.create_thread()

        self.assertEqual(thread_id, result)
