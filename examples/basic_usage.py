#!/usr/bin/env python3
"""
Ejemplo de uso del LLM Arch SDK

Este script demuestra cómo usar el SDK para hacer llamadas a un servidor LLM
con autenticación automática y manejo de errores.
"""

import logging
import os
from dotenv import load_dotenv
from llm_arch_sdk.adapters.llama_adapter import LlamaAdapter

# Configurar logging para ver los logs de Langfuse
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Cargar variables de entorno desde el archivo .env (forzado)
_env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=_env_path, override=True)

def example_health(client):
    print("\n🔍 Probando Health Check...")
    try:
        health_response = client.health()
        print("✅ Health check exitoso:")
        print(f"   Estado: {health_response.status}")
        print(f"   Versión del servidor: {health_response.version}")
    except Exception as e:
        print(f"⚠️  Health check falló: {e}")
        
def example_chat_completions(client):
    print("\n📝 Probando Chat Completions...")
    try:
        trace_metadata = {"flow": "basic_usage", "user_id": "demo"}
        trace_tags = ["example", "chat", "basic_usage"]
        chat_response = client.chat.create(
            model="llama-7b",  
            messages=[
                {"role": "system", "content": "Eres un asistente útil."},
                {"role": "user", "content": "Hola, ¿cuál es la capital de Francia?"}
            ],
            max_tokens=100,
            temperature=0.7,
            trace_metadata=trace_metadata,
            trace_tags=trace_tags,
        )
        print("✅ Chat completion exitoso:")
        print(f"   Respuesta: {chat_response.choices[0].message.content}")
        print(f"   Modelo usado: {chat_response.model}")
        print(f"   Tokens usados: {chat_response.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️  Chat completion falló: {e}")
        
def example_text_completions(client):
    print("\n✍️  Probando Text Completions...")
    try:
        trace_metadata = {"flow": "basic_usage", "user_id": "demo"}
        trace_tags = ["example", "completions", "basic_usage"]
        completion_response = client.completions.create(
            model="llama-7b", 
            prompt="Escribe un poema corto sobre la inteligencia artificial.",
            max_tokens=50,
            temperature=0.7,
            trace_metadata=trace_metadata,
            trace_tags=trace_tags,
        )
        print("✅ Text completion exitoso:")
        print(f"   Respuesta: {completion_response.content.strip()}")
        print(f"   Modelo usado: {completion_response.model}")
        print(f"   Tokens usados: {completion_response.tokens_predicted}")
    except Exception as e:
        print(f"⚠️  Text completion falló: {e}")
        
def example_embeddings(client):
    # Probar embeddings
    print("\n🧠 Probando Embeddings...")
    try:
        trace_metadata = {"flow": "basic_usage", "user_id": "demo"}
        trace_tags = ["example", "embeddings", "basic_usage"]
        response = client.embeddings.create(
            model="llama-embedding-7b",
            input=["Inteligencia artificial", "Aprendizaje automático"],
            trace_metadata=trace_metadata,
            trace_tags=trace_tags,
        )
        print("✅ Embeddings exitoso:")
        
        for i, embedding in enumerate(response.data):
            print(f"   Input: {response.input[i]}")
            print(f"   Embedding vector (primeros 5 valores): {embedding.embedding[:5]}...")
        print(f"   Número de embeddings: {len(response.data)}")
        print(f"   Dimensiones: {len(response.data[0].embedding)}")
        print(f"   Modelo usado: {response.model}")
            
        # Mostrar similitud aproximada entre los primeros dos embeddings
        if len(response.data) >= 2:
            emb1 = response.data[0].embedding
            emb2 = response.data[1].embedding
            # Similitud coseno aproximada (simplificada)
            dot_product = sum(a*b for a,b in zip(emb1, emb2))
            similarity = dot_product / (sum(a**2 for a in emb1)**0.5 * sum(b**2 for b in emb2)**0.5)
            print(f"   Similitud aproximada entre 'Hola mundo' y 'Hello world': {similarity:.3f}")
    except Exception as e:
        print(f"⚠️  Embeddings falló: {e}")
        

def main():
    print("🚀 Probando LLM Arch SDK - LLMAdapter")

    try:
        # Crear adapter con parámetros personalizados
        adapter = LlamaAdapter(
            timeout=60.0
        )
        print("✅ Adapter creado exitosamente")

        # Obtener cliente
        client = adapter.client()
        print("✅ Cliente LLM obtenido")
        
        example_health(client)
        example_chat_completions(client)
        example_text_completions(client)
        example_embeddings(client)
        
        print("\n🎉 Prueba completada!")

    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())