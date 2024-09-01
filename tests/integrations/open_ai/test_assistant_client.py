from unittest import TestCase
from unittest.mock import MagicMock

from invoicelytics.integrations.open_ai.assistant_client import AssistantClient


class TestAssistantClient(TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_client.beta.assistants.create = MagicMock()
        self.mock_client.beta.assistants.list = MagicMock()

        self.message_client = AssistantClient(
            client=self.mock_client,
        )

    def test_create_assistant(self):
        name = "Test Assistant"
        model = "gpt-4o"
        description = "Test Description"
        instructions = "Test Instructions"
        tools = [{"tool": "test_tool"}]

        self.message_client.create(name, model, description, instructions, tools)

        self.mock_client.beta.assistants.create.assert_called_once_with(
            name=name,
            model=model,
            description=description,
            instructions=instructions,
            tools=tools,
            tool_resources=None,
            temperature=0.01,
            top_p=1.0,
        )

    def test_find_by_name(self):
        name = "Test Assistant"
        mock_assistant = MagicMock()
        mock_assistant.name = name
        self.mock_client.beta.assistants.list.return_value = [mock_assistant]

        result = self.message_client.find_by_name(name)

        self.assertEqual(result, mock_assistant)
        self.mock_client.beta.assistants.list.assert_called_once_with(limit=100)
