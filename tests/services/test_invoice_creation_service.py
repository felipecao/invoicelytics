import asyncio
from unittest import TestCase
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4

from temporalio.client import Client

from invoicelytics.services.invoice_creation_service import InvoiceCreationService
from invoicelytics.temporal.parameters import InvoiceInferenceWorkflowParams
from invoicelytics.temporal.queues import INVOICE_QUEUE_NAME
from invoicelytics.temporal.workflow.invoice import InvoiceInferenceWorkflow
from tests import test_faker


class TestInvoiceCreationService(TestCase):
    def setUp(self):
        self._mock_temporal_client = MagicMock(spec=Client)
        self._mock_temporal_client.start_workflow = AsyncMock()
        self._service = InvoiceCreationService(
            temporal_client=self._mock_temporal_client,
        )

    def test_create_invoice_calls_temporal_workflow_with_correct_parameters(self):
        file_path = test_faker.file_path(extension="pdf")
        invoice_id = uuid4()
        uploader_id = uuid4()
        tenant_id = uuid4()

        asyncio.run(self._service.create_invoice(invoice_id, file_path, uploader_id, tenant_id))

        self._mock_temporal_client.start_workflow.assert_called_once()

        call_args = self._mock_temporal_client.start_workflow.call_args
        workflow_func = call_args[0][0]
        params = call_args[0][1]
        workflow_id = call_args[1]["id"]
        task_queue = call_args[1]["task_queue"]

        self.assertEqual(workflow_func, InvoiceInferenceWorkflow.run)

        self.assertIsInstance(params, InvoiceInferenceWorkflowParams)
        self.assertEqual(params.invoice_id, invoice_id)
        self.assertEqual(params.file_path, file_path)
        self.assertEqual(params.uploader_id, uploader_id)
        self.assertEqual(params.tenant_id, tenant_id)

        self.assertEqual(workflow_id, "invoice-workflow")
        self.assertEqual(task_queue, INVOICE_QUEUE_NAME)
