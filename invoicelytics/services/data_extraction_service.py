import logging
import os
from typing import Optional
from uuid import UUID

from invoicelytics.assistants.data_extraction_assistant import DataExtractionAssistant
from invoicelytics.entities.domain_entities import InvoiceStatus
from invoicelytics.repository.invoice_repository import InvoiceRepository
from invoicelytics.services.base_service import BaseService


class DataExtractionService(BaseService):
    def __init__(
        self, invoice_repository: Optional[InvoiceRepository] = None, data_extraction_assistant: Optional[DataExtractionAssistant] = None
    ):
        self._logger = logging.getLogger(__name__)
        self._invoice_repository = invoice_repository or InvoiceRepository()
        self._data_extraction_assistant = data_extraction_assistant or DataExtractionAssistant()

    def _run(self, invoice_id: UUID, tenant_id: UUID):
        self._logger.info(f"Data extraction started, invoice_id: {invoice_id}, tenant_id: {tenant_id}")
        invoice = self._invoice_repository.find_by_id(invoice_id, tenant_id)
        extracted_data_points = self._data_extraction_assistant.extract_attributes(invoice)

        extracted_data_points["status"] = InvoiceStatus.PROCESSED

        self._invoice_repository.update(invoice, extracted_data_points)

    @staticmethod
    def _build_invoice_path(invoice_id: UUID, tenant_id: UUID):
        return os.path.join(os.environ["UPLOAD_FOLDER"], f"tenants/{tenant_id}/invoices/{invoice_id}.pdf")
