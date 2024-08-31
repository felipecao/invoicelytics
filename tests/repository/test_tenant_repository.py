from uuid import uuid4, UUID

from sqlalchemy import exists

from invoicelytics.entities.domain_entities import Tenant
from invoicelytics.repository.tenant_repository import TenantRepository
from invoicelytics.run import db
from tests import test_faker
from tests.repository.base_repository_test import BaseRepositoryTest


class TestTenantRepository(BaseRepositoryTest):

    def setUp(self):
        super().setUp()
        self._repository = TenantRepository()

    def tearDown(self):
        super().tearDown()

    def test_update(self):
        tenant_id = uuid4()
        name = test_faker.company()
        vector_store_id = str(uuid4())

        instance = self._save_entity(
            Tenant(
                id=tenant_id,
                tenant_name=name,
            )
        )

        self._repository.update(instance, vector_store_id)

        self.assertTrue(self._exists(tenant_id, vector_store_id))

    def test_find_by_id(self):
        tenant_id = uuid4()
        name = test_faker.company()

        self._save_entity(
            Tenant(
                id=tenant_id,
                tenant_name=name,
            )
        )

        instance = self._repository.find_by_id(tenant_id)

        self.assertIsNotNone(instance)
        self.assertEqual(name, instance.tenant_name)

    def test_find_all(self):
        tenant_id = uuid4()
        name = test_faker.company()

        self._save_entity(
            Tenant(
                id=tenant_id,
                tenant_name=name,
            )
        )

        instances = self._repository.find_all()

        self.assertEqual(1, len(instances))
        self.assertEqual(name, instances[0].tenant_name)

    @staticmethod
    def _exists(tenant_id: UUID, vector_store_id: str) -> bool:
        return db.session.scalar(exists().where(Tenant.id == tenant_id).where(Tenant.open_ai_vector_store_id == vector_store_id).select())

    @staticmethod
    def _save_entity(entity):
        db.session.add(entity)
        db.session.commit()
        return entity
