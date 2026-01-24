
import logging

from .base_client import BaseClient
from ..models.chat_completion import ChatCompletionResult


logger = logging.getLogger("llm.sdk.client.chat_completions")


class ChatCompletions:
    def __init__(self, client: BaseClient):
        self._client = client

    def create(self, model: str, messages: list, **kwargs):
        payload = {
            "model": model,
            "messages": messages,
            **kwargs,
        }

        logger.debug("llm.chat.create %s", payload)

        raw = self._client._request(
            "POST",
            "/llm/chat/completions",
            json=payload,
        )

        logger.debug("llm.chat.create response %s", raw)

        return ChatCompletionResult.from_dict(raw)
