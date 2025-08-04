import asyncio
from unittest import TestCase
from unittest.mock import MagicMock, patch
from uuid import uuid4

from invoicelytics.entities.domain_entities import InvoiceStatus
from invoicelytics.temporal.activity.db import save_invoice_to_db
from invoicelytics.temporal.parameters import SaveInvoiceParams
from tests import test_faker


class TestSaveInvoiceToDb(TestCase):
    def setUp(self):
        self.params = SaveInvoiceParams(
            invoice_id=uuid4(),
            tenant_id=uuid4(),
            uploader_id=uuid4(),
            file_path=test_faker.file_path(),
            open_ai_file_id=str(uuid4()),
        )

    @patch("invoicelytics.temporal.activity.db.get_activity_app")
    @patch("invoicelytics.temporal.activity.db._invoice_repository")
    def test_extract_invoice_data_success(self, mock_repository, mock_get_app):
        mock_app = MagicMock()
        mock_app_context = MagicMock()
        mock_app.app_context.return_value = mock_app_context
        mock_get_app.return_value = mock_app

        mock_repository.execute = MagicMock()

        asyncio.run(save_invoice_to_db(self.params))

        call_args = mock_repository.save.call_args
        inv = call_args[0][0]

        self.assertEqual(inv.id, self.params.invoice_id)
        self.assertEqual(inv.tenant_id, self.params.tenant_id)
        self.assertEqual(inv.status, InvoiceStatus.CREATED)
        self.assertEqual(inv.pdf_file_path, self.params.file_path)
        self.assertEqual(inv.open_ai_pdf_file_id, self.params.open_ai_file_id)
        self.assertEqual(inv.uploaded_by, self.params.uploader_id)
