import httpx
import logging
from ..auth.token_manager import TokenManager
from .http_client_factory import HttpClientFactory

logger = logging.getLogger("llm.sdk.transport.auth_http_client_factory")

class AuthHttpClientFactory:

    @staticmethod
    def create(
        auth: TokenManager,
        timeout: float = 60.0,
        extra_headers: dict = None,
    ) -> httpx.Client:
        
        headers = HttpClientFactory._default_headers(extra_headers)

        logger.debug("Creando httpx.Client con Autenticacion común para LLM")

        return httpx.Client(
            auth=auth,
            timeout=timeout,
            headers=headers,
        )
