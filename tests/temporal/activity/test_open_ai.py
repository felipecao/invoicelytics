import asyncio
from unittest import TestCase
from unittest.mock import patch
from uuid import uuid4

from invoicelytics.temporal.activity.open_ai import upload_invoice_to_open_ai
from invoicelytics.temporal.parameters import InvoiceInferenceWorkflowParams
from tests import test_faker


class TestUploadInvoiceToOpenAi(TestCase):
    def setUp(self):
        self._invoice_id = uuid4()
        self._tenant_id = uuid4()

        self.params = InvoiceInferenceWorkflowParams(
            invoice_id=self._invoice_id, tenant_id=self._tenant_id, uploader_id=uuid4(), file_path=test_faker.file_path()
        )

    @patch("invoicelytics.temporal.activity.open_ai._file_client")
    @patch("invoicelytics.temporal.activity.open_ai.UploadFolder")
    def test_extract_invoice_data_success(self, mock_upload_folder, mock_file_client):
        file_id = test_faker.ssn()
        file_contents = b"fake file contents"

        mock_upload_folder.read_file.return_value = file_contents
        mock_file_client.upload_file.return_value = file_id

        result = asyncio.run(upload_invoice_to_open_ai(self.params))

        self.assertEqual(file_id, result)

        call_args = mock_file_client.upload_file.call_args
        invoice_file = call_args[0][0]

        self.assertEqual(invoice_file.filename, f"{self.params.invoice_id}.pdf")
        self.assertEqual(invoice_file.contents, file_contents)
        self.assertEqual(invoice_file.content_type, "application/pdf")
