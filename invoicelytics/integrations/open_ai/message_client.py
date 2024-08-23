import logging
import os
from typing import Literal, Optional

from openai import OpenAI
from openai.pagination import SyncCursorPage
from openai.types.beta.threads import Message


class MessageClient:
    def __init__(self, client: Optional[OpenAI] = None):
        self._client = client or (OpenAI() if os.environ.get("OPENAI_API_KEY") else None)
        self.logger = logging.getLogger(self.__class__.__name__)

    def create(
        self,
        thread_id: str,
        prompt: str,
        role: Literal["user", "assistant"] = "user",
        attachments: list = None,
    ) -> Message:
        if not attachments:
            attachments = []

        content = [
            {"type": "text", "text": prompt},
        ]

        return self._client.beta.threads.messages.create(
            thread_id=thread_id,
            content=content,
            role=role,
            attachments=attachments,
        )

    def list(self, thread_id: str) -> SyncCursorPage[Message]:
        return self._client.beta.threads.messages.list(thread_id=thread_id)
