import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from ..transport.auth_http_client_factory import AuthHttpClientFactory
from .base import BaseLLMAdapter


load_dotenv()

logger = logging.getLogger("llm.sdk.adapters.langchain")

class LangChainAdapter(BaseLLMAdapter):
    """
    Adapter enterprise para instanciar un cliente ChatOpenAI de LangChain

    Encapsula:
    - ChatOpenAI client
    - base_url
    - api_key
    - model
    - timeouts
    """

    def __init__(
        self,
        base_url: str = None,
        timeout: float = 60.0,
        **kwargs
    ):
        self.base_url = base_url or os.environ.get("LLM_BASE_URL")
        self.timeout = timeout
        self.client_kwargs = kwargs

        self._validate_config()

        self._langchain_client: ChatOpenAI = None
        self._http_client = AuthHttpClientFactory.create(
            timeout=self.timeout,
        )

    # -------------------------
    # Public API
    # -------------------------
    def client(self) -> ChatOpenAI:
        """
        Devuelve una instancia singleton de ChatOpenAI de LangChain
        completamente configurada.
        """
        if not self._langchain_client:
            logger.info("Inicializando cliente LangChain ChatOpenAI")
            self._langchain_client = ChatOpenAI(
                base_url=self.base_url,
                api_key="unused",
                http_client=self._http_client,
                default_headers=AuthHttpClientFactory._default_headers(),
                **self.client_kwargs
            )

        return self._langchain_client

    # -------------------------
    # Validation
    # -------------------------
    def _validate_config(self):
        if not self.base_url:
            raise RuntimeError("LLM_BASE_URL no está configurado")

        if not self.base_url.startswith("http"):
            raise RuntimeError(f"LLM_BASE_URL inválida: {self.base_url}")
