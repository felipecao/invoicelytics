import logging
import os
from typing import Optional

from openai import OpenAI

from invoicelytics.data_structures.uploaded_file import UploadedFile


class FileClient:
    def __init__(self, client: Optional[OpenAI] = None):
        self._client = client or (OpenAI() if os.environ.get("OPENAI_API_KEY") else None)
        self.logger = logging.getLogger(self.__class__.__name__)

    def upload_file(self, file: UploadedFile) -> str:
        filename = file.filename
        content = file.read()
        file_type = file.content_type

        data = (filename, content, file_type)

        payload = self._client.files.create(file=data, purpose="assistants")

        return payload.id
