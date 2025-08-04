from temporalio import activity

from invoicelytics.entities.domain_entities import Invoice, InvoiceStatus
from invoicelytics.repository.invoice_repository import InvoiceRepository
from invoicelytics.run import get_activity_app
from invoicelytics.temporal.parameters import SaveInvoiceParams

_invoice_repository = InvoiceRepository()


@activity.defn
async def save_invoice_to_db(p: SaveInvoiceParams) -> None:
    with get_activity_app().app_context():
        _invoice_repository.save(
            Invoice(
                id=p.invoice_id,
                tenant_id=p.tenant_id,
                status=InvoiceStatus.CREATED,
                pdf_file_path=p.file_path,
                open_ai_pdf_file_id=p.open_ai_file_id,
                uploaded_by=p.uploader_id,
            )
        )
