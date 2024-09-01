from unittest import TestCase
from unittest.mock import MagicMock

from invoicelytics.assistants.assistant_builder import AssistantBuilder
from invoicelytics.integrations.open_ai.assistant_client import AssistantClient


class TestAssistantBuilder(TestCase):
    def setUp(self):
        self.mock_assistant_client = MagicMock(spec=AssistantClient)
        self.builder = AssistantBuilder(assistant_client=self.mock_assistant_client)

    def test_create_assistant_if_does_not_exist_existing(self):
        name = "Test Assistant"
        description = "Test Description"
        instructions = "Test Instructions"
        tools = [{"tool": "test_tool"}]
        mock_existing_assistant = MagicMock()
        mock_existing_assistant.id = "existing_id"
        self.mock_assistant_client.find_by_name.return_value = mock_existing_assistant

        assistant_id = self.builder.create_assistant_if_does_not_exist(name, description, instructions, tools)

        self.mock_assistant_client.find_by_name.assert_called_once_with(name)
        self.mock_assistant_client.create.assert_not_called()
        self.assertEqual(assistant_id, "existing_id")

    def test_create_assistant_if_does_not_exist_new(self):
        name = "Test Assistant"
        description = "Test Description"
        instructions = "Test Instructions"
        tools = [{"tool": "test_tool"}]
        tool_resources = {"tools_resources": "test_tools_resources"}

        mock_new_assistant = MagicMock()
        mock_new_assistant.id = "new_id"

        self.mock_assistant_client.find_by_name.return_value = None
        self.mock_assistant_client.create.return_value = mock_new_assistant

        assistant_id = self.builder.create_assistant_if_does_not_exist(name, description, instructions, tools, tool_resources)

        self.mock_assistant_client.find_by_name.assert_called_once_with(name)
        self.mock_assistant_client.create.assert_called_once_with(
            name=name,
            description=description,
            instructions=instructions,
            tools=tools,
            tool_resources=tool_resources,
        )
        self.assertEqual(assistant_id, "new_id")
