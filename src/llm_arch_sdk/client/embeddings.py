
import logging

from .base_client import BaseClient

logger = logging.getLogger("llm.sdk.client.embeddings")


class Embeddings:
    def __init__(self, client: BaseClient):
        self._client = client

    def create(self, model: str, input: list[str]):
        logger.debug("llama.embeddings.create model=%s input=%s", model, input)
        
        return self._client._request(
            "POST",
            "/v1/embeddings",
            json={"model": model, "input": input},
        )
