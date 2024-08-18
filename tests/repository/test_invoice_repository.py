from uuid import uuid4
from tests import test_faker

from sqlalchemy import exists

from invoicelytics.entities.domain_entities import Invoice, InvoiceStatus
from invoicelytics.repository.invoice_repository import InvoiceRepository
from invoicelytics.run import db
from tests.repository.base_repository_test import BaseRepositoryTest


class TestInvoiceRepository(BaseRepositoryTest):

    def setUp(self):
        super().setUp()
        self._repository = InvoiceRepository()

    def tearDown(self):
        super().tearDown()

    def test_invoice_creation(self):
        invoice_id = uuid4()
        tenant_id = uuid4()
        pdf_file_path = test_faker.file_path(extension="pdf")

        self._repository.save(
            Invoice(
                id=invoice_id,
                tenant_id=tenant_id,
                status=InvoiceStatus.CREATED,
                pdf_file_path=pdf_file_path,
            )
        )

        self.assertTrue(self._exists_invoice(invoice_id, tenant_id))

    @staticmethod
    def _exists_invoice(invoice_id, tenant_id) -> bool:
        return db.session.scalar(exists().where(Invoice.id == invoice_id).where(Invoice.tenant_id == tenant_id).select())
