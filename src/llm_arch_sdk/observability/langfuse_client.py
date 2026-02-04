"""Langfuse client wrapper for optional tracing."""

import logging
import os
from contextvars import ContextVar
from importlib import metadata
from typing import Any, Dict, Optional

logger = logging.getLogger("llm.sdk.observability.langfuse")

_LANGFUSE_IMPORT_ERROR = None
_LANGFUSE_CLIENT = None
_LANGFUSE_INIT_SENT = False
_ACTIVE_TRACE: ContextVar[Optional[Any]] = ContextVar("llm_sdk_active_trace", default=None)
_ACTIVE_TRACE_GLOBAL: Optional[Any] = None

try:
    from langfuse import Langfuse
except Exception as e:  
    _LANGFUSE_IMPORT_ERROR = e
    Langfuse = None

def _record_sdk_init(client: "Langfuse", host: str) -> None: # type: ignore
    """Emit a one-time trace to confirm Langfuse connectivity."""
    global _LANGFUSE_INIT_SENT

    if _LANGFUSE_INIT_SENT:
        return

    try:
        version = metadata.version("llm-arch-sdk")
    except Exception:
        version = "unknown"

    try:
        logger.info("📤 Sending SDK initialization span to Langfuse...")

        span = client.start_span(
            name="llm.sdk.init.observability",
            input={"status": "startup", "version": version},
            metadata={"sdk_version": version, "langfuse_host": host},
        )
        
        if span:
            logger.info("✅ SDK initialization span created: %s", span.id if hasattr(span, 'id') else span)
            span.end()
            logger.info("✅ SDK initialization span ended")
        else:
            logger.warning("⚠️  SDK initialization span returned None")
        
        _LANGFUSE_INIT_SENT = True
        
        # Force flush to ensure data is sent
        client.flush()
        logger.info("✅ Langfuse data flushed to server")
        
    except Exception as exc:
        logger.error("❌ Langfuse init failed: %s", exc)
        import traceback
        logger.debug("Traceback: %s", traceback.format_exc())

def get_langfuse() -> Optional["Langfuse"]: # type: ignore
    """Return a Langfuse client if configured, otherwise None."""
    global _LANGFUSE_CLIENT

    if Langfuse is None:
        if _LANGFUSE_IMPORT_ERROR:
            logger.error("❌ Langfuse not available - import error: %s", _LANGFUSE_IMPORT_ERROR)
        else:
            logger.debug("⚠️  Langfuse not available - not installed")
        return None

    if _LANGFUSE_CLIENT is not None:
        return _LANGFUSE_CLIENT

    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_BASE_URL")

    if not public_key or not secret_key or not host:
        logger.warning("⚠️  Langfuse not configured - missing credentials")
        logger.warning("   LANGFUSE_PUBLIC_KEY: %s", "✓ configured" if public_key else "✗ missing")
        logger.warning("   LANGFUSE_SECRET_KEY: %s", "✓ configured" if secret_key else "✗ missing")
        logger.warning("   LANGFUSE_BASE_URL: %s", "✓ configured" if host else "✗ missing")
        logger.warning("   Add these to examples/.env to enable Langfuse tracing")
        return None

    try:
        logger.info("🔧 Initializing Langfuse client...")
        logger.info("   Host: %s", host)
        logger.info("   Public Key: %s***", public_key[:10] if public_key else "None")
        
        _LANGFUSE_CLIENT = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
        )
        
        logger.info("✅ Langfuse client initialized successfully")
        _record_sdk_init(_LANGFUSE_CLIENT, host)
    except Exception as exc:
        logger.error("❌ Failed to initialize Langfuse: %s", exc)
        import traceback
        logger.debug("Traceback: %s", traceback.format_exc())
        _LANGFUSE_CLIENT = None

    return _LANGFUSE_CLIENT

