from typing import Optional
from uuid import UUID

from invoicelytics.assistants.assistant_builder import AssistantBuilder


class ChatAssistant:
    def __init__(
        self,
        assistant_builder: Optional[AssistantBuilder] = None,
    ):
        self._assistant_builder = assistant_builder or AssistantBuilder()
        self._NAME = "emma_chat_assistant_"

    def create_if_not_exists(self, tenant_id: UUID):
        return self._assistant_builder.create_assistant_if_does_not_exist(
            name=f"{self._NAME}_{tenant_id}",
            description="Emma is an accounting assistant who provides information about invoices uploaded into the system",
            tools=[{"type": "file_search"}],
            instructions="""
                You are Emma, an accounting assistant who provides information about invoices uploaded into the system.

                Your role is to process the invoices uploaded into our storage and provide accurate and precise information about them.
                Whenever you don't know how to answer a question, you simply say "I don't know". You don't create imaginary values.
            """,
        )
