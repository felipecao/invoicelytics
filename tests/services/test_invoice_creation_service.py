from unittest import TestCase
from unittest.mock import MagicMock, patch
from uuid import uuid4

from invoicelytics.entities.domain_entities import InvoiceStatus
from invoicelytics.repository.invoice_repository import InvoiceRepository
from invoicelytics.services.data_extraction_service import DataExtractionService
from invoicelytics.services.invoice_creation_service import InvoiceCreationService
from invoicelytics.support.os_utils import UploadFolder
from tests import test_faker


class TestInvoiceCreationService(TestCase):
    def setUp(self):
        self._mock_invoice_repository = MagicMock(spec=InvoiceRepository)
        self._mock_data_extraction_service = MagicMock(spec=DataExtractionService)
        self._mock_upload_folder = MagicMock(spec=UploadFolder)
        self._service = InvoiceCreationService(
            invoice_repository=self._mock_invoice_repository,
            data_extraction_service=self._mock_data_extraction_service,
            upload_folder=self._mock_upload_folder,
        )

    @patch.dict("os.environ", {"UPLOAD_FOLDER": "/tmp/test"})
    def test_create_invoice(self):
        file_path = test_faker.file_path(extension="pdf")
        invoice_id = uuid4()
        tenant_id = uuid4()

        self._service.create_invoice(invoice_id, file_path, tenant_id)

        args, kwargs = self._mock_upload_folder.move_file.call_args_list[0]
        self.assertEqual(file_path, args[0])
        self.assertEqual(f"/tmp/test/tenants/{tenant_id}/invoices/{invoice_id}.pdf", args[1])

        args, kwargs = self._mock_invoice_repository.save.call_args_list[0]
        self.assertEqual(invoice_id, args[0].id)
        self.assertEqual(tenant_id, args[0].tenant_id)
        self.assertEqual(InvoiceStatus.CREATED, args[0].status)
        self.assertEqual(f"/tmp/test/tenants/{tenant_id}/invoices/{invoice_id}.pdf", args[0].pdf_file_path)
