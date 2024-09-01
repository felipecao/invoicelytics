import logging
from typing import Optional
from uuid import UUID

from invoicelytics.assistants.assistant_builder import AssistantBuilder
from invoicelytics.integrations.open_ai.assistant_client import AssistantClient
from invoicelytics.integrations.open_ai.message_client import MessageClient
from invoicelytics.integrations.open_ai.run_client import RunClient
from invoicelytics.integrations.open_ai.thread_client import ThreadClient


class ChatAssistant:
    def __init__(
        self,
        assistant_builder: Optional[AssistantBuilder] = None,
        assistant_client: Optional[AssistantClient] = None,
        thread_client: Optional[ThreadClient] = None,
        message_client: Optional[MessageClient] = None,
        run_client: Optional[RunClient] = None,
    ):
        self._assistant_builder = assistant_builder or AssistantBuilder()
        self._assistant_client = assistant_client or AssistantClient()
        self._thread_client = thread_client or ThreadClient()
        self._message_client = message_client or MessageClient()
        self._run_client = run_client or RunClient()

        self._logger = logging.getLogger(__name__)
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

    def ask_question(self, question: str, tenant_id: UUID, thread_id: Optional[str]):
        assistant_id = self._get_assistant_id(tenant_id)

        if not thread_id:
            thread_id = self._thread_client.create_thread()

        self._message_client.create(thread_id=thread_id, prompt=question, attachments=[])

        run = self._run_client.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )

        if run.status != "completed":
            self._logger.error(f"Assistant failed to answer question, tenant_id: {tenant_id}, thread_id: {thread_id}, question: {question}")
            if run.status != "failed":
                self._run_client.cancel_run(thread_id=thread_id, run_id=run.id)

            return None, thread_id

        messages = self._message_client.list(thread_id=thread_id)

        return messages.data[0].content[0].text.value, thread_id

    def _get_assistant_id(self, tenant_id: UUID):
        assistant_name = f"{self._NAME}_{tenant_id}"
        assistant = self._assistant_client.find_by_name(assistant_name)
        return assistant.id
