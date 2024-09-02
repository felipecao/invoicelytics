from uuid import uuid4

from invoicelytics.entities.domain_entities import User
from invoicelytics.repository.user_repository import UserRepository
from invoicelytics.run import db
from tests import test_faker
from tests.repository.base_repository_test import BaseRepositoryTest


class TestUserRepository(BaseRepositoryTest):

    def setUp(self):
        super().setUp()
        self._repository = UserRepository()

    def tearDown(self):
        super().tearDown()

    def test_find_by_id(self):
        user_id = uuid4()
        tenant_id = uuid4()
        username = test_faker.user_name()
        email = test_faker.company_email()
        password_hash = test_faker.sha256()

        self._save_entity(
            User(
                id=user_id,
                tenant_id=tenant_id,
                username=username,
                email=email,
                password_hash=password_hash,
            )
        )

        result = self._repository.find_by_id(user_id)

        self.assertIsNotNone(result)
        self.assertEqual(username, result.username)

    def test_find_by_email(self):
        user_id = uuid4()
        tenant_id = uuid4()
        username = test_faker.user_name()
        email = test_faker.company_email()
        password_hash = test_faker.sha256()

        self._save_entity(
            User(
                id=user_id,
                tenant_id=tenant_id,
                username=username,
                email=email,
                password_hash=password_hash,
            )
        )

        result = self._repository.find_by_email(email)

        self.assertIsNotNone(result)
        self.assertEqual(username, result.username)

    @staticmethod
    def _save_entity(entity):
        db.session.add(entity)
        db.session.commit()
        return entity
