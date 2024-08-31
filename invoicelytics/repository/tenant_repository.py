from uuid import UUID

from sqlalchemy import select, update

from invoicelytics.entities.domain_entities import Tenant
from invoicelytics.run import db


class TenantRepository:

    @staticmethod
    def find_by_id(tenant_id: UUID) -> Tenant:
        return db.session.scalar(select(Tenant).where(Tenant.id == tenant_id))

    @staticmethod
    def update(instance: Tenant, open_ai_vector_store_id: str):
        db.session.execute(
            update(Tenant)
            .where(Tenant.id == instance.id)
            .values(
                open_ai_vector_store_id=open_ai_vector_store_id,
            )
        )
        db.session.commit()
