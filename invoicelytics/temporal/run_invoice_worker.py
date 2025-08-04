import asyncio
import dotenv


dotenv.load_dotenv()

from temporalio.client import Client
from temporalio.worker import Worker

from invoicelytics.temporal.activity.data_extraction import extract_invoice_data
from invoicelytics.temporal.activity.filesystem import move_invoice_to_tenant_folder
from invoicelytics.temporal.activity.db import save_invoice_to_db
from invoicelytics.temporal.activity.open_ai import upload_invoice_to_open_ai
from invoicelytics.temporal.queues import INVOICE_QUEUE_NAME
from invoicelytics.temporal.workflow.invoice import InvoiceInferenceWorkflow


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue=INVOICE_QUEUE_NAME,
        workflows=[InvoiceInferenceWorkflow],
        activities=[move_invoice_to_tenant_folder, upload_invoice_to_open_ai, save_invoice_to_db, extract_invoice_data],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
