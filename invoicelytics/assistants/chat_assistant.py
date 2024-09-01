import logging
from typing import Optional
from uuid import UUID

from invoicelytics.integrations.open_ai.message_client import MessageClient
from invoicelytics.integrations.open_ai.run_client import RunClient
from invoicelytics.integrations.open_ai.thread_client import ThreadClient
from invoicelytics.repository.tenant_repository import TenantRepository


class ChatAssistant:

    NAME_PREFIX = "emma_chat_assistant_"

    def __init__(
        self,
        thread_client: Optional[ThreadClient] = None,
        message_client: Optional[MessageClient] = None,
        run_client: Optional[RunClient] = None,
        tenant_repository: Optional[TenantRepository] = None,
    ):
        self._thread_client = thread_client or ThreadClient()
        self._message_client = message_client or MessageClient()
        self._run_client = run_client or RunClient()
        self._tenant_repository = tenant_repository or TenantRepository()

        self._logger = logging.getLogger(__name__)

    def ask_question(self, question: str, tenant_id: UUID, thread_id: Optional[str]):
        tenant = self._tenant_repository.find_by_id(tenant_id)
        assistant_id = tenant.open_ai_chat_assistant_id
        vector_store_id = tenant.open_ai_vector_store_id

        if not thread_id:
            tool_resources = {"file_search": {"vector_store_ids": [vector_store_id]}}
            thread_id = self._thread_client.create_thread(tool_resources=tool_resources)

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
