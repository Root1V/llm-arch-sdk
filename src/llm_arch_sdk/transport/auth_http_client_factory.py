import httpx
import logging
from typing import Optional
from ..auth.token_manager import TokenManager
from .http_client_factory import HttpClientFactory

logger = logging.getLogger("llm.sdk.transport.auth_http_client_factory")

class AuthHttpClientFactory(HttpClientFactory):

    @classmethod
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
