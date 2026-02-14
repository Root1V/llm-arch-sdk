import logging

from .base import BaseLLMAdapter
from ..client.llm_client import LlmClient
from ..transport.auth_http_client_factory import AuthHttpClientFactory
from ..config.settings import _sdk_settings
from langfuse import observe, get_client

logger = logging.getLogger("llm.sdk.adapters.llama")

langfuse = get_client()


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
        base_url: str = _sdk_settings.llm.base_url,
        timeout: float = _sdk_settings.transport.timeout_seconds,
        **kwargs
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.client_kwargs = kwargs

        self._validate_config()

        self._llm_client: LlmClient = None
        self._http_client = AuthHttpClientFactory.create(
            timeout=self.timeout,
        )

    @observe(
        name="llama.adapter.client", 
        capture_input=False, 
        capture_output=False
    )
    def client(self) -> LlmClient:
        """
        Devuelve un cliente minimalista para inferencia con llama-server
        completamente configurada.
        """
        if not self._llm_client:
            logger.info("Inicializando cliente LLM")
            
            # metadata técnica guardada en el span actual
            langfuse.update_current_span(
                metadata={
                    "adapter": "llama",
                    "base_url": self.base_url,
                    "timeout": self.timeout,
                }
            )
            
            self._llm_client = LlmClient(
                base_url=self.base_url,
                http_client=self._http_client,
                **self.client_kwargs
            )
        return self._llm_client

    def _validate_config(self):
        if not self.base_url:
            raise RuntimeError("LLM_BASE_URL no configurada")