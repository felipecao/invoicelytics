import asyncio
from unittest import TestCase
from unittest.mock import MagicMock, patch
from uuid import uuid4

from invoicelytics.temporal.activity.data_extraction import extract_invoice_data
from invoicelytics.temporal.parameters import InvoiceInferenceWorkflowParams
from tests import test_faker


class TestExtractInvoiceData(TestCase):
    def setUp(self):
        self._invoice_id = uuid4()
        self._tenant_id = uuid4()

        self.params = InvoiceInferenceWorkflowParams(
            invoice_id=self._invoice_id, tenant_id=self._tenant_id, uploader_id=uuid4(), file_path=test_faker.file_path()
        )

    @patch("invoicelytics.temporal.activity.data_extraction.get_activity_app")
    @patch("invoicelytics.temporal.activity.data_extraction._data_extraction_service")
    def test_extract_invoice_data_success(self, mock_service, mock_get_app):
        mock_app = MagicMock()
        mock_app_context = MagicMock()
        mock_app.app_context.return_value = mock_app_context
        mock_get_app.return_value = mock_app

        mock_service.execute = MagicMock()

        asyncio.run(extract_invoice_data(self.params))

        mock_service.execute.assert_called_once_with(invoice_id=self._invoice_id, tenant_id=self._tenant_id)
