from dataclasses import dataclass


@dataclass
class InvoiceDataPoint:
    name: str
    data_type: str
    description: str
