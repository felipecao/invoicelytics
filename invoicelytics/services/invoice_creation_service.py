import logging
import os
import threading
from typing import Optional
from uuid import UUID

from invoicelytics.entities.domain_entities import Invoice, InvoiceStatus
from invoicelytics.repository.invoice_repository import InvoiceRepository
from invoicelytics.services.data_extraction_service import DataExtractionService
from invoicelytics.support.os_utils import UploadFolder


class InvoiceCreationService:
    def __init__(
        self,
        invoice_repository: Optional[InvoiceRepository] = None,
        data_extraction_service: Optional[DataExtractionService] = None,
        upload_folder: Optional[UploadFolder] = None,
    ):
        self._logger = logging.getLogger(__name__)
        self._invoice_repository = invoice_repository or InvoiceRepository()
        self._data_extraction_service = data_extraction_service or DataExtractionService()
        self._upload_folder = upload_folder or UploadFolder()

    def create_invoice(self, invoice_id: UUID, file_path: str, tenant_id: UUID):
        new_file_path = self._generate_new_file_path(tenant_id, invoice_id)

        self._upload_folder.move_file(file_path, new_file_path)
        self._invoice_repository.save(
            Invoice(
                id=invoice_id,
                tenant_id=tenant_id,
                status=InvoiceStatus.CREATED,
                pdf_file_path=new_file_path,
            )
        )
        self._fire_and_forget_data_extraction(invoice_id, tenant_id)

    @staticmethod
    def _generate_new_file_path(tenant_id: UUID, invoice_id: UUID) -> str:
        new_directory = os.path.join(os.environ["UPLOAD_FOLDER"], f"tenants/{tenant_id}/invoices")
        new_file_path = os.path.join(new_directory, f"{invoice_id}.pdf")
        return new_file_path

    def _fire_and_forget_data_extraction(self, invoice_id: UUID, tenant_id: UUID):
        threading.Thread(target=self._data_extraction_service.extract_data_from_invoice, args=(invoice_id, tenant_id)).start()
