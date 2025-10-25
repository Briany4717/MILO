#!/usr/bin/env python3
"""
Script de prueba para verificar proveedores de LLM (Ollama y Gemini)
"""
import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
load_dotenv()

from src.llm_processor import LLMProcessor
from src.logger import get_logger

logger = get_logger(__name__)

def test_ollama():
    """Prueba el proveedor Ollama"""
    print("\n" + "="*80)
    print("PROBANDO OLLAMA")
    print("="*80)
    
    try:
        llm = LLMProcessor(provider="ollama")
        logger.info("Ollama inicializado correctamente")
        
        # Hacer una pregunta simple
        user_query = "¿Qué es Python en una frase?"
        logger.info(f"Enviando consulta: {user_query}")
        
        response_stream = llm.get_response(user_query)
        
        full_response = ""
        for chunk in response_stream:
            token = chunk.choices[0].delta.content
            if token:
                full_response += token
        
        logger.info(f"Respuesta recibida: {full_response}")
        llm.add_assistant_response(full_response)
        
        print("✅ OLLAMA funcionando correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error con Ollama: {e}")
        logger.exception("Detalles:")
        return False

def test_gemini():
    """Prueba el proveedor Gemini"""
    print("\n" + "="*80)
    print("PROBANDO GEMINI")
    print("="*80)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "tu_api_key_aqui":
        logger.warning("⚠️  GEMINI_API_KEY no configurada - saltando prueba de Gemini")
        print("Para probar Gemini, configura GEMINI_API_KEY en tu archivo .env")
        return None
    
    try:
        llm = LLMProcessor(provider="gemini")
        logger.info("Gemini inicializado correctamente")
        
        # Hacer una pregunta simple
        user_query = "¿Qué es Python en una frase?"
        logger.info(f"Enviando consulta: {user_query}")
        
        response_stream = llm.get_response(user_query)
        
        full_response = ""
        try:
            for chunk in response_stream:
                if hasattr(chunk, 'text'):
                    full_response += chunk.text
                    logger.debug(f"Chunk recibido: {chunk.text}")
                elif hasattr(chunk, 'parts'):
                    for part in chunk.parts:
                        if hasattr(part, 'text'):
                            full_response += part.text
                            logger.debug(f"Part recibido: {part.text}")
        except Exception as e:
            logger.error(f"Error durante streaming: {e}")
            if hasattr(response_stream, 'text'):
                full_response = response_stream.text
        
        logger.info(f"Respuesta recibida ({len(full_response)} chars): {full_response}")
        
        if not full_response.strip():
            logger.error("❌ La respuesta de Gemini está vacía")
            return False
        
        llm.add_assistant_response(full_response)
        
        print("✅ GEMINI funcionando correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error con Gemini: {e}")
        logger.exception("Detalles:")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*80)
    print("PRUEBA DE PROVEEDORES LLM")
    print("="*80)
    
    # Mostrar configuración actual
    llm_provider = os.getenv("LLM_PROVIDER", "ollama")
    print(f"\nProveedor configurado en .env: {llm_provider}")
    
    results = {}
    
    # Probar Ollama
    results['ollama'] = test_ollama()
    
    # Probar Gemini
    results['gemini'] = test_gemini()
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE PRUEBAS")
    print("="*80)
    
    for provider, result in results.items():
        if result is True:
            print(f"✅ {provider.upper()}: Funcionando")
        elif result is False:
            print(f"❌ {provider.upper()}: Error")
        else:
            print(f"⚠️  {provider.upper()}: No probado (falta configuración)")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
