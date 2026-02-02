
import logging
from typing import Optional
from ..observability.langfuse_client import start_trace, record_event

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
        metadata = {"model": model, "endpoint": "/v1/embeddings"}
        if trace_metadata:
            metadata = {**metadata, **trace_metadata}

        trace = start_trace(
            name="llm.client.embeddings.create",
            input=payload,
            metadata=metadata,
            tags=trace_tags,
        )

        try:
            return self._client._request(
                "POST",
                "/v1/embeddings",
                json=payload,
            )
        except Exception as exc:
            record_event(trace, name="llm.client.embeddings.error", input={"error": str(exc)})
            raise
