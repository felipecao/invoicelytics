from uuid import uuid4, UUID

from sqlalchemy import exists

from invoicelytics.entities.domain_entities import Invoice, InvoiceStatus
from invoicelytics.repository.invoice_repository import InvoiceRepository
from invoicelytics.run import db
from tests import test_faker
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
        status = InvoiceStatus.CREATED
        pdf_file_path = test_faker.file_path(extension="pdf")

        self._repository.save(
            Invoice(
                id=invoice_id,
                tenant_id=tenant_id,
                status=status,
                pdf_file_path=pdf_file_path,
            )
        )

        self.assertTrue(self._exists_invoice(invoice_id, tenant_id, status))

    def test_invoice_update(self):
        invoice_id = uuid4()
        tenant_id = uuid4()
        status = InvoiceStatus.CREATED
        pdf_file_path = test_faker.file_path(extension="pdf")

        invoice = self._save_entity(
            Invoice(
                id=invoice_id,
                tenant_id=tenant_id,
                status=status,
                pdf_file_path=pdf_file_path,
            )
        )

        self._repository.update(invoice, {"status": InvoiceStatus.PROCESSED})

        self.assertTrue(self._exists_invoice(invoice_id, tenant_id, InvoiceStatus.PROCESSED))

    def test_find_by_id(self):
        invoice_id = uuid4()
        tenant_id = uuid4()
        status = InvoiceStatus.CREATED
        pdf_file_path = test_faker.file_path(extension="pdf")

        self._save_entity(
            Invoice(
                id=invoice_id,
                tenant_id=tenant_id,
                status=status,
                pdf_file_path=pdf_file_path,
            )
        )

        instance = self._repository.find_by_id(invoice_id, tenant_id)

        self.assertIsNotNone(instance)
        self.assertEqual(status, instance.status)

    def test_find_by_status(self):
        invoice_id = uuid4()
        tenant_id = uuid4()

        self._save_entity(
            Invoice(
                id=invoice_id,
                tenant_id=tenant_id,
                status=InvoiceStatus.CREATED,
                pdf_file_path=test_faker.file_path(extension="pdf"),
            )
        )

        self._save_entity(
            Invoice(
                id=uuid4(),
                tenant_id=tenant_id,
                status=InvoiceStatus.PROCESSED,
                pdf_file_path=test_faker.file_path(extension="pdf"),
            )
        )

        instances = self._repository.find_by_status(InvoiceStatus.CREATED, tenant_id)

        self.assertEqual(1, len(instances))
        self.assertEqual(invoice_id, instances[0].id)

    @staticmethod
    def _exists_invoice(invoice_id: UUID, tenant_id: UUID, status: InvoiceStatus) -> bool:
        return db.session.scalar(
            exists().where(Invoice.id == invoice_id).where(Invoice.tenant_id == tenant_id).where(Invoice.status == status).select()
        )

    @staticmethod
    def _save_entity(entity):
        db.session.add(entity)
        db.session.commit()
        return entity
