#!/usr/bin/env python3
"""
Ejemplo completo de uso del LLM Arch SDK con OpenAI

Este script demuestra cómo usar el adapter de OpenAI para:
- Chat completions
- Text completions
- Embeddings
"""

import os
from dotenv import load_dotenv
from llm_arch_sdk.adapters.open_ai_adapter import OpenAIAdapter

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def example_chat_completions(client):
    # 1. Probar Chat Completions
    print("\n📝 Probando Chat Completions...")
    try:
        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "system", "content": "Eres un asistente útil."},
                {"role": "user", "content": "Hola, ¿cuál es la capital de Francia?"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        print("✅ Chat completion exitoso:")
        print(f"   Respuesta: {chat_response.choices[0].message.content}")
        print(f"   Modelo usado: {chat_response.model}")
        print(f"   Tokens usados: {chat_response.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️  Chat completion falló: {e}")

def example_text_completions(client):
    # 2. Probar Text Completions
    print("\n✍️  Probando Text Completions...")
    try:
        completion_response = client.completions.create(
            model="text-davinci-003", 
            prompt="Escribe un poema corto sobre la inteligencia artificial.",
            max_tokens=50,
            temperature=0.7
        )
        print("✅ Text completion exitoso:")
        print(f"   Respuesta: {completion_response.choices[0].text.strip()}")
        print(f"   Modelo usado: {completion_response.model}")
        print(f"   Tokens usados: {completion_response.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️  Text completion falló: {e}")
        
def example_embeddings(client):
    # 3. Probar Embeddings
    print("\n🧠 Probando Embeddings...")
    try:
        embedding_response = client.embeddings.create(
            model="text-embedding-ada-002", 
            input=["Inteligencia artificial", "Aprendizaje automático"]
        )
        print("✅ Embeddings exitosos:")
        for i, embedding in enumerate(embedding_response.data):
            print(f"   Embedding {i}: Dimensiones={len(embedding.embedding)}")
    except Exception as e:
        print(f"⚠️  Embeddings fallaron: {e}")
        

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