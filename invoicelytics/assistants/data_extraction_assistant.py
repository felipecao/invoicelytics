import json
import logging
from json import JSONDecodeError
from typing import Optional

from invoicelytics.assistants.assistant_builder import AssistantBuilder
from invoicelytics.data_structures.invoice_data_point import InvoiceDataPoint
from invoicelytics.entities.domain_entities import Invoice
from invoicelytics.integrations.open_ai.message_client import MessageClient
from invoicelytics.integrations.open_ai.run_client import RunClient
from invoicelytics.integrations.open_ai.thread_client import ThreadClient
from invoicelytics.repository.invoice_data_point_repository import InvoiceDataPointRepository
from invoicelytics.repository.invoice_repository import InvoiceRepository


class DataExtractionAssistant:
    def __init__(
        self,
        assistant_builder: Optional[AssistantBuilder] = None,
        thread_client: Optional[ThreadClient] = None,
        message_client: Optional[MessageClient] = None,
        run_client: Optional[RunClient] = None,
        invoice_repository: Optional[InvoiceRepository] = None,
        invoice_data_point_repository: Optional[InvoiceDataPointRepository] = None,
    ):
        self._assistant_builder = assistant_builder or AssistantBuilder()
        self._thread_client = thread_client or ThreadClient()
        self._message_client = message_client or MessageClient()
        self._run_client = run_client or RunClient()
        self._invoice_repository = invoice_repository or InvoiceRepository()
        self._invoice_data_point_repository = invoice_data_point_repository or InvoiceDataPointRepository()
        self._logger = logging.getLogger(__name__)

        self._NAME = "ethan_data_extraction_assistant_b4ce491f-ec4a-4324-aa11-f81288af2bad"

    def extract_attributes(self, invoice: Invoice) -> dict:
        self._logger.info(f"Extracting data from invoice {invoice.id}")

        data_points = self._invoice_data_point_repository.get_all()
        formatted_data_points = self._format_attribute_definitions_for_prompt(data_points)

        prompt = f"""
                # instructions
                You need to extract data points from an invoice in JSON format.
                The invoice has been uploaded and its file ID is: {invoice.open_ai_file_id}

                It is very important that you do not generate any imaginary values.
                Only extract information that is clearly visible and verifiable from the invoice.
                If any information is not present or cannot be confidently extracted, please return "N/A".

                Please do not generate random values. Be concise. Don't provide any explanations about your reasoning.

                Please extract the following data points from the invoice:

                # data points
                {formatted_data_points}

                """

        thread_id = self._create_thread()
        attachments = [{"file_id": invoice.open_ai_file_id, "tools": [{"type": "file_search"}]}]
        answer = self._ask_gpt(prompt=prompt, invoice=invoice, thread_id=thread_id, attachments=attachments)

        return answer

    @staticmethod
    def _format_attribute_definitions_for_prompt(data_points: list[InvoiceDataPoint]) -> str:
        formatted_string = ""
        for dp in data_points:
            description = dp.description
            field_type = dp.data_type
            additional_info = f"If there is no clear '{dp.name}' please return 'N/A'."
            formatted_string += f"- `{dp.name}` [type: {field_type}]: {description}. {additional_info}\n"
        return formatted_string.strip()

    def _create_thread(self) -> str:
        return self._thread_client.create_thread()

    def _ask_gpt(self, prompt: str, invoice: Invoice, thread_id: str = None, attachments: list[dict] = None) -> dict:
        self._message_client.create(thread_id=thread_id, prompt=prompt, attachments=attachments)

        run = self._run_client.create_and_poll(
            thread_id=thread_id,
            assistant_id=self._get_assistant_id(),
        )

        if run.status != "completed":
            self._logger.error(
                f"Assistant failed to complete run while extracting invoice data, invoice_id: {invoice.id}, "
                f"tenant_id: {invoice.tenant_id}, assistant: {self._NAME}, thread_id: {thread_id}, run_status: {run.status}, "
                f"prompt: {prompt}"
            )
            if run.status != "failed":
                self._run_client.cancel_run(thread_id=thread_id, run_id=run.id)

            return dict()

        messages = self._message_client.list(thread_id=thread_id)
        json_text = self._sanitize_text(messages.data[0].content[0].text.value)

        try:
            return json.loads(json_text)
        except JSONDecodeError:
            return {}

    def _get_assistant_id(self):
        return self._assistant_builder.create_assistant_if_does_not_exist(
            name=self._NAME,
            description="Ethan is an accounting assistant working on the extraction of core information from invoices",
            tools=[{"type": "file_search"}],
            instructions="""
                        You are Ethan, an accounting assistant working on automatically extracting core information from invoices.

                        To help with this extraction, here are some core information that are typically contained in an invoice:
                           - An invoice number
                           - Date of issue
                           - Billing and shipping addresses
                           - An itemized list of products or services with prices
                           - Total amount due
                           - Payment terms
                           - Invoices often contain keywords and phrases such as "Invoice", "Bill To", "Amount Due", and "Payment Terms".

                        They may also include company logos and tables with itemized lists.
                    """,
        )

    @staticmethod
    def _sanitize_text(json_text: str) -> str:
        return json_text.replace("```json", "").replace("```", "")
