from typing import Dict, Optional, Any
import logging

from .bootstrap import get_langfuse_client
from .helpers import new_session_id
from ..config.settings import _sdk_settings


logger = logging.getLogger("llm.sdk.observability.context")

class ObservabilityContext:
    """
    Punto único para:
    - asegurar session_id
    - actualizar metadata/tags del span actual
    - no exponer langfuse al resto del SDK
    """

    def __init__(self):
        self._client = get_langfuse_client()

    def update(
        self,
        *,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Garantiza que exista un contexto mínimo de observabilidad
        y actualiza el span activo creado por @observe.

        Devuelve el session_id efectivo.
        """

        if not self._client:
            return session_id

        try:
            sid = session_id or new_session_id()

            payload: Dict[str, Any] = {
                "session_id": sid,
            }
            
            uid = user_id or _sdk_settings.llm.username
            payload["user_id"] = uid

            if metadata:
                payload["metadata"] = metadata

            if tags:
                payload["tags"] = tags

            # API oficial v3
            self._client.update_current_trace(**payload)

            return sid

        except Exception as exc:
            logger.debug("Langfuse update_current_trace failed: %s", exc)
            return session_id


# singleton liviano
obs = ObservabilityContext()


