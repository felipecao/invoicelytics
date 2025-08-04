from typing import Optional
from uuid import UUID

from flask import current_app
from temporalio.client import Client

from invoicelytics.temporal.queues import INVOICE_QUEUE_NAME
from invoicelytics.temporal.workflow.invoice import InvoiceInferenceWorkflowParams, InvoiceInferenceWorkflow


class InvoiceCreationService:
    def __init__(
        self,
        temporal_client: Optional[Client] = None,
    ):
        self._temporal_client = temporal_client

    async def create_invoice(self, invoice_id: UUID, file_path: str, uploader_id: UUID, tenant_id: UUID):
        client = self._temporal_client or current_app.temporal_client

        params = InvoiceInferenceWorkflowParams(
            invoice_id=invoice_id,
            tenant_id=tenant_id,
            file_path=file_path,
            uploader_id=uploader_id,
        )

        await client.start_workflow(
            InvoiceInferenceWorkflow.run,
            params,
            id="invoice-workflow",
            task_queue=INVOICE_QUEUE_NAME,
        )
