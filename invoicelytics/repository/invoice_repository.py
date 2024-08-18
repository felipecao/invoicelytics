from invoicelytics.entities.domain_entities import Invoice
from invoicelytics.run import db


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
