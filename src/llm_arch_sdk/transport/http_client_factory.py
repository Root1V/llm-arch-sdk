from typing import Dict, Mapping, Optional
import httpx
import logging

logger = logging.getLogger("llm.sdk.transport.http_client_factory")

class HttpClientFactory:

    @classmethod
    def _default_headers(cls, extra: Optional[Mapping[str, str]] = None) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "SDK-Architecture-PE/LLM-Client/1.0",
        }
        if extra:
            headers.update(extra)
        return headers


    @classmethod
    def create(
        cls,
        timeout: float = 60.0,
        extra_headers: dict = None,
    ) -> httpx.Client:

        headers = cls._default_headers(extra_headers)

        logger.debug("Creando httpx.Client común para LLM")

        return httpx.Client(
            timeout=timeout,
            headers=headers,
        )
