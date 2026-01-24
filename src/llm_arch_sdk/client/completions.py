
import logging

from .base_client import BaseClient
from ..models.completion import CompletionResult

logger = logging.getLogger("llm.sdk.client.completions")


class Completions:
    def __init__(self, client: BaseClient):
        self._client = client

    def create(self, prompt: str, temperature: float = 0.7, n_predict: int = 100, **kwargs):
        payload = {
            "prompt": prompt,
            "temperature": temperature,
            "n_predict": n_predict,
            **kwargs,
        }

        logger.debug("llm.completions.create %s", payload)

        raw = self._client._request(
            "POST",
            "/llm/completions",
            json=payload,
        )

        logger.debug("llm.completions.create response %s", raw)

        return CompletionResult.from_dict(raw)
