import logging
import os
from typing import Optional

from openai import OpenAI
from openai.types.beta.threads import Run


class RunClient:
    def __init__(self, client: Optional[OpenAI] = None):
        self._client = client or (OpenAI() if os.environ.get("OPENAI_API_KEY") else None)
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_and_poll(self, thread_id: str, assistant_id: str) -> Run:
        return self._client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_id,
            tool_choice="auto",
        )

    def cancel_run(self, thread_id: str, run_id: str) -> Run:
        return self._client.beta.threads.runs.cancel(
            thread_id=thread_id,
            run_id=run_id,
        )
