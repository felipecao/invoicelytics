from dataclasses import dataclass
from uuid import UUID


@dataclass
class InvoiceInferenceWorkflowParams:
    invoice_id: UUID
    file_path: str
    tenant_id: UUID
    uploader_id: UUID


@dataclass
class SaveInvoiceParams:
    invoice_id: UUID
    tenant_id: UUID
    file_path: str
    open_ai_file_id: str
    uploader_id: UUID
