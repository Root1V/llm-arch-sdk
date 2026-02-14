import httpx
import threading
import logging
from http import HTTPStatus
from typing import Optional

from ..transport.circuit_breaker import CircuitBreaker
from ..transport.http_client_factory import HttpClientFactory
from langfuse import observe, get_client
from ..config.settings import _sdk_settings


langfuse = get_client()

logger = logging.getLogger("llm.sdk.auth.token_manager")

# Constantes para retry
RETRY_HEADER = "X-Retry"
RETRY_VALUE = "1"

class AuthError(Exception):
    """Errores relacionados con autenticación contra el gateway LLM."""


class TokenManager(httpx.Auth):
    def __init__(self, timeout: float):
        self.base_url = _sdk_settings.llm.base_url
        self.username = _sdk_settings.llm.username
        self.password = _sdk_settings.llm.password
        self.timeout = timeout

        self._validate()

        self.token: Optional[str] = None
        self._lock = threading.Lock()

        self._login_client = HttpClientFactory.create(timeout=self.timeout)
        
        self._circuit = CircuitBreaker(
            failure_threshold= _sdk_settings.circuit_breaker.failure_threshold,
            reset_timeout=_sdk_settings.circuit_breaker.reset_timeout,
        )

    @observe(
        name="llm.auth.flow",
        capture_input=False,
        capture_output=False,
    )
    def auth_flow(self, request):
        # 1 Asegurar token (thread-safe)
        if not self.token:
            with self._lock:
                if not self.token:
                    logger.info("Token no presente, login inicial")  
                    langfuse.update_current_span(
                        metadata={"auth.reason": "missing_token"}
                    )                  
                    self.token = self._login()
        else:
            langfuse.update_current_span(
                metadata={"auth.reason": "cached_token"}
            )

        # 2 Adjuntar token
        request.headers["Authorization"] = f"Bearer {self.token}"
        logger.debug("Enviando request con token %s", request.headers["Authorization"])
        langfuse.update_current_span(
            metadata={"auth.token_attached": True}
        )

        # 3️ Enviar request
        response = yield request

        # 4️ Retry UNA vez si token expiró
        if response.status_code == HTTPStatus.UNAUTHORIZED and not request.headers.get(RETRY_HEADER):
            logger.warning("401 recibido, refrescando token")

            langfuse.update_current_span(
                metadata={"auth.reason": "token_expired"}
            )

            with self._lock:
                self.token = self._login()

            request.headers["Authorization"] = f"Bearer {self.token}"
            request.headers[RETRY_HEADER] = RETRY_VALUE
            logger.debug("Reintentando request con nuevo token", request.headers["Authorization"])

            yield request

    @observe(
        name="llm.auth.login",
        capture_input=False,
        capture_output=False,
    )
    def _login(self) -> str:
        # Circuit breaker: ¿se permite intentar login?
        if not self._circuit.allow_request():
            langfuse.update_current_span(
                metadata={"circuit": self._circuit._state.value, "blocked": True}
            )
            raise AuthError("Circuit breaker abierto: login bloqueado")

        try:
            langfuse.update_current_span(
                metadata={"login.endpoint": "/llm/login"}
            )
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
            langfuse.update_current_span(
                metadata={"circuit": self._circuit._state.value, "error": type(e).__name__}
            )
            raise AuthError("Timeout durante login") from e

        except httpx.RequestError as e:
            self._circuit.record_failure()
            logger.error("Error de conexión durante login")
            langfuse.update_current_span(
                metadata={"circuit": self._circuit._state.value, "error": type(e).__name__}
            )
            raise AuthError(f"Error de conexión durante login: {e}") from e

        except httpx.HTTPStatusError as e:
            self._circuit.record_failure()
            logger.error(
                "Error HTTP durante login",
                extra={"status_code": e.response.status_code},
            )
            langfuse.update_current_span(
                metadata={"circuit": self._circuit._state.value, "error": type(e).__name__}
            )
            raise AuthError(
                f"Error HTTP durante login: {e.response.status_code}"
            ) from e

        except Exception as e:
            self._circuit.record_failure()
            logger.exception("Error inesperado durante login")
            langfuse.update_current_span(
                metadata={"circuit": self._circuit._state.value, "error": type(e).__name__}
            )
            raise AuthError("Error inesperado durante login") from e
    
    def _validate(self):
        if not self.base_url:
            raise RuntimeError("LLM_BASE_URL no configurada")
        if not self.username:
            raise RuntimeError("LLM_USERNAME no configurado")
        if not self.password:
            raise RuntimeError("LLM_PASSWORD no configurado")
