import logging
import os 

logger = logging.getLogger("llm.sdk.observability.langfuse")
from ..config.settings import _sdk_settings


_langfuse_client = None


def get_langfuse_client():
    global _langfuse_client

    if _langfuse_client is not None:
        return _langfuse_client

    try:
        from langfuse import get_client
    except Exception as exc:
        logger.warning("Langfuse not installed: %s", exc)
        return None

    public_key = _sdk_settings.langfuse.public_key
    secret_key = _sdk_settings.langfuse.secret_key
    host = _sdk_settings.langfuse.base_url

    if not public_key or not secret_key or not host:
        logger.info("Langfuse disabled (missing env vars)")
        return None

    try:
        _langfuse_client = get_client(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
        )
        logger.info("Langfuse client initialized")

    except Exception as exc:
        logger.error("Failed to init Langfuse client: %s", exc)
        _langfuse_client = None

    return _langfuse_client
