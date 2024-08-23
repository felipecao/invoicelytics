from unittest import TestCase
from unittest.mock import MagicMock
from uuid import uuid4

from invoicelytics.assistants.data_extraction_assistant import DataExtractionAssistant
from invoicelytics.entities.domain_entities import Invoice, InvoiceStatus
from invoicelytics.repository.invoice_repository import InvoiceRepository
from invoicelytics.services.data_extraction_service import DataExtractionService


class TestDataExtractionService(TestCase):
    def setUp(self):
        self.mock_invoice_repository = MagicMock(spec=InvoiceRepository)
        self.mock_data_extraction_assistant = MagicMock(spec=DataExtractionAssistant)
        self.service = DataExtractionService(
            invoice_repository=self.mock_invoice_repository, data_extraction_assistant=self.mock_data_extraction_assistant
        )

    def test_run(self):
        invoice_id = uuid4()
        tenant_id = uuid4()
        mock_invoice = MagicMock(spec=Invoice)

        self.mock_invoice_repository.find_by_id.return_value = mock_invoice
        self.mock_data_extraction_assistant.extract_attributes.return_value = {"some_key": "some_value"}

        self.service._run(invoice_id, tenant_id)

        self.mock_invoice_repository.find_by_id.assert_called_once_with(invoice_id, tenant_id)
        self.mock_data_extraction_assistant.extract_attributes.assert_called_once_with(mock_invoice)
        self.mock_invoice_repository.update.assert_called_once_with(
            mock_invoice, {"some_key": "some_value", "status": InvoiceStatus.PROCESSED}
        )
