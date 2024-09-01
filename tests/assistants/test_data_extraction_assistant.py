from unittest import TestCase
from unittest.mock import MagicMock
from uuid import uuid4

from invoicelytics.assistants.data_extraction_assistant import DataExtractionAssistant
from invoicelytics.data_structures.invoice_data_point import InvoiceDataPoint
from invoicelytics.entities.domain_entities import Invoice
from invoicelytics.integrations.open_ai.message_client import MessageClient
from invoicelytics.integrations.open_ai.run_client import RunClient
from invoicelytics.integrations.open_ai.thread_client import ThreadClient
from invoicelytics.repository.invoice_data_point_repository import InvoiceDataPointRepository
from invoicelytics.repository.invoice_repository import InvoiceRepository
from invoicelytics.repository.tenant_repository import TenantRepository
from tests import test_faker
from tests.randoms import fake_object


class TestDataExtractionAssistant(TestCase):
    def setUp(self):
        self.mock_thread_client = MagicMock(spec=ThreadClient)
        self.mock_message_client = MagicMock(spec=MessageClient)
        self.mock_run_client = MagicMock(spec=RunClient)
        self.mock_invoice_repository = MagicMock(spec=InvoiceRepository)
        self.mock_invoice_data_point_repository = MagicMock(spec=InvoiceDataPointRepository)
        self.mock_tenant_repository = MagicMock(spec=TenantRepository)
        self.assistant = DataExtractionAssistant(
            thread_client=self.mock_thread_client,
            message_client=self.mock_message_client,
            run_client=self.mock_run_client,
            invoice_repository=self.mock_invoice_repository,
            invoice_data_point_repository=self.mock_invoice_data_point_repository,
            tenant_repository=self.mock_tenant_repository,
        )

    def test_extract_attributes(self):
        thread_id = test_faker.random_letters(length=10)

        mock_run = MagicMock()
        mock_run.status = "completed"

        mock_messages = fake_object(
            {"data": [fake_object({"content": [fake_object({"text": fake_object({"value": '```json{"payee_name":"Test Company"}```'})})]})]}
        )

        invoice = MagicMock(spec=Invoice)
        invoice.id = uuid4()
        invoice.open_ai_file_id = "file_id"

        self.mock_invoice_data_point_repository.get_all.return_value = [
            InvoiceDataPoint(name="payee_name", data_type="string", description="Payee name")
        ]
        self.mock_tenant_repository.find_by_id.return_value = MagicMock(open_ai_chat_assistant_id="assistant_id")
        self.mock_thread_client.create_thread.return_value = thread_id
        self.mock_run_client.create_and_poll.return_value = mock_run
        self.mock_message_client.list.return_value = mock_messages

        result = self.assistant.extract_attributes(invoice)

        self.assertEqual(result, {"payee_name": "Test Company"})
        self.mock_run_client.cancel_run.assert_not_called()

    def test_extract_attributes_cancel_run(self):
        thread_id = test_faker.random_letters(length=10)
        run_id = test_faker.random_letters(length=10)

        mock_run = MagicMock()
        mock_run.id = run_id
        mock_run.status = "action_required"

        invoice = MagicMock(spec=Invoice)
        invoice.id = uuid4()
        invoice.open_ai_file_id = "file_id"

        self.mock_invoice_data_point_repository.get_all.return_value = [
            InvoiceDataPoint(name="payee_name", data_type="string", description="Payee name")
        ]
        self.mock_tenant_repository.find_by_id.return_value = MagicMock(open_ai_chat_assistant_id="assistant_id")
        self.mock_thread_client.create_thread.return_value = thread_id
        self.mock_run_client.create_and_poll.return_value = mock_run

        result = self.assistant.extract_attributes(invoice)

        self.assertEqual(result, {})
        self.mock_message_client.list.assert_not_called()
        self.mock_run_client.cancel_run.assert_called_once_with(thread_id=thread_id, run_id=run_id)

    def test_extract_attributes_failed_run(self):
        thread_id = test_faker.random_letters(length=10)
        run_id = test_faker.random_letters(length=10)

        mock_run = MagicMock()
        mock_run.id = run_id
        mock_run.status = "failed"

        invoice = MagicMock(spec=Invoice)
        invoice.id = uuid4()
        invoice.open_ai_file_id = "file_id"

        self.mock_invoice_data_point_repository.get_all.return_value = [
            InvoiceDataPoint(name="payee_name", data_type="string", description="Payee name")
        ]
        self.mock_tenant_repository.find_by_id.return_value = MagicMock(open_ai_chat_assistant_id="assistant_id")
        self.mock_thread_client.create_thread.return_value = thread_id
        self.mock_run_client.create_and_poll.return_value = mock_run

        result = self.assistant.extract_attributes(invoice)

        self.assertEqual(result, {})
        self.mock_message_client.list.assert_not_called()
        self.mock_run_client.cancel_run.assert_not_called()
