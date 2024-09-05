from uuid import UUID

from sqlalchemy import select, update

from invoicelytics.entities.domain_entities import Invoice, InvoiceStatus
from invoicelytics.run import db
from invoicelytics.support.helpers import get_value


class InvoiceRepository:

    @staticmethod
    def save(instance: Invoice):
        try:
            with db.session.begin_nested():
                db.session.add(instance)
            db.session.commit()
            return instance.id
        except Exception as e:
            db.session.rollback()
            raise e
        finally:
            db.session.close()

    @staticmethod
    def update(instance: Invoice, attributes_to_update: dict):
        db.session.execute(
            update(Invoice)
            .where(Invoice.id == instance.id)
            .where(Invoice.tenant_id == instance.tenant_id)
            .values(
                payee_name=get_value(attributes_to_update, instance, "payee_name"),
                payee_address=get_value(attributes_to_update, instance, "payee_address"),
                invoice_number=get_value(attributes_to_update, instance, "invoice_number"),
                issue_date=get_value(attributes_to_update, instance, "issue_date"),
                total_amount=get_value(attributes_to_update, instance, "total_amount"),
                tax_amount=get_value(attributes_to_update, instance, "tax_amount"),
                due_date=get_value(attributes_to_update, instance, "due_date"),
                status=get_value(attributes_to_update, instance, "status"),
                open_ai_json_file_id=get_value(attributes_to_update, instance, "open_ai_json_file_id"),
                approved_by=get_value(attributes_to_update, instance, "approved_by"),
            )
        )
        db.session.commit()

    @staticmethod
    def find_by_id(invoice_id: UUID, tenant_id: UUID) -> Invoice:
        return db.session.scalar(select(Invoice).where(Invoice.id == invoice_id).where(Invoice.tenant_id == tenant_id))

    @staticmethod
    def find_by_status(status: InvoiceStatus, tenant_id: UUID) -> list[Invoice]:
        return db.session.scalars(select(Invoice).where(Invoice.status == status).where(Invoice.tenant_id == tenant_id)).all()
