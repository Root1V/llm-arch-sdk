import httpx
import logging
from typing import Optional
from ..auth.token_manager import TokenManager
from .http_client_factory import HttpClientFactory
from langfuse import observe

logger = logging.getLogger("llm.sdk.transport.auth_http_client_factory")

class AuthHttpClientFactory(HttpClientFactory):

    @classmethod
    @observe(
        name="llm.transport.http_client_factory",
        capture_input=False,
        capture_output=False,
    )
    def create(
        cls,
        auth: Optional[TokenManager] = None,
        timeout: float = 60.0,
        extra_headers: dict = None,
    ) -> httpx.Client:
            
        auth = auth or TokenManager()

        headers = cls._default_headers(extra_headers)

        logger.debug("Creando httpx.Client con Autenticacion común para LLM")

        return httpx.Client(
            auth=auth,
            timeout=timeout,
            headers=headers,
        )
