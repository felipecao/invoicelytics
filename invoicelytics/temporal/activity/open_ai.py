from temporalio import activity

from invoicelytics.data_structures.uploaded_file import UploadedFile
from invoicelytics.integrations.open_ai.file_client import FileClient
from invoicelytics.support.os_utils import UploadFolder
from invoicelytics.temporal.parameters import InvoiceInferenceWorkflowParams


_file_client = FileClient()


@activity.defn
async def upload_invoice_to_open_ai(params: InvoiceInferenceWorkflowParams) -> str:
    invoice_contents = UploadFolder.read_file(params.file_path)
    invoice_file = UploadedFile(f"{params.invoice_id}.pdf", invoice_contents, "application/pdf")
    return _file_client.upload_file(invoice_file)
