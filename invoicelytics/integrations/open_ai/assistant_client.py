import logging
import os
from typing import Optional

from openai import OpenAI
from openai.types.beta import Assistant


class AssistantClient:
    def __init__(self, client: Optional[OpenAI] = None):
        self._client = client or (OpenAI() if os.environ.get("OPENAI_API_KEY") else None)
        self.logger = logging.getLogger(self.__class__.__name__)

    def create(
        self,
        name: str,
        model: str = "gpt-4o",
        description: str = None,
        instructions: str = None,
        tools=None,
        tool_resources=None,
        temperature: float = 0.01,
        top_p: float = 1.0,
    ) -> Assistant:
        if tools is None:
            tools = []

        return self._client.beta.assistants.create(
            name=name,
            model=model,
            description=description,
            instructions=instructions,
            tools=tools,
            tool_resources=tool_resources,
            temperature=temperature,
            top_p=top_p,
        )

    def find_by_name(self, name: str) -> Assistant:
        all_assistants = self._client.beta.assistants.list(limit=100)
        return next(filter(lambda a: a.name == name, all_assistants), None)
