import logging
from typing import Optional
from uuid import UUID

from openai.types.beta import Assistant

from invoicelytics.assistants.chat_assistant import ChatAssistant
from invoicelytics.integrations.open_ai.assistant_client import AssistantClient
from invoicelytics.integrations.open_ai.vector_store_client import VectorStoreClient
from invoicelytics.repository.tenant_repository import TenantRepository
from invoicelytics.services.base_service import BaseService


class OpenAiBootstrapService(BaseService):
    def __init__(
        self,
        tenant_repository: Optional[TenantRepository] = None,
        chat_assistant: Optional[ChatAssistant] = None,
        vector_store_client: Optional[VectorStoreClient] = None,
        assistant_client: Optional[AssistantClient] = None,
    ):
        self._logger = logging.getLogger(__name__)
        self._tenant_repository = tenant_repository or TenantRepository()
        self._chat_assistant = chat_assistant or ChatAssistant()
        self._vector_store_client = vector_store_client or VectorStoreClient()
        self._assistant_client = assistant_client or AssistantClient()

    def _run(self):
        self._logger.info("Started initializing open ai assets")

        for tenant in self._tenant_repository.find_all():
            vector_store_id = self._create_vector_store_if_not_exists(tenant.id, tenant.open_ai_vector_store_id)
            chat_assistant_id = self._create_chat_assistant_if_not_exists(tenant.id, vector_store_id, tenant.open_ai_chat_assistant_id)

            self._tenant_repository.update(tenant, vector_store_id, chat_assistant_id)
            self._logger.info(f"OpenAI assets successfully initialized for tenant, tenant_id: {tenant.id}")

        self._logger.info("Finished initializing open ai assets")

    def _create_vector_store_if_not_exists(self, tenant_id: UUID, vector_store_id_on_db: Optional[str]) -> str:
        if not vector_store_id_on_db:
            return self._vector_store_client.create(name=self._build_vector_store_name(tenant_id)).id

        if self._vector_store_client.find_by_id(vector_store_id_on_db) is not None:
            return vector_store_id_on_db

        return self._vector_store_client.create(name=self._build_vector_store_name(tenant_id)).id

    def _create_chat_assistant_if_not_exists(self, tenant_id: UUID, vector_store_id: str, assistant_id_on_db: Optional[str]) -> str:
        if not assistant_id_on_db:
            return self._create_assistant(tenant_id, vector_store_id).id

        if self._assistant_client.find_by_name(self._build_assistant_name(tenant_id)) is not None:
            return assistant_id_on_db

        return self._create_assistant(tenant_id, vector_store_id).id

    def _create_assistant(self, tenant_id: UUID, vector_store_id: str) -> Assistant:
        return self._assistant_client.create(
            name=self._build_assistant_name(tenant_id),
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
    def _build_assistant_name(tenant_id: UUID) -> str:
        return f"{ChatAssistant.NAME_PREFIX}_{tenant_id}"

    @staticmethod
    def _build_vector_store_name(tenant_id: UUID) -> str:
        return f"vs_{tenant_id}"
