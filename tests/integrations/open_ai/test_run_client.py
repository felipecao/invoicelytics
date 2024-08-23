from unittest import TestCase
from unittest.mock import MagicMock

from openai.types.beta.threads import Run

from invoicelytics.integrations.open_ai.run_client import RunClient
from tests import test_faker
from tests.randoms import fake_object


class TestRunClient(TestCase):
    def setUp(self):
        self.mock_run = MagicMock(spec=Run)
        self.mock_create_and_poll = MagicMock()

        self.mock_create_and_poll.create_and_poll.return_value = self.mock_run
        self.mock_create_and_poll.cancel.return_value = self.mock_run

        self.mock_client = fake_object({"beta": fake_object({"threads": fake_object({"runs": self.mock_create_and_poll})})})

        self.run_client = RunClient(
            client=self.mock_client,
        )

    def test_create_and_poll(self):
        thread_id = test_faker.word()
        assistant_id = test_faker.word()
        run_id = test_faker.word()

        self.mock_run.id = run_id

        result = self.run_client.create_and_poll(thread_id, assistant_id)

        self.assertEqual(run_id, result.id)
        self.mock_create_and_poll.create_and_poll.assert_called_once_with(
            thread_id=thread_id,
            assistant_id=assistant_id,
            tool_choice="auto",
        )

    def test_cancel_run(self):
        thread_id = test_faker.word()
        run_id = test_faker.word()

        self.mock_run.id = run_id

        result = self.run_client.cancel_run(thread_id, run_id)

        self.assertEqual(run_id, result.id)
        self.mock_create_and_poll.cancel.assert_called_once_with(
            thread_id=thread_id,
            run_id=run_id,
        )
