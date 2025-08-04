import logging
from datetime import timedelta
from typing import Any, Callable

from temporalio import workflow
from temporalio.common import RetryPolicy

from invoicelytics.temporal.parameters import InvoiceInferenceWorkflowParams, SaveInvoiceParams

with workflow.unsafe.imports_passed_through():
    from invoicelytics.temporal.activity.data_extraction import extract_invoice_data
    from invoicelytics.temporal.activity.db import save_invoice_to_db
    from invoicelytics.temporal.activity.filesystem import move_invoice_to_tenant_folder
    from invoicelytics.temporal.activity.open_ai import upload_invoice_to_open_ai


@workflow.defn
class InvoiceInferenceWorkflow:
    def __init__(self):
        self._default_timeout = timedelta(seconds=15)
        self._default_retry = RetryPolicy(
            backoff_coefficient=2.0,
            maximum_attempts=5,
            initial_interval=timedelta(seconds=1),
        )
        self._logger = logging.getLogger(__name__)

    @workflow.run
    async def run(self, p: InvoiceInferenceWorkflowParams) -> None:
        self._logger.info(f"start InvoicePipelineWorkflow, old file path: {p.file_path}")

        new_file_path = await self._execute(move_invoice_to_tenant_folder, p)
        self._logger.info(f"running InvoicePipelineWorkflow, new_file_path: {new_file_path}")

        p = InvoiceInferenceWorkflowParams(
            invoice_id=p.invoice_id,
            tenant_id=p.tenant_id,
            file_path=new_file_path,
            uploader_id=p.uploader_id,
        )

        file_id = await self._execute(upload_invoice_to_open_ai, p)
        self._logger.info(f"running InvoicePipelineWorkflow, file_id: {file_id}")

        s = SaveInvoiceParams(
            invoice_id=p.invoice_id,
            tenant_id=p.tenant_id,
            file_path=p.file_path,
            uploader_id=p.uploader_id,
            open_ai_file_id=file_id,
        )
        await self._execute(save_invoice_to_db, s)
        self._logger.info("running InvoicePipelineWorkflow, invoice saved to DB")

        await self._execute(extract_invoice_data, p, timeout=timedelta(seconds=30))
        self._logger.info("running InvoicePipelineWorkflow, invoice data extracted")

        self._logger.info("end InvoicePipelineWorkflow")

    async def _execute(self, activity: Callable, params: Any, timeout: timedelta = None) -> Any:
        return await workflow.execute_activity(
            activity, params, start_to_close_timeout=timeout or self._default_timeout, retry_policy=self._default_retry
        )
