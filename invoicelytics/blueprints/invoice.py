import logging
from typing import Optional
from uuid import UUID, uuid4

from flask import Blueprint, flash, redirect, render_template, request, url_for, send_file
from flask_login import login_required, current_user

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
        @login_required
        def post_uploaded_file():
            _ensure_openai_assets_are_created(current_user.tenant_id)

            uploaded_files = request.files.values()

            for uploaded_file in uploaded_files:
                file_path = self._upload_folder.save_to_filesystem(uploaded_file)
                self._invoice_creation_service.create_invoice(uuid4(), file_path, current_user.tenant_id)
                self._logger.info(f"File successfully uploaded: {file_path}")

            flash("Your upload was successful. Please wait a few seconds while we process your invoice...")
            return redirect(url_for("invoice_bp.load_upload_page"))

        @self.blueprint.route("/upload", methods=["GET"])
        @login_required
        def load_upload_page():
            _ensure_openai_assets_are_created(current_user.tenant_id)
            return render_template("upload.html")

        @self.blueprint.route("/invoices", methods=["GET"])
        @login_required
        def list_processed_invoices():
            invoices = self._invoice_repository.find_by_status(InvoiceStatus.PROCESSED, current_user.tenant_id)
            approved_invoices = self._invoice_repository.find_by_status(InvoiceStatus.APPROVED, current_user.tenant_id)
            return render_template("list_invoices.html", invoices=invoices, approved_invoices=approved_invoices)

        @self.blueprint.route("/invoice/<uuid:invoice_id>", methods=["GET"])
        @login_required
        def view_invoice(invoice_id):
            invoice = self._invoice_repository.find_by_id(invoice_id, current_user.tenant_id)
            readonly = request.args.get("readonly", "false").lower() == "true"
            return render_template("invoice_detail.html", invoice=invoice, readonly=readonly)

        @self.blueprint.route("/invoice/pdf/<uuid:invoice_id>", methods=["GET"])
        @login_required
        def serve_invoice_pdf(invoice_id):
            invoice = self._invoice_repository.find_by_id(invoice_id, current_user.tenant_id)
            if invoice and invoice.pdf_file_path:
                return send_file(invoice.pdf_file_path)
            else:
                return "File not found", 404

        @self.blueprint.route("/invoice/approve/<uuid:invoice_id>", methods=["POST"])
        @login_required
        def approve_invoice(invoice_id):
            _ensure_openai_assets_are_created(current_user.tenant_id)
            invoice = self._invoice_repository.find_by_id(invoice_id, current_user.tenant_id)

            if invoice:
                self._invoice_approval_service.execute(
                    invoice_id,
                    current_user.tenant_id,
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
        @login_required
        def reject_invoice(invoice_id):
            invoice = self._invoice_repository.find_by_id(invoice_id, current_user.tenant_id)

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
