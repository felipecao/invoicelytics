from temporalio import activity

from invoicelytics.run import get_activity_app
from invoicelytics.services.data_extraction_service import DataExtractionService
from invoicelytics.temporal.parameters import InvoiceInferenceWorkflowParams

_data_extraction_service = DataExtractionService()


@activity.defn
async def extract_invoice_data(p: InvoiceInferenceWorkflowParams) -> None:
    with get_activity_app().app_context():
        _data_extraction_service.execute(invoice_id=p.invoice_id, tenant_id=p.tenant_id)
