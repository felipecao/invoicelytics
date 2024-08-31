import logging
import os
import threading
from typing import Optional
from uuid import UUID

from invoicelytics.data_structures.uploaded_file import UploadedFile
from invoicelytics.entities.domain_entities import Invoice, InvoiceStatus
from invoicelytics.integrations.open_ai.file_client import FileClient
from invoicelytics.repository.invoice_repository import InvoiceRepository
from invoicelytics.services.data_extraction_service import DataExtractionService
from invoicelytics.support.os_utils import UploadFolder


class InvoiceCreationService:
    def __init__(
        self,
        invoice_repository: Optional[InvoiceRepository] = None,
        data_extraction_service: Optional[DataExtractionService] = None,
        upload_folder: Optional[UploadFolder] = None,
        file_client: Optional[FileClient] = None,
    ):
        self._logger = logging.getLogger(__name__)
        self._invoice_repository = invoice_repository or InvoiceRepository()
        self._data_extraction_service = data_extraction_service or DataExtractionService()
        self._upload_folder = upload_folder or UploadFolder()
        self._file_client = file_client or FileClient()

    def create_invoice(self, invoice_id: UUID, file_path: str, tenant_id: UUID):
        new_file_path = self._move_invoice_to_tenant_folder(invoice_id, file_path, tenant_id)
        file_id = self._upload_invoice_to_open_ai(invoice_id, new_file_path)

        self._invoice_repository.save(
            Invoice(
                id=invoice_id,
                tenant_id=tenant_id,
                status=InvoiceStatus.CREATED,
                pdf_file_path=new_file_path,
                open_ai_pdf_file_id=file_id,
            )
        )

        self._fire_and_forget_data_extraction(invoice_id, tenant_id)

    def _move_invoice_to_tenant_folder(self, invoice_id: UUID, file_path: str, tenant_id: UUID) -> str:
        new_file_path = self._generate_new_file_path(tenant_id, invoice_id)
        self._upload_folder.move_file(file_path, new_file_path)
        return new_file_path

    @staticmethod
    def _generate_new_file_path(tenant_id: UUID, invoice_id: UUID) -> str:
        new_directory = os.path.join(os.environ["UPLOAD_FOLDER"], f"tenants/{tenant_id}/invoices")
        new_file_path = os.path.join(new_directory, f"{invoice_id}.pdf")
        return new_file_path

    def _upload_invoice_to_open_ai(self, invoice_id: UUID, file_path: str) -> str:
        invoice_contents = self._upload_folder.read_file(file_path)
        invoice_file = UploadedFile(f"{invoice_id}.pdf", invoice_contents, "application/pdf")
        return self._file_client.upload_file(invoice_file)

    def _fire_and_forget_data_extraction(self, invoice_id: UUID, tenant_id: UUID):
        threading.Thread(target=self._data_extraction_service.execute, args=(invoice_id, tenant_id)).start()
