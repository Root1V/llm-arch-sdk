
import logging
from typing import Optional

from .base_client import BaseClient

logger = logging.getLogger("llm.client.embeddings")


class Embeddings:
    def __init__(self, client: BaseClient):
        self._client = client

    def create(
        self,
        model: str,
        input: list[str],
        trace_metadata: Optional[dict] = None,
        trace_tags: Optional[list[str]] = None,
    ):
        logger.debug("llm.client.embeddings.create model=%s input=%s", model, input)
        payload = {"model": model, "input": input}

        try:
            return self._client._request(
                "POST",
                "/v1/embeddings",
                json=payload,
            )
        except Exception as exc:
            raise
        finally:
            pass