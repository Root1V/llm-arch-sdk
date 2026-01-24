# LLM Arch SDK

SDK para consumir llama-server con autenticación y renovación automática de tokens.

## Descripción

Este SDK proporciona una interfaz unificada para interactuar con servidores LLM (como llama-server), manejando autenticación, renovación de tokens, circuit breakers y diferentes adaptadores para proveedores como OpenAI y Llama.

## Características

- **Autenticación automática**: Manejo de tokens con renovación automática.
- **Circuit Breaker**: Protección contra fallos en las llamadas a la API.
- **Adaptadores múltiples**: Soporte para OpenAI y Llama.
- **Normalización de respuestas**: Estandarización de respuestas de diferentes proveedores.
- **Cliente HTTP robusto**: Uso de httpx con configuraciones personalizables.

## Instalación

### Requisitos

- Python >= 3.14

### Instalación desde código fuente

1. Clona el repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd llm_arch_sdk
   ```

2. Instala las dependencias:
   ```bash
   uv sync
   ```

3. Activa el entorno virtual:
   ```bash
   source .venv/bin/activate
   ```

4. Instala el paquete en modo editable (para que ejecuten los test)
   ```bash
   pip install -e .
   ```

## Ejemplos de uso

La carpeta `examples/` contiene scripts demostrativos para probar las funcionalidades del SDK:

### Ejemplo básico con Llama
```bash
uv run python examples/basic_usage.py
```

### Ejemplo con OpenAI
```bash
uv run python examples/openai_example.py
```

Estos ejemplos incluyen manejo de errores y funcionan tanto con servidores reales como con configuraciones de prueba.

### Configuración de autenticación

Crea un archivo `.env` en la raíz del proyecto:

```
LLM_BASE_URL=
LLM_USERNAME=
LLM_PASSWORD=

```

## Estructura del Proyecto

```
llm_arch_sdk/
├── src/
│   └── llm-arch-sdk/
│       ├── adapters/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── llama_adapter.py
│       │   └── open_ai_adapter.py
│       ├── auth/
│       │   ├── __init__.py
│       │   └── token_manager.py
│       ├── client/
│       │   ├── __init__.py
│       │   ├── base_client.py
│       │   ├── chat_completions.py
│       │   ├── completions.py
│       │   ├── embeddings.py
│       │   ├── llm_client.py
│       │   └── test_llm_client.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── chat_completion.py
│       │   ├── completion.py
│       │   ├── generation_settings.py
│       │   ├── llm_response.py
│       │   ├── stop_type.py
│       │   ├── timings.py
│       │   └── usage.py
│       ├── normalizers/
│       │   ├── __init__.py
│       │   ├── completion_detector.py
│       │   └── content_normalizer.py
│       └── transport/
│           ├── __init__.py
│           ├── auth_http_client_factory.py
│           ├── circuit_breaker.py
│           └── http_client_factory.py
├── test/
│   ├── adapters/
│   │   ├── test_llama_adapter.py
│   │   └── test_openai_adapter.py
│   ├── auth/
│   │   └── test_token_manager.py
│   ├── client/
│   │   ├── test_chat_completions.py
│   │   ├── test_completions.py
│   │   ├── test_embeddings.py
│   │   └── test_llm_client.py
│   ├── models/
│   │   └── test_models.py
│   ├── normalizers/
│   │   └── test_normalizers.py
│   └── transport/
│       └── test_circuit_breaker.py
├── examples/
│   ├── basic_usage.py
│   └── openai_example.py
├── pyproject.toml
├── uv.lock
├── .gitignore
├── LICENSE
└── README.md
```

### Descripción de módulos

- **adapters/**: Adaptadores para diferentes proveedores de LLM (OpenAI, Llama).
- **auth/**: Gestión de autenticación y tokens.
- **client/**: Cliente principal y endpoints específicos (chat, completions, embeddings).
- **models/**: Modelos de datos para respuestas y configuraciones.
- **normalizers/**: Utilidades para normalizar respuestas.
- **transport/**: Manejo de transporte HTTP, circuit breakers y fábricas de clientes.

## Pruebas

Para ejecutar las pruebas:

```bash
uv run pytest test/
```

El proyecto incluye 83 pruebas unitarias organizadas en una estructura que refleja el código fuente, facilitando el mantenimiento y la localización de tests relacionados con módulos específicos.

### Estructura de pruebas

- `test/client/`: Tests para clientes y endpoints (chat, completions, embeddings)
- `test/auth/`: Tests para autenticación y gestión de tokens
- `test/transport/`: Tests para circuit breaker y transporte HTTP
- `test/adapters/`: Tests para adaptadores de proveedores (Llama, OpenAI)
- `test/models/`: Tests para modelos de datos y parsing JSON
- `test/normalizers/`: Tests para normalización de contenido

### Cobertura de pruebas

- **TokenManager**: Autenticación, renovación de tokens, circuit breaker.
- **CircuitBreaker**: Estados CLOSED/OPEN/HALF_OPEN, timeouts.
- **Clientes**: ChatCompletions, Completions, Embeddings.
- **Adaptadores**: LlamaAdapter, OpenAIAdapter.
- **Modelos**: Parsing de respuestas JSON, validación de datos.
- **Normalizadores**: Detección de completitud semántica, limpieza de texto.
- **Transporte**: Manejo de HTTP, errores, timeouts.

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## Autor

Emeric Espiritu Santiago
