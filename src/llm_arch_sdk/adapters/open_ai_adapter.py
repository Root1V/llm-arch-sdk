import os
import logging
import httpx
from openai import OpenAI
from dotenv import load_dotenv

from .base import BaseLLMAdapter
from ..auth.token_manager import TokenManager
from ..transport.auth_http_client_factory import AuthHttpClientFactory, HttpClientFactory


load_dotenv()

logger = logging.getLogger("llm.sdk.adapters.openai")

class OpenAIAdapter(BaseLLMAdapter):
    """
    Adapter enterprise para instanciar un cliente OpenAI

    Encapsula:
    - TokenManager
    - httpx.Client
    - base_url
    - timeouts
    """

    def __init__(
        self,
        base_url: str = None,
        timeout: float = 60.0,
    ):
        self.base_url = base_url or os.environ.get("LLM_BASE_URL")
        self.timeout = timeout

        self._validate_config()

        self._auth = TokenManager()
        self._openai_client: OpenAI = None
        self._http_client = AuthHttpClientFactory.create(
            auth=self._auth,
            timeout=self.timeout,
        )

    # -------------------------
    # Public API
    # -------------------------
    def client(self) -> OpenAI:
        """
        Devuelve una instancia singleton de OpenAI
        completamente configurada.
        """
        if not self._openai_client:
            logger.info("Inicializando cliente OpenAI")
            self._openai_client =  OpenAI(
                base_url=self.base_url,
                api_key="unused", 
                http_client=self._http_client,
                default_headers=HttpClientFactory._default_headers()
            )

        return self._openai_client

    # -------------------------
    # Validation
    # -------------------------
    def _validate_config(self):
        if not self.base_url:
            raise RuntimeError("LLM_BASE_URL no está configurado")

        if not self.base_url.startswith("http"):
            raise RuntimeError(f"LLM_BASE_URL inválida: {self.base_url}")
