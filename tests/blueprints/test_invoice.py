from io import BytesIO
from unittest import TestCase
from unittest.mock import patch, MagicMock, ANY
from uuid import UUID, uuid4

from invoicelytics.entities.domain_entities import Invoice, InvoiceStatus
from invoicelytics.repository.invoice_repository import InvoiceRepository
from invoicelytics.services.invoice_approval_service import InvoiceApprovalService
from tests import test_faker

from flask import Flask

from invoicelytics.blueprints.invoice import InvoiceBlueprint
from invoicelytics.support.os_utils import UploadFolder
from invoicelytics.services.invoice_creation_service import InvoiceCreationService


class TestInvoiceBlueprint(TestCase):
    def setUp(self):
        self._mock_invoice_creation_service = MagicMock(spec=InvoiceCreationService)
        self._mock_invoice_approval_service = MagicMock(spec=InvoiceApprovalService)
        self._mock_upload_folder = MagicMock(spec=UploadFolder)
        self._mock_invoice_repository = MagicMock(spec=InvoiceRepository)
        self.app = Flask(__name__)
        self.invoice_blueprint = InvoiceBlueprint(
            invoice_creation_service=self._mock_invoice_creation_service,
            invoice_approval_service=self._mock_invoice_approval_service,
            upload_folder=self._mock_upload_folder,
            invoice_repository=self._mock_invoice_repository,
        )
        self.app.register_blueprint(self.invoice_blueprint.blueprint)
        self.client = self.app.test_client()

    @patch("invoicelytics.blueprints.invoice.flash")
    def test_post_uploaded_file(self, mock_flash):
        file_contents = BytesIO(b"my file contents")
        file_name = test_faker.file_name(extension="pdf")
        file_path = test_faker.file_path()
        data = {
            "file": (file_contents, file_name),
        }

        self._mock_upload_folder.save_to_filesystem.return_value = file_path
        mock_flash.return_value = True

        response = self.client.post("/upload", data=data, content_type="multipart/form-data")

        self._mock_invoice_creation_service.create_invoice.assert_called_once_with(
            ANY, file_path, UUID("123e4567-e89b-12d3-a456-426614174000")
        )
        self.assertEqual(response.status_code, 302)

    @patch("invoicelytics.blueprints.invoice.render_template")
    def test_load_upload_page(self, mock_render_template):
        mock_render_template.return_value = "mock_rendered_template"

        response = self.client.get("/upload")

        mock_render_template.assert_called_once_with("upload.html")
        self.assertEqual(response.data, b"mock_rendered_template")

    @patch("invoicelytics.blueprints.invoice.render_template")
    def test_list_processed_invoices(self, mock_render_template):
        mock_render_template.return_value = "mock_rendered_template"
        mock_invoices = [
            Invoice(
                invoice_number="INV-001",
                payee_name="John Doe",
                due_date="2023-10-01",
                total_amount=100.0,
            ),
            Invoice(
                invoice_number="INV-002",
                payee_name="Jane Smith",
                due_date="2023-10-02",
                total_amount=200.0,
            ),
        ]
        self._mock_invoice_repository.find_by_status.return_value = mock_invoices

        response = self.client.get("/invoices")

        mock_render_template.assert_called_once_with("home.html", invoices=mock_invoices)
        self.assertEqual(response.data, b"mock_rendered_template")
        self.assertEqual(response.status_code, 200)

    @patch("invoicelytics.blueprints.invoice.render_template")
    def test_view_invoice(self, mock_render_template):
        invoice_id = uuid4()
        mock_invoice = Invoice(
            id=invoice_id,
            invoice_number="INV-001",
            payee_name="John Doe",
            due_date="2023-10-01",
            total_amount=100.0,
            status="processed",
            pdf_file_path="/path/to/invoice.pdf",
        )
        self._mock_invoice_repository.find_by_id.return_value = mock_invoice
        mock_render_template.return_value = "mock_rendered_template"

        response = self.client.get(f"/invoice/{invoice_id}")

        self._mock_invoice_repository.find_by_id.assert_called_once_with(invoice_id, UUID("123e4567-e89b-12d3-a456-426614174000"))
        mock_render_template.assert_called_once_with("invoice_detail.html", invoice=mock_invoice)
        self.assertEqual(response.data, b"mock_rendered_template")
        self.assertEqual(response.status_code, 200)

    @patch("invoicelytics.blueprints.invoice.send_file")
    def test_serve_invoice_pdf(self, mock_send_file):
        invoice_id = uuid4()
        mock_invoice = Invoice(
            id=invoice_id,
            invoice_number="INV-001",
            payee_name="John Doe",
            due_date="2023-10-01",
            total_amount=100.0,
            status="processed",
            pdf_file_path="/path/to/invoice.pdf",
        )
        self._mock_invoice_repository.find_by_id.return_value = mock_invoice
        mock_send_file.return_value = "mock_pdf_file"

        response = self.client.get(f"/invoice/pdf/{invoice_id}")

        self._mock_invoice_repository.find_by_id.assert_called_once_with(invoice_id, UUID("123e4567-e89b-12d3-a456-426614174000"))
        mock_send_file.assert_called_once_with("/path/to/invoice.pdf")
        self.assertEqual(response.data, b"mock_pdf_file")
        self.assertEqual(response.status_code, 200)

    def test_serve_invoice_pdf_not_found(self):
        invoice_id = uuid4()
        self._mock_invoice_repository.find_by_id.return_value = None

        response = self.client.get(f"/invoice/pdf/{invoice_id}")

        self._mock_invoice_repository.find_by_id.assert_called_once_with(invoice_id, UUID("123e4567-e89b-12d3-a456-426614174000"))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, b"File not found")

    @patch("invoicelytics.blueprints.invoice.render_template")
    @patch("invoicelytics.blueprints.invoice.flash")
    def test_approve_invoice_success(self, mock_flash, mock_render_template):
        invoice_id = uuid4()
        mock_invoice = Invoice(
            id=invoice_id,
            invoice_number="INV-001",
            payee_name="John Doe",
            due_date="2023-10-01",
            total_amount=100.0,
            status="created",
        )

        self._mock_invoice_repository.find_by_id.return_value = mock_invoice
        mock_render_template.return_value = "mock_rendered_template"

        data = {
            "invoice_number": "INV-001",
            "payee_name": "John Doe",
            "due_date": "2023-10-01",
            "total_amount": "100.0",
        }

        response = self.client.post(f"/invoice/approve/{invoice_id}", data=data, content_type="multipart/form-data")

        self._mock_invoice_approval_service.execute.assert_called_once_with(
            invoice_id,
            UUID("123e4567-e89b-12d3-a456-426614174000"),
            {
                "invoice_number": "INV-001",
                "payee_name": "John Doe",
                "due_date": "2023-10-01",
                "total_amount": "100.0",
            },
        )
        mock_flash.assert_called_once_with("Invoice approved successfully")
        mock_render_template.assert_called_once_with("home.html", invoices=ANY)
        self.assertEqual(response.data, b"mock_rendered_template")
        self.assertEqual(response.status_code, 200)

    @patch("invoicelytics.blueprints.invoice.render_template")
    @patch("invoicelytics.blueprints.invoice.flash")
    def test_approve_invoice_not_found(self, mock_flash, mock_render_template):
        invoice_id = uuid4()

        mock_render_template.return_value = "mock_rendered_template"
        self._mock_invoice_repository.find_by_id.return_value = None

        response = self.client.post(f"/invoice/approve/{invoice_id}")

        self._mock_invoice_repository.update.assert_not_called()
        mock_flash.assert_called_once_with("Invoice not found", "error")
        mock_render_template.assert_called_once_with("home.html", invoices=ANY)
        self.assertEqual(response.data, b"mock_rendered_template")
        self.assertEqual(response.status_code, 200)

    @patch("invoicelytics.blueprints.invoice.render_template")
    @patch("invoicelytics.blueprints.invoice.flash")
    def test_reject_invoice_success(self, mock_flash, mock_render_template):
        invoice_id = uuid4()
        mock_invoice = Invoice(
            id=invoice_id,
            invoice_number="INV-001",
            payee_name="John Doe",
            due_date="2023-10-01",
            total_amount=100.0,
            status="created",
        )

        self._mock_invoice_repository.find_by_id.return_value = mock_invoice
        mock_render_template.return_value = "mock_rendered_template"

        response = self.client.post(f"/invoice/reject/{invoice_id}", data={}, content_type="multipart/form-data")

        self._mock_invoice_repository.update.assert_called_once_with(
            mock_invoice,
            {
                "status": InvoiceStatus.REJECTED,
            },
        )
        mock_flash.assert_called_once_with("Invoice rejected successfully")
        mock_render_template.assert_called_once_with("home.html", invoices=ANY)
        self.assertEqual(response.data, b"mock_rendered_template")
        self.assertEqual(response.status_code, 200)

    @patch("invoicelytics.blueprints.invoice.render_template")
    @patch("invoicelytics.blueprints.invoice.flash")
    def test_reject_invoice_not_found(self, mock_flash, mock_render_template):
        invoice_id = uuid4()

        mock_render_template.return_value = "mock_rendered_template"
        self._mock_invoice_repository.find_by_id.return_value = None

        response = self.client.post(f"/invoice/reject/{invoice_id}")

        self._mock_invoice_repository.update.assert_not_called()
        mock_flash.assert_called_once_with("Invoice not found", "error")
        mock_render_template.assert_called_once_with("home.html", invoices=ANY)
        self.assertEqual(response.data, b"mock_rendered_template")
        self.assertEqual(response.status_code, 200)
