
import logging
from typing import Optional
from ..observability.langfuse_client import start_trace, record_generation, record_event

from .base_client import BaseClient
from ..models.chat_completion import ChatCompletionResult


logger = logging.getLogger("llm.client.chatcompletions")


class ChatCompletions:
    def __init__(self, client: BaseClient):
        self._client = client

    def create(
        self,
        model: str,
        messages: list,
        trace_metadata: Optional[dict] = None,
        trace_tags: Optional[list[str]] = None,
        **kwargs,
    ):
        payload = {
            "model": model,
            "messages": messages,
            **kwargs,
        }

        logger.debug("llm.client.chatcompletions.create %s", payload)
        metadata = {"model": model, "endpoint": "/llm/chat/completions"}
        if trace_metadata:
            metadata = {**metadata, **trace_metadata}

        trace = start_trace(
            name="llm.client.chatcompletions.create",
            input=payload,
            metadata=metadata,
            tags=trace_tags,
        )
        
        logger.debug("trace created: %s", trace)

        try:
            raw = self._client._request(
                "POST",
                "/llm/chat/completions",
                json=payload,
            )

            logger.debug("llm.client.chatcompletions.create response %s", raw)

            record_generation(
                trace=trace,
                name="llm.client.chatcompletions.completion",
                input=messages,
                output=raw,
                model=model,
                usage=raw.get("usage"),
            )
            
            logger.debug("returning ChatCompletionResult %s", record_generation)

            return ChatCompletionResult.from_dict(raw)
        except Exception as exc:
            logger.error("Error in chat completions: %s", exc)
            record_event(trace, name="llm.client.chatcompletions.error", input={"error": str(exc)})
            raise
