import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from invoicelytics.assistants.assistant_builder import AssistantBuilder
from invoicelytics.assistants.chat_assistant import ChatAssistant
from invoicelytics.integrations.open_ai.assistant_client import AssistantClient
from invoicelytics.integrations.open_ai.message_client import MessageClient
from invoicelytics.integrations.open_ai.run_client import RunClient
from invoicelytics.integrations.open_ai.thread_client import ThreadClient
from tests import test_faker


class TestChatAssistant(unittest.TestCase):
    def setUp(self):
        self.assistant_builder_mock = MagicMock(spec=AssistantBuilder)
        self.assistant_client_mock = MagicMock(spec=AssistantClient)
        self.thread_client_mock = MagicMock(spec=ThreadClient)
        self.message_client_mock = MagicMock(spec=MessageClient)
        self.run_client_mock = MagicMock(spec=RunClient)

        self.chat_assistant = ChatAssistant(
            assistant_builder=self.assistant_builder_mock,
            assistant_client=self.assistant_client_mock,
            thread_client=self.thread_client_mock,
            message_client=self.message_client_mock,
            run_client=self.run_client_mock,
        )

    def test_ask_question_success(self):
        # Arrange
        tenant_id = uuid4()
        thread_id = test_faker.ssn()
        question = "What is the status of invoice 123?"

        assistant_id = test_faker.ssn()
        run_id = test_faker.ssn()
        run_status = "completed"
        answer = "The status of invoice 123 is paid."
        assistant = MagicMock(id=assistant_id)

        self.assistant_client_mock.find_by_name.return_value = assistant
        self.thread_client_mock.create_thread.return_value = thread_id
        self.message_client_mock.create.return_value = None

        run_mock = MagicMock(status=run_status, id=run_id)
        self.run_client_mock.create_and_poll.return_value = run_mock

        message_mock = MagicMock(data=[MagicMock(content=[MagicMock(text=MagicMock(value=answer))])])
        self.message_client_mock.list.return_value = message_mock

        # Act
        response, returned_thread_id = self.chat_assistant.ask_question(question, tenant_id, thread_id)

        # Assert
        self.assistant_client_mock.find_by_name.assert_called_once_with(f"emma_chat_assistant__{tenant_id}")
        self.thread_client_mock.create_thread.assert_not_called()  # thread_id is provided
        self.message_client_mock.create.assert_called_once_with(thread_id=thread_id, prompt=question, attachments=[])
        self.run_client_mock.create_and_poll.assert_called_once_with(thread_id=thread_id, assistant_id=assistant_id)
        self.message_client_mock.list.assert_called_once_with(thread_id=thread_id)

        self.assertEqual(response, answer)
        self.assertEqual(returned_thread_id, thread_id)

    def test_ask_question_no_thread_id(self):
        # Arrange
        tenant_id = uuid4()
        thread_id = "thread-id"
        question = "What is the status of invoice 123?"

        assistant_id = "assistant-id"
        run_id = "run-id"
        run_status = "completed"
        answer = "The status of invoice 123 is paid."
        assistant = MagicMock(id=assistant_id)

        self.assistant_client_mock.find_by_name.return_value = assistant
        self.thread_client_mock.create_thread.return_value = thread_id
        self.message_client_mock.create.return_value = None

        run_mock = MagicMock(status=run_status, id=run_id)
        self.run_client_mock.create_and_poll.return_value = run_mock

        message_mock = MagicMock(data=[MagicMock(content=[MagicMock(text=MagicMock(value=answer))])])
        self.message_client_mock.list.return_value = message_mock

        # Act
        response, returned_thread_id = self.chat_assistant.ask_question(question, tenant_id, None)

        # Assert
        self.assistant_client_mock.find_by_name.assert_called_once_with(f"emma_chat_assistant__{tenant_id}")
        self.thread_client_mock.create_thread.assert_called_once()  # thread_id is not provided, so it should be created
        self.message_client_mock.create.assert_called_once_with(thread_id=thread_id, prompt=question, attachments=[])
        self.run_client_mock.create_and_poll.assert_called_once_with(thread_id=thread_id, assistant_id=assistant_id)
        self.message_client_mock.list.assert_called_once_with(thread_id=thread_id)

        self.assertEqual(response, answer)
        self.assertEqual(returned_thread_id, thread_id)

    def test_ask_question_run_not_completed(self):
        # Arrange
        tenant_id = uuid4()
        thread_id = "thread-id"
        question = "What is the status of invoice 123?"

        assistant_id = "assistant-id"
        run_id = "run-id"
        run_status = "not_completed"

        self.assistant_client_mock.find_by_name.return_value = MagicMock(id=assistant_id)
        self.thread_client_mock.create_thread.return_value = thread_id
        self.message_client_mock.create.return_value = None

        run_mock = MagicMock(status=run_status, id=run_id)
        self.run_client_mock.create_and_poll.return_value = run_mock

        # Act
        response, returned_thread_id = self.chat_assistant.ask_question(question, tenant_id, thread_id)

        # Assert
        self.assistant_client_mock.find_by_name.assert_called_once_with(f"emma_chat_assistant__{tenant_id}")
        self.thread_client_mock.create_thread.assert_not_called()  # thread_id is provided
        self.message_client_mock.create.assert_called_once_with(thread_id=thread_id, prompt=question, attachments=[])
        self.run_client_mock.create_and_poll.assert_called_once_with(thread_id=thread_id, assistant_id=assistant_id)
        self.message_client_mock.list.assert_not_called()
        self.run_client_mock.cancel_run.assert_called_once_with(thread_id=thread_id, run_id=run_id)

        self.assertIsNone(response)
        self.assertEqual(returned_thread_id, thread_id)

    def test_ask_question_run_failed(self):
        # Arrange
        tenant_id = uuid4()
        thread_id = "thread-id"
        question = "What is the status of invoice 123?"

        assistant_id = "assistant-id"
        run_id = "run-id"
        run_status = "failed"

        self.assistant_client_mock.find_by_name.return_value = MagicMock(id=assistant_id)
        self.thread_client_mock.create_thread.return_value = thread_id
        self.message_client_mock.create.return_value = None

        run_mock = MagicMock(status=run_status, id=run_id)
        self.run_client_mock.create_and_poll.return_value = run_mock

        # Act
        response, returned_thread_id = self.chat_assistant.ask_question(question, tenant_id, thread_id)

        # Assert
        self.assistant_client_mock.find_by_name.assert_called_once_with(f"emma_chat_assistant__{tenant_id}")
        self.thread_client_mock.create_thread.assert_not_called()  # thread_id is provided
        self.message_client_mock.create.assert_called_once_with(thread_id=thread_id, prompt=question, attachments=[])
        self.run_client_mock.create_and_poll.assert_called_once_with(thread_id=thread_id, assistant_id=assistant_id)
        self.message_client_mock.list.assert_not_called()
        self.run_client_mock.cancel_run.assert_not_called()

        self.assertEqual(response, None)
        self.assertEqual(returned_thread_id, thread_id)
