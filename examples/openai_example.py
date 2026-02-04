#!/usr/bin/env python3
"""
Ejemplo completo de uso del LLM Arch SDK con OpenAI

Este script demuestra cómo usar el adapter de OpenAI para:
- Chat completions
- Text completions
- Embeddings
"""

import logging
import os
import uuid
from dotenv import load_dotenv
from llm_arch_sdk.adapters.open_ai_adapter import OpenAIAdapter
from llm_arch_sdk.observability.langfuse_client import set_active_trace, clear_active_trace

# Configurar logging para ver los logs de Langfuse
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Reducir warnings del wrapper Langfuse
logging.getLogger("langfuse").setLevel(logging.ERROR)

# Cargar variables de entorno desde el archivo .env (forzado)
_env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=_env_path, override=True)

def _endpoint_name(prefix, func):
    return f"{prefix}.{getattr(func, '__name__', 'create')}"


def example_chat_completions(client):
    # 1. Probar Chat Completions
    print("\n📝 Probando Chat Completions...")
    trace_id = uuid.uuid4().hex
    set_active_trace({"trace_id": trace_id})
    try:
        metadata = {
            "flow": example_chat_completions.__name__,
            "endpoint": _endpoint_name("client.chat.completions", client.chat.completions.create),
            "model": "gpt-3.5-turbo",
        }
        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "system", "content": "Eres un asistente útil."},
                {"role": "user", "content": "Hola, ¿cuál es la capital de Francia?"}
            ],
            max_tokens=100,
            temperature=0.7,
            metadata=metadata,
            trace_id=trace_id,
        )
        print("✅ Chat completion exitoso:")
        print(f"   Respuesta: {chat_response.choices[0].message.content}")
        print(f"   Modelo usado: {chat_response.model}")
        print(f"   Tokens usados: {chat_response.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️  Chat completion falló: {e}")
    finally:
        clear_active_trace()

def example_text_completions(client):
    # 2. Probar Text Completions
    print("\n✍️  Probando Text Completions...")
    trace_id = uuid.uuid4().hex
    set_active_trace({"trace_id": trace_id})
    try:
        metadata = {
            "flow": example_text_completions.__name__,
            "endpoint": _endpoint_name("client.completions", client.completions.create),
            "model": "text-davinci-003",
        }
        completion_response = client.completions.create(
            model="text-davinci-003", 
            prompt="Escribe un poema corto sobre la inteligencia artificial.",
            max_tokens=50,
            temperature=0.7,
            metadata=metadata,
            trace_id=trace_id,
        )
        print("✅ Text completion exitoso:")
        print(f"   Respuesta: {completion_response.choices[0].text.strip()}")
        print(f"   Modelo usado: {completion_response.model}")
        print(f"   Tokens usados: {completion_response.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️  Text completion falló: {e}")
    finally:
        clear_active_trace()
        
def example_embeddings(client):
    # 3. Probar Embeddings
    print("\n🧠 Probando Embeddings...")
    trace_id = uuid.uuid4().hex
    set_active_trace({"trace_id": trace_id})
    try:
        metadata = {
            "flow": example_embeddings.__name__,
            "endpoint": _endpoint_name("client.embeddings", client.embeddings.create),
            "model": "text-embedding-ada-002",
        }
        embedding_response = client.embeddings.create(
            model="text-embedding-ada-002", 
            input=["Inteligencia artificial", "Aprendizaje automático"],
            metadata=metadata,
            trace_id=trace_id,
        )
        print("✅ Embeddings exitosos:")
        for i, embedding in enumerate(embedding_response.data):
            print(f"   Embedding {i}: Dimensiones={len(embedding.embedding)}")
    except Exception as e:
        print(f"⚠️  Embeddings fallaron: {e}")
    finally:
        clear_active_trace()
        

def main():
    print("🚀 Probando LLM Arch SDK con OpenAI - Ejemplo completo")
    try:
        # Crear adapter con parámetros personalizados
        adapter = OpenAIAdapter(
            timeout=60.0
        )
        print("✅ OpenAI Adapter creado")

        # Obtener cliente
        client = adapter.client()
        print("✅ Cliente OpenAI obtenido")
        
        example_chat_completions(client)
        example_text_completions(client)
        example_embeddings(client)
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())