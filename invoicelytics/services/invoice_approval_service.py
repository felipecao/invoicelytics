from typing import Optional
from uuid import UUID

from invoicelytics.data_structures.uploaded_file import UploadedFile
from invoicelytics.entities.domain_entities import InvoiceStatus
from invoicelytics.integrations.open_ai.file_client import FileClient
from invoicelytics.integrations.open_ai.vector_store_client import VectorStoreClient
from invoicelytics.repository.invoice_repository import InvoiceRepository
from invoicelytics.repository.tenant_repository import TenantRepository
from invoicelytics.services.base_service import BaseService
from invoicelytics.support.helpers import to_json_bytes


class InvoiceApprovalService(BaseService):
    def __init__(
        self,
        invoice_repository: Optional[InvoiceRepository] = None,
        tenant_repository: Optional[TenantRepository] = None,
        file_client: Optional[FileClient] = None,
        vector_store_client: Optional[VectorStoreClient] = None,
    ):
        self._invoice_repository = invoice_repository or InvoiceRepository()
        self._tenant_repository = tenant_repository or TenantRepository()
        self._file_client = file_client or FileClient()
        self._vector_store_client = vector_store_client or VectorStoreClient()

    def _run(self, invoice_id: UUID, tenant_id: UUID, attributes_to_update: dict):
        invoice = self._invoice_repository.find_by_id(invoice_id, tenant_id)

        if invoice:
            file = UploadedFile(f"{invoice_id}.json", to_json_bytes(invoice.to_dict()), "application/json")
            vector_store_id = self._create_vector_store_if_not_exists(tenant_id)
            file_id = self._file_client.upload_file(file)

            self._vector_store_client.upload_files_by_ids(vector_store_id, [file_id])

            attributes_to_update["status"] = InvoiceStatus.APPROVED
            attributes_to_update["open_ai_json_file_id"] = file_id
            self._invoice_repository.update(invoice, attributes_to_update)

    def _create_vector_store_if_not_exists(self, tenant_id: UUID) -> str:
        tenant_instance = self._tenant_repository.find_by_id(tenant_id)

        if tenant_instance.open_ai_vector_store_id:
            return tenant_instance.open_ai_vector_store_id

        vs_id = self._vector_store_client.create()
        self._tenant_repository.update(tenant_instance, vs_id)

        return vs_id
