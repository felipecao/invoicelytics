import os
from uuid import UUID

from temporalio import activity

from invoicelytics.support.os_utils import UploadFolder
from invoicelytics.temporal.parameters import InvoiceInferenceWorkflowParams


@activity.defn
async def move_invoice_to_tenant_folder(p: InvoiceInferenceWorkflowParams) -> str:
    new_file_path = _generate_new_file_path(p.tenant_id, p.invoice_id)
    UploadFolder.move_file(p.file_path, new_file_path)
    return new_file_path


def _generate_new_file_path(tenant_id: UUID, invoice_id: UUID) -> str:
    new_directory = os.path.join(os.environ["UPLOAD_FOLDER"], f"tenants/{tenant_id}/invoices")
    new_file_path = os.path.join(new_directory, f"{invoice_id}.pdf")
    return new_file_path
