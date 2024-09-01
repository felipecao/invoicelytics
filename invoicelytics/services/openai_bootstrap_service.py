import logging
from typing import Optional
from uuid import UUID

from invoicelytics.assistants.assistant_builder import AssistantBuilder
from invoicelytics.assistants.chat_assistant import ChatAssistant
from invoicelytics.integrations.open_ai.vector_store_client import VectorStoreClient
from invoicelytics.repository.tenant_repository import TenantRepository
from invoicelytics.services.base_service import BaseService


class OpenAiBootstrapService(BaseService):
    def __init__(
        self,
        tenant_repository: Optional[TenantRepository] = None,
        chat_assistant: Optional[ChatAssistant] = None,
        vector_store_client: Optional[VectorStoreClient] = None,
        assistant_builder: Optional[AssistantBuilder] = None,
    ):
        self._logger = logging.getLogger(__name__)
        self._tenant_repository = tenant_repository or TenantRepository()
        self._chat_assistant = chat_assistant or ChatAssistant()
        self._vector_store_client = vector_store_client or VectorStoreClient()
        self._assistant_builder = assistant_builder or AssistantBuilder()

    def _run(self):
        self._logger.info("Started initializing open ai assets")

        for tenant in self._tenant_repository.find_all():
            vector_store_id = self._create_vector_store_if_not_exists(tenant.id, tenant.open_ai_vector_store_id)
            chat_assistant_id = self._create_chat_assistant_if_not_exists(tenant.id, vector_store_id)

            self._tenant_repository.update(tenant, vector_store_id, chat_assistant_id)

        self._logger.info("Finished initializing open ai assets")

    def _create_vector_store_if_not_exists(self, tenant_id: UUID, vector_store_id_on_db: Optional[str]) -> str:
        if vector_store_id_on_db is not None:
            return vector_store_id_on_db

        return self._vector_store_client.create(name=self._build_vector_store_name(tenant_id))

    def _create_chat_assistant_if_not_exists(self, tenant_id: UUID, vector_store_id: str) -> str:
        return self._assistant_builder.create_assistant_if_does_not_exist(
            name=f"{ChatAssistant.NAME_PREFIX}_{tenant_id}",
            description="Emma is an accounting assistant who provides information about invoices uploaded into the system",
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
            instructions="""
                You are Emma, an accounting assistant who provides information about invoices uploaded into the system.
                Your role is to process the invoices uploaded into our storage and provide accurate and precise information about them.
                Whenever you don't know how to answer a question, you simply say "I don't know". You don't create imaginary values.
                """,
        )

    @staticmethod
    def _build_vector_store_name(tenant_id: UUID) -> str:
        return f"vs_{tenant_id}"
