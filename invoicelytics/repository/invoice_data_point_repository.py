from invoicelytics.data_structures.invoice_data_point import InvoiceDataPoint


class InvoiceDataPointRepository:
    @staticmethod
    def get_all():
        return [
            InvoiceDataPoint(
                "payee_name",
                "string",
                "What is the name of the company that sent the invoice? This should be the entity or individual that "
                "issued or sent the invoice, which is typically found at the top. This is not the recipient or the entity "
                "being invoiced. Please focus on identifying the sender's name as 'payee_name'.",
            ),
            InvoiceDataPoint(
                "payee_address",
                "string",
                "What is the address of the company that sent the invoice? It should be a valid address. "
                "It should not contain phone numbers.",
            ),
            InvoiceDataPoint(
                "invoice_number",
                "string",
                "What's the identifier of this invoices? It's usually an alphanumeric code that uniquely "
                "identifies this invoices. It could be a code starting with 'INV-' but this is not guaranteed.",
            ),
            InvoiceDataPoint(
                "issue_date",
                "date",
                "When was this invoice issued? If a issue date is present, please format it in the YYYY-MM-DD format. "
                "This date may be labeled as 'Invoice Date,' 'Issue Date,' 'Date,' or similar. "
                "If multiple dates are present, choose the one most likely associated with the issuance of the invoice. "
                "If the date appears ambiguous, default to the earliest date mentioned on the invoice.",
            ),
            InvoiceDataPoint(
                "total_amount",
                "float",
                "What is the total amount due (including tax) on the invoice? Please do not include the currency.",
            ),
            InvoiceDataPoint(
                "tax_amount",
                "float",
                "What is the total amount of tax due on the invoice? Please do not include the currency.",
            ),
            InvoiceDataPoint(
                "due_date",
                "date",
                "When is the payment due on the invoice? This could be written in a couple of ways. The first would be "
                "to just explicitly write the due date itself. Alternatively they can be written relative to the "
                "invoice date / issue date. If so you will see something like '30 days from date of issue' or "
                "just 'net30' written on the invoice. This means that you'd need to add 30 days to the invoice "
                "date / issue date (or whatever number is written there). If a due date is present, "
                "please format it in the YYYY-MM-DD format.",
            ),
        ]
