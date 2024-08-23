import logging
import os
from typing import Optional

from openai import OpenAI


class ThreadClient:
    def __init__(self, client: Optional[OpenAI] = None):
        self._client = client or (OpenAI() if os.environ.get("OPENAI_API_KEY") else None)
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_thread(self):
        return self._client.beta.threads.create().id
