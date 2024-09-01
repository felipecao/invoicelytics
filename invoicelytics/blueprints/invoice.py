import logging
from typing import Optional
from uuid import UUID, uuid4

from flask import Blueprint, flash, redirect, render_template, request, url_for, send_file

from invoicelytics.entities.domain_entities import InvoiceStatus
from invoicelytics.repository.invoice_repository import InvoiceRepository
from invoicelytics.repository.tenant_repository import TenantRepository
from invoicelytics.services.invoice_approval_service import InvoiceApprovalService
from invoicelytics.services.invoice_creation_service import InvoiceCreationService
from invoicelytics.support.os_utils import UploadFolder


class InvoiceBlueprint:
    def __init__(
        self,
        invoice_creation_service: Optional[InvoiceCreationService] = None,
        invoice_approval_service: Optional[InvoiceApprovalService] = None,
        upload_folder: Optional[UploadFolder] = None,
        invoice_repository: Optional[InvoiceRepository] = None,
        tenant_repository: Optional[TenantRepository] = None,
    ):
        # TODO remove this fixed tenant id. This should be fetched from the accounts table based on the logged user.
        self._TENANT_ID = UUID("123e4567-e89b-12d3-a456-426614174000")
        # end TODO
        self._logger = logging.getLogger(__name__)
        self._invoice_creation_service = invoice_creation_service or InvoiceCreationService()
        self._invoice_approval_service = invoice_approval_service or InvoiceApprovalService()
        self._upload_folder = upload_folder or UploadFolder()
        self._invoice_repository = invoice_repository or InvoiceRepository()
        self._tenant_repository = tenant_repository or TenantRepository()
        self.blueprint = Blueprint("invoice_bp", __name__)
        self._add_routes()

    def _add_routes(self):
        @self.blueprint.route("/upload", methods=["POST"])
        def post_uploaded_file():
            _ensure_openai_assets_are_created(self._TENANT_ID)

            uploaded_files = request.files.values()

            for uploaded_file in uploaded_files:
                file_path = self._upload_folder.save_to_filesystem(uploaded_file)
                self._invoice_creation_service.create_invoice(uuid4(), file_path, self._TENANT_ID)
                self._logger.info(f"File successfully uploaded: {file_path}")

            flash("Your upload was successful. Please wait a few seconds while we process your invoice...")
            return redirect(url_for("invoice_bp.load_upload_page"))

        @self.blueprint.route("/upload", methods=["GET"])
        def load_upload_page():
            _ensure_openai_assets_are_created(self._TENANT_ID)
            return render_template("upload.html")

        @self.blueprint.route("/invoices", methods=["GET"])
        def list_processed_invoices():
            invoices = self._invoice_repository.find_by_status(InvoiceStatus.PROCESSED, self._TENANT_ID)
            return render_template("home.html", invoices=invoices)

        @self.blueprint.route("/invoice/<uuid:invoice_id>", methods=["GET"])
        def view_invoice(invoice_id):
            invoice = self._invoice_repository.find_by_id(invoice_id, self._TENANT_ID)
            return render_template("invoice_detail.html", invoice=invoice)

        @self.blueprint.route("/invoice/pdf/<uuid:invoice_id>", methods=["GET"])
        def serve_invoice_pdf(invoice_id):
            invoice = self._invoice_repository.find_by_id(invoice_id, self._TENANT_ID)
            if invoice and invoice.pdf_file_path:
                return send_file(invoice.pdf_file_path)
            else:
                return "File not found", 404

        @self.blueprint.route("/invoice/approve/<uuid:invoice_id>", methods=["POST"])
        def approve_invoice(invoice_id):
            _ensure_openai_assets_are_created(self._TENANT_ID)
            invoice = self._invoice_repository.find_by_id(invoice_id, self._TENANT_ID)

            if invoice:
                self._invoice_approval_service.execute(
                    invoice_id,
                    self._TENANT_ID,
                    {
                        "invoice_number": request.form.get("invoice_number"),
                        "payee_name": request.form.get("payee_name"),
                        "due_date": request.form.get("due_date"),
                        "total_amount": request.form.get("total_amount"),
                    },
                )
                flash("Invoice approved successfully")
            else:
                flash("Invoice not found", "error")
            return list_processed_invoices()

        @self.blueprint.route("/invoice/reject/<uuid:invoice_id>", methods=["POST"])
        def reject_invoice(invoice_id):
            invoice = self._invoice_repository.find_by_id(invoice_id, self._TENANT_ID)

            if invoice:
                self._invoice_repository.update(
                    invoice,
                    {
                        "status": InvoiceStatus.REJECTED,
                    },
                )
                flash("Invoice rejected successfully")
            else:
                flash("Invoice not found", "error")

            return list_processed_invoices()

        def _ensure_openai_assets_are_created(tenant_id: UUID):
            tenant = self._tenant_repository.find_by_id(tenant_id)

            if not tenant.open_ai_vector_store_id or not tenant.open_ai_chat_assistant_id:
                raise ValueError("OpenAI assets have not been setup. Please use the bootstrap endpoint first.")
