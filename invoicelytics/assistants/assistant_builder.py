from typing import Optional

from invoicelytics.integrations.open_ai.assistant_client import AssistantClient


class AssistantBuilder:
    def __init__(self, assistant_client: Optional[AssistantClient] = None):
        self._assistant_client = assistant_client or AssistantClient()

    def create_assistant_if_does_not_exist(
        self, name: str, description: str, instructions: str, tools: Optional[list[dict]] = None, tool_resources: Optional[dict] = None
    ):
        existing_assistant = self._assistant_client.find_by_name(name)

        if existing_assistant:
            return existing_assistant.id

        existing_assistant = self._assistant_client.create(
            name=name,
            description=description,
            instructions=instructions,
            tools=tools,
            tool_resources=tool_resources,
        )

        return existing_assistant.id
