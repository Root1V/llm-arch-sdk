import os
import httpx
import threading
import logging
from typing import Optional
from dotenv import load_dotenv

from ..transport.circuit_breaker import CircuitBreaker
from ..transport.http_client_factory import HttpClientFactory

load_dotenv()

logger = logging.getLogger("llm.sdk.auth.token_manager")

class AuthError(Exception):
    """Errores relacionados con autenticación contra el gateway LLM."""


class TokenManager(httpx.Auth):
    def __init__(self, timeout: float = 10.0    ):
        self.base_url = os.environ.get("LLM_BASE_URL")
        self.username = os.environ.get("LLM_USERNAME")
        self.password = os.environ.get("LLM_PASSWORD")
        self.timeout = timeout

        self._validate()

        self.token: Optional[str] = None
        self._lock = threading.Lock()

        self._login_client = HttpClientFactory.create(timeout=self.timeout)
        
        self._circuit = CircuitBreaker(
            failure_threshold=3,
            reset_timeout=30,
        )

    def auth_flow(self, request):
        # 1 Asegurar token (thread-safe)
        if not self.token:
            with self._lock:
                if not self.token:
                    logger.info("Token no presente, login inicial")
                    self.token = self._login()

        # 2 Adjuntar token
        request.headers["Authorization"] = f"Bearer {self.token}"
        logger.debug("Enviando request con token %s", request.headers["Authorization"])

        # 3️ Enviar request
        response = yield request

        # 4️ Retry UNA vez si token expiró
        if response.status_code == 401 and not request.headers.get("X-Retry"):
            logger.warning("401 recibido, refrescando token")

            with self._lock:
                self.token = self._login()

            request.headers["Authorization"] = f"Bearer {self.token}"
            request.headers["X-Retry"] = "1"
            logger.debug("Reintentando request con nuevo token", request.headers["Authorization"])

            yield request

    def _login(self) -> str:
        # Circuit breaker: ¿se permite intentar login?
        if not self._circuit.allow_request():
            raise AuthError("Circuit breaker abierto: login bloqueado")

        try:
            resp = self._login_client.post(
                f"{self.base_url}/llm/login",
                auth=(self.username, self.password),
            )
            resp.raise_for_status()

            data = resp.json()
            token = data.get("token")

            if not token:
                raise AuthError("Login exitoso pero sin token")

            self._circuit.record_success()
            return token

        except httpx.TimeoutException as e:
            self._circuit.record_failure()
            logger.error("Timeout durante login")
            raise AuthError("Timeout durante login") from e

        except httpx.RequestError as e:
            self._circuit.record_failure()
            logger.error("Error de conexión durante login")
            raise AuthError(f"Error de conexión durante login: {e}") from e

        except httpx.HTTPStatusError as e:
            self._circuit.record_failure()
            logger.error(
                "Error HTTP durante login",
                extra={"status_code": e.response.status_code},
            )
            raise AuthError(
                f"Error HTTP durante login: {e.response.status_code}"
            ) from e

        except Exception as e:
            self._circuit.record_failure()
            logger.exception("Error inesperado durante login")
            raise AuthError("Error inesperado durante login") from e
    
    def _validate(self):
        if not self.base_url:
            raise RuntimeError("LLM_BASE_URL no configurada")
        if not self.username:
            raise RuntimeError("LLM_USERNAME no configurado")
        if not self.password:
            raise RuntimeError("LLM_PASSWORD no configurado")
