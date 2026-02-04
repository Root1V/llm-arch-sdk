import os
import logging
import httpx
from openai import OpenAI
from dotenv import load_dotenv

from .base import BaseLLMAdapter
from ..transport.auth_http_client_factory import AuthHttpClientFactory


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
        **kwargs
    ):
        self.base_url = base_url or os.environ.get("LLM_BASE_URL")
        self.timeout = timeout
        self.client_kwargs = kwargs

        self._validate_config()

        self._openai_client: OpenAI = None
        self._http_client = AuthHttpClientFactory.create(
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
            
            try:
                from langfuse.openai import OpenAI as LangfuseOpenAI
                
                logger.info("Langfuse OpenAI instrumentation enabled (langfuse)")
                self._openai_client = LangfuseOpenAI(
                    base_url=self.base_url,
                    api_key="unused",
                    http_client=self._http_client,
                    default_headers=AuthHttpClientFactory._default_headers(),
                    **self.client_kwargs,
                )
            except Exception as exc:
                logger.warning("Langfuse OpenAI integration failed, using plain OpenAI client: %s", exc)
                self._openai_client = OpenAI(
                    base_url=self.base_url,
                    api_key="unused",
                    http_client=self._http_client,
                    default_headers=AuthHttpClientFactory._default_headers(),
                    **self.client_kwargs,
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
