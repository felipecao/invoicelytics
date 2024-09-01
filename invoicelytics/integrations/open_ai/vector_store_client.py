import logging
import os
from typing import Optional

from openai import OpenAI
from openai.types.beta import VectorStore


class VectorStoreClient:
    def __init__(self, client: Optional[OpenAI] = None):
        self._client = client or (OpenAI() if os.environ.get("OPENAI_API_KEY") else None)
        self.logger = logging.getLogger(self.__class__.__name__)

    def upload_files_by_ids(self, vector_store_id: str, file_ids: list[str]) -> bool:
        if len(file_ids) == 0:
            return False

        try:
            self._client.beta.vector_stores.file_batches.upload_and_poll(vector_store_id=vector_store_id, file_ids=file_ids, files=[])
            return True
        except Exception as e:
            self.logger.error(f"Error when uploading files to the vector store, vector_store_id={vector_store_id}, error={e}")
            return False

    def create(self, name: Optional[str] = None) -> str:
        if name is None:
            return self._client.beta.vector_stores.create().id
        return self._client.beta.vector_stores.create(name=name).id

    def find_by_id(self, vector_store_id: str) -> VectorStore:
        all_vector_stores = self._client.beta.vector_stores.list(limit=100)
        return next(filter(lambda a: a.id == vector_store_id, all_vector_stores), None)
