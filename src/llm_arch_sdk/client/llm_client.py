import httpx
import logging

from .base_client import BaseClient
from .chat_completions import ChatCompletions
from .completions import Completions
from .embeddings import Embeddings
from ..transport.circuit_breaker import CircuitBreaker, CircuitBreakerOpen

logger = logging.getLogger("llm.sdk.client")

class LlmAPIError(Exception):
    pass


class LlmClient(BaseClient):
    """
    Cliente liviano para llama-server compatible con OpenAI-style APIs
    """

    def __init__(self, base_url: str, http_client: httpx.Client):
        self.base_url = base_url.rstrip("/")
        self._http_client = http_client
        self._circuit = CircuitBreaker(
            failure_threshold=3,
            reset_timeout=30,
        )

        self.completions = Completions(self)
        self.chat = ChatCompletions(self)
        self.embeddings = Embeddings(self)

    def _request(self, method: str, endpoint: str, **kwargs):
        if not self._circuit.allow_request():
            raise CircuitBreakerOpen("Circuit abierto para llama-server")
        
        try:
            resp = self._http_client.request(
                method,
                f"{self.base_url}{endpoint}",
                **kwargs,
            )
            if resp.status_code >= 500:
                self._circuit.record_failure()
                raise LlmAPIError(f"Error {resp.status_code}")

            self._circuit.record_success()
            resp.raise_for_status()
            return resp.json()
            
        except httpx.HTTPStatusError as e:
            self._circuit.record_failure()
            raise LlmAPIError(f"HTTP {e.response.status_code}: {e.response.text}") from e
        
        except (httpx.TimeoutException, httpx.RequestError) as e:
            self._circuit.record_failure()
            raise LlmAPIError(str(e)) from e
        
    def health(self):
        return self._request("GET", "/health")
    
