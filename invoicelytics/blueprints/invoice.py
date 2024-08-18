import logging
from typing import Optional
from uuid import UUID, uuid4

from flask import Blueprint, flash, redirect, render_template, request, url_for

from invoicelytics.support.os_utils import UploadFolder
from invoicelytics.services.invoice_creation_service import InvoiceCreationService


class InvoiceBlueprint:
    def __init__(self, invoice_creation_service: Optional[InvoiceCreationService] = None, upload_folder: Optional[UploadFolder] = None):
        # TODO remove this fixed tenant id. This should be fetched from the accounts table based on the logged user.
        self._TENANT_ID = UUID("123e4567-e89b-12d3-a456-426614174000")
        # end TODO
        self._logger = logging.getLogger(__name__)
        self._invoice_creation_service = invoice_creation_service or InvoiceCreationService()
        self._upload_folder = upload_folder or UploadFolder()
        self.blueprint = Blueprint("invoice_bp", __name__)
        self._add_routes()

    def _add_routes(self):
        @self.blueprint.route("/upload", methods=["POST"])
        def post_uploaded_file():
            uploaded_files = request.files.values()

            for uploaded_file in uploaded_files:
                file_path = self._upload_folder.save_to_filesystem(uploaded_file)
                self._invoice_creation_service.create_invoice(uuid4(), file_path, self._TENANT_ID)
                self._logger.info(f"File successfully uploaded: {file_path}")

            flash("Your upload was successful")
            return redirect(url_for("invoice_bp.load_upload_page"))

        @self.blueprint.route("/upload", methods=["GET"])
        def load_upload_page():
            return render_template("upload.html")
