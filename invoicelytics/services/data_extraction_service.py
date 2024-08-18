import logging
from uuid import UUID


class DataExtractionService:
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def extract_data_from_invoice(self, invoice_id: UUID, tenant_id: UUID):
        self._logger.info(f"Data extraction started, invoice_id: {invoice_id}, tenant_id: {tenant_id}")
        pass
