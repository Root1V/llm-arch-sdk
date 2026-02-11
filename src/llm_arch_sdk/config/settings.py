from dataclasses import dataclass, field
from typing import List, Optional
import os


# -------------------------
# Observability
# -------------------------

@dataclass
class ObservabilitySettings:
    enabled: bool = True

    provider: str = "langfuse"

    capture_input: bool = False
    capture_output: bool = False

    # hooks de masking registrados por nombre
    masking_strategies: List[str] = field(default_factory=lambda: [
        "mask_secrets",
        "mask_pii",
        "mask_credit_card",
        "mask_email_and_phone",
    ])

# -------------------------
# LLM backend
# -------------------------

@dataclass
class LlmBackendEnv:
    base_url: str
    username: Optional[str]
    password: Optional[str]
    

# -------------------------
# Langfuse
# -------------------------

@dataclass
class LangfuseEnv:
    public_key: Optional[str]
    secret_key: Optional[str]
    base_url: Optional[str]
    environment: Optional[str]
    release: Optional[str]


# -------------------------
# OpenTelemetry
# -------------------------

@dataclass
class OtelEnv:
    service_name: Optional[str]



# -------------------------
# Transport / HTTP
# -------------------------

@dataclass
class TransportSettings:
    timeout_seconds: float = 60.0


@dataclass
class AuthSettings:
    token_timeout: float = 10.0

# -------------------------
# Circuit breaker
# -------------------------

@dataclass
class CircuitBreakerSettings:
    failure_threshold: int = 3
    reset_timeout: int = 30
    half_open_success: int = 1


# -------------------------
# SDK identity
# -------------------------

@dataclass
class SdkIdentitySettings:
    name: str = "llm-arch-sdk"
    version: str = os.getenv("LLM_ARCH_SDK_VERSION", "dev")
    user_agent: str = "SDK-Architecture-PE/LLM-Client/1.0"


# -------------------------
# Root SDK settings
# -------------------------

@dataclass
class SdkSettings:
    observability: ObservabilitySettings = field(default_factory=ObservabilitySettings)
    transport: TransportSettings = field(default_factory=TransportSettings)
    circuit_breaker: CircuitBreakerSettings = field(default_factory=CircuitBreakerSettings)
    auth: AuthSettings = field(default_factory=AuthSettings)
    identity: SdkIdentitySettings = field(default_factory=SdkIdentitySettings)
    llm: LlmBackendEnv = field(default_factory=lambda: LlmBackendEnv(
        base_url=os.getenv("LLM_BASE_URL"),
        username=os.getenv("LLM_USERNAME"),
        password=os.getenv("LLM_PASSWORD"),
    ))
    langfuse: LangfuseEnv = field(default_factory=lambda: LangfuseEnv(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            base_url=os.getenv("LANGFUSE_BASE_URL"),
            environment=os.getenv("LANGFUSE_TRACING_ENVIRONMENT"),
            release=os.getenv("LANGFUSE_RELEASE"),
        ))
    otel: OtelEnv = field(default_factory=lambda: OtelEnv(
            service_name=os.getenv("OTEL_SERVICE_NAME"),
        ))


# singleton
_sdk_settings = SdkSettings()


def get_sdk_settings() -> SdkSettings:
    return _sdk_settings

