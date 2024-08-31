from unittest import TestCase
from uuid import uuid4

from invoicelytics.integrations.open_ai.vector_store_client import VectorStoreClient
from tests import test_faker
from tests.randoms import fake_object

vector_store_id = test_faker.word()


class MockVectorStores:
    file_batches = fake_object({"upload_and_poll": lambda vector_store_id, file_ids, files: True})

    @staticmethod
    def create():
        return fake_object({"id": vector_store_id})


class TestVectorStoreClient(TestCase):

    def test_create(self):
        mock_client = fake_object({"beta": fake_object({"vector_stores": MockVectorStores()})})
        client = VectorStoreClient(client=mock_client)

        result = client.create()

        self.assertEqual(vector_store_id, result)

    def test_upload_files_by_ids(self):
        mock_client = fake_object({"beta": fake_object({"vector_stores": MockVectorStores()})})
        client = VectorStoreClient(client=mock_client)
        file_id = str(uuid4())

        result = client.upload_files_by_ids(vector_store_id=vector_store_id, file_ids=[file_id])

        self.assertTrue(result)
