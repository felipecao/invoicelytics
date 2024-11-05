from unittest import TestCase
from unittest.mock import MagicMock, patch
from uuid import uuid4

from invoicelytics.entities.domain_entities import Invoice, InvoiceStatus
from invoicelytics.integrations.open_ai.file_client import FileClient
from invoicelytics.integrations.open_ai.vector_store_client import VectorStoreClient
from invoicelytics.repository.invoice_repository import InvoiceRepository
from invoicelytics.repository.tenant_repository import TenantRepository
from invoicelytics.services.invoice_approval_service import InvoiceApprovalService
from invoicelytics.data_structures.uploaded_file import UploadedFile


class TestInvoiceApprovalService(TestCase):
    def setUp(self):
        self.mock_invoice_repository = MagicMock(spec=InvoiceRepository)
        self.mock_tenant_repository = MagicMock(spec=TenantRepository)
        self.mock_file_client = MagicMock(spec=FileClient)
        self.mock_vector_store_client = MagicMock(spec=VectorStoreClient)
        self.service = InvoiceApprovalService(
            invoice_repository=self.mock_invoice_repository,
            tenant_repository=self.mock_tenant_repository,
            file_client=self.mock_file_client,
            vector_store_client=self.mock_vector_store_client,
        )

    @patch("invoicelytics.services.invoice_approval_service.to_json_bytes")
    def test_run(self, mock_to_json_bytes):
        invoice_id = uuid4()
        tenant_id = uuid4()
        logged_user_id = uuid4()
        file_id = "file_id"
        vector_store_id = "vector_store_id"
        mock_invoice = MagicMock(spec=Invoice)
        mock_invoice.id = invoice_id
        mock_invoice.to_dict.return_value = {"key": "value"}
        mock_to_json_bytes.return_value = b'{"key": "value"}'

        self.mock_invoice_repository.find_by_id.return_value = mock_invoice
        self.mock_file_client.upload_file.return_value = file_id
        self.mock_vector_store_client.upload_files_by_ids.return_value = None
        self.mock_tenant_repository.find_by_id.return_value = MagicMock(open_ai_vector_store_id=vector_store_id)

        attributes_to_update = {"some_key": "some_value"}

        self.service._run(invoice_id, logged_user_id, tenant_id, attributes_to_update)

        self.mock_invoice_repository.find_by_id.assert_called_once_with(invoice_id, tenant_id)
        self.mock_file_client.upload_file.assert_called_once_with(
            UploadedFile(f"{invoice_id}.json", b'{"key": "value"}', "application/json")
        )
        self.mock_vector_store_client.upload_files_by_ids.assert_called_once_with(vector_store_id, [file_id])
        self.mock_invoice_repository.update.assert_called_once_with(
            mock_invoice,
            {"some_key": "some_value", "status": InvoiceStatus.APPROVED, "open_ai_json_file_id": file_id, "approved_by": logged_user_id},
        )

    @patch("invoicelytics.services.invoice_approval_service.to_json_bytes")
    def test_invoice_does_not_exist(self, mock_to_json_bytes):
        invoice_id = uuid4()
        tenant_id = uuid4()
        logged_user_id = uuid4()
        mock_invoice = MagicMock(spec=Invoice)
        mock_invoice.to_dict.return_value = {"key": "value"}
        mock_to_json_bytes.return_value = b'{"key": "value"}'

        self.mock_invoice_repository.find_by_id.return_value = None

        attributes_to_update = {"some_key": "some_value"}

        self.service._run(invoice_id, logged_user_id, tenant_id, attributes_to_update)

        self.mock_invoice_repository.find_by_id.assert_called_once_with(invoice_id, tenant_id)
        self.mock_file_client.upload_file.assert_not_called()
        self.mock_vector_store_client.upload_files_by_ids.assert_not_called()
        self.mock_invoice_repository.update.assert_not_called()
