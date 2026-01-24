import os
import logging
from dotenv import load_dotenv

from .base import BaseLLMAdapter
from ..client.llm_client import LlmClient
from ..auth.token_manager import TokenManager
from ..transport.auth_http_client_factory import AuthHttpClientFactory

load_dotenv()

logger = logging.getLogger("llm.sdk.adapters.llama")


class LlamaAdapter(BaseLLMAdapter):
    """
    Adapter enterprise para instanciar un cliente LlamaServer

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
        self._llm_client: LlmClient = None
        self._http_client = AuthHttpClientFactory.create(
            auth=self._auth,
            timeout=self.timeout,
        )

    def client(self) -> LlmClient:
        """
        Devuelve un cliente minimalista para inferencia con llama-server
        completamente configurada.
        """
        if not self._llm_client:
            logger.info("Inicializando cliente LLM")
            self._llm_client = LlmClient(
                base_url=self.base_url,
                http_client=self._http_client
            )
        return self._llm_client

    def _validate_config(self):
        if not self.base_url:
            raise RuntimeError("LLM_BASE_URL no configurada")