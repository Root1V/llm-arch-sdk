
import logging
from typing import Optional
from ..observability.langfuse_client import start_trace, record_generation, record_event, set_active_trace, clear_active_trace

from .base_client import BaseClient
from ..models.completion import CompletionResult

logger = logging.getLogger("llm.client.completions")


class Completions:
    def __init__(self, client: BaseClient):
        self._client = client

    def create(
        self,
        prompt: str,
        temperature: float = 0.7,
        n_predict: int = 100,
        trace_metadata: Optional[dict] = None,
        trace_tags: Optional[list[str]] = None,
        **kwargs,
    ):
        payload = {
            "prompt": prompt,
            "temperature": temperature,
            "n_predict": n_predict,
            **kwargs,
        }

        logger.debug("llm.client.completions.create %s", payload)
        metadata = {"endpoint": "/llm/completions"}
        if trace_metadata:
            metadata = {**metadata, **trace_metadata}

        trace = start_trace(
            name="llm.client.completions.create",
            input=payload,
            metadata=metadata,
            tags=trace_tags,
        )
        set_active_trace(trace)

        try:
            raw = self._client._request(
                "POST",
                "/llm/completions",
                json=payload,
            )

            logger.debug("llm.client.completions.create response %s", raw)

            record_generation(
                trace=trace,
                name="llm.client.completions.completion",
                input=prompt,
                output=raw,
                model=raw.get("model"),
                usage=raw.get("usage"),
            )

            return CompletionResult.from_dict(raw)
        except Exception as exc:
            record_event(trace, name="llm.client.completions.error", input={"error": str(exc)})
            raise
        finally:
            clear_active_trace()