def start_trace(
    name: str,
    input: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    tags: Optional[list[str]] = None,
):
    """Start a Langfuse span if configured."""
    client = get_langfuse()
    if not client:
        return None

    try:
        logger.debug("📍 Starting Langfuse span: %s", name)
        meta = metadata or {}
        if tags:
            meta = {**meta, "tags": tags}
        if hasattr(client, "trace"):
            try:
                span = client.trace(
                    name=name,
                    input=input,
                    metadata=meta,
                    tags=tags,
                )
            except TypeError:
                span = client.trace(
                    name=name,
                    input=input,
                    metadata=meta,
                )
        elif hasattr(client, "start_trace"):
            try:
                span = client.start_trace(
                    name=name,
                    input=input,
                    metadata=meta,
                    tags=tags,
                )
            except TypeError:
                span = client.start_trace(
                    name=name,
                    input=input,
                    metadata=meta,
                )
        else:
            span = client.start_span(
                name=name,
                input=input,
                metadata=meta,
            )
        
        if span:
            logger.debug("   ✓ Span created: %s", span.id if hasattr(span, 'id') else "ok")
        else:
            logger.warning("   ⚠️  Span returned None")
        
        return span
    except Exception as exc:
        logger.error("❌ Failed to create span '%s': %s", name, exc)
        return None


def set_active_trace(trace) -> None:
    global _ACTIVE_TRACE_GLOBAL
    _ACTIVE_TRACE.set(trace)
    _ACTIVE_TRACE_GLOBAL = trace


def clear_active_trace() -> None:
    global _ACTIVE_TRACE_GLOBAL
    _ACTIVE_TRACE.set(None)
    _ACTIVE_TRACE_GLOBAL = None


def get_active_trace():
    trace = _ACTIVE_TRACE.get()
    if trace is None:
        return _ACTIVE_TRACE_GLOBAL
    return trace


def record_generation(
    trace,
    name: str,
    input: Any,
    output: Any,
    model: Optional[str] = None,
    usage: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
):
    """Record a generation on a Langfuse span."""
    if not trace:
        return

    try:
        logger.debug("📝 Recording generation on span: %s (model=%s)", name, model)
        # Langfuse 3.x - use start_observation with type='generation'
        obs = trace.start_observation(
            name=name,
            input=input,
            output=output,
            model=model,
            as_type="generation",
            metadata=metadata,
        )
        
        if obs:
            logger.debug("   ✓ Generation recorded: %s", obs.id if hasattr(obs, 'id') else "ok")
            if hasattr(obs, "end"):
                obs.end()
            if hasattr(trace, "end"):
                trace.end()
                logger.debug("   ✓ Span ended after generation")
        else:
            logger.warning("   ⚠️  Generation observation returned None")
            
    except Exception as exc:
        logger.error("❌ Failed to record generation '%s': %s", name, exc)
        import traceback
        logger.debug("Traceback: %s", traceback.format_exc())


def record_event(trace, name: str, input: Optional[Dict[str, Any]] = None):
    """Record a Langfuse event on a span."""
    if not trace:
        return

    try:
        logger.debug("🔔 Recording event on span: %s", name)
        # In Langfuse 3.x, events are typically logged via start_span or just as status
        # For errors, we can use the span's methods
        if hasattr(trace, 'update'):
            trace.update(
                output={"event": name, "details": input},
                level="ERROR",
                status_message=str(input) if input else None,
            )
            if hasattr(trace, "end"):
                trace.end()
            logger.debug("   ✓ Event recorded and span ended: %s", name)
        else:
            logger.warning("   ⚠️  Span does not have update method")
    except Exception as exc:
        logger.error("❌ Failed to record event '%s': %s", name, exc)


def record_step(trace, name: str, input: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None):
    """Record a non-terminal step on a span without ending it."""
    if not trace:
        return

    try:
        if isinstance(trace, dict) and "trace_id" in trace:
            client = get_langfuse()
            if not client:
                return
            step = client.start_span(
                trace_context=trace,
                name=name,
                input=input,
                metadata=metadata,
            )
            if step and hasattr(step, "end"):
                step.end()
            return

        if hasattr(trace, "start_span"):
            step = trace.start_span(
                name=name,
                input=input,
                metadata=metadata,
            )
            if step and hasattr(step, "end"):
                step.end()
            return

        if hasattr(trace, "update"):
            trace.update(
                output={"event": name, "details": input},
                metadata=metadata,
            )
    except Exception as exc:
        logger.error("❌ Failed to record step '%s': %s", name, exc)
