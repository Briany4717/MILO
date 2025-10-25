#!/usr/bin/env python3
"""
Script de prueba para verificar la instalación de Piper TTS
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tts_processor import TTSProcessor
from src.logger import get_logger

logger = get_logger(__name__)

def test_piper():
    """Prueba la funcionalidad de Piper TTS"""
    
    print("=" * 60)
    print("🧪 Test de Piper TTS")
    print("=" * 60)
    
    # Verificar que el modelo existe
    model_path = "models/piper/es_ES-sharvard-medium.onnx"
    config_path = "models/piper/es_ES-sharvard-medium.onnx.json"
    
    if not os.path.exists(model_path):
        print(f"\n❌ Modelo no encontrado: {model_path}")
        print("\n📥 Para descargar el modelo, ejecuta:")
        print("   ./scripts/download_piper_model.sh sharvard-medium")
        print("\nO descarga manualmente desde:")
        print("   https://huggingface.co/rhasspy/piper-voices/tree/main/es/es_ES/sharvard/medium")
        return False
    
    print(f"✅ Modelo encontrado: {model_path}")
    
    try:
        # Inicializar Piper
        print("\n🔧 Inicializando Piper TTS...")
        tts = TTSProcessor(
            backend_type="piper",
            model_path=model_path,
            config_path=config_path,
            speaker_id=0
        )
        print(f"✅ Piper inicializado correctamente")
        print(f"   Sample rate: {tts.sample_rate} Hz")
        
        # Generar audio de prueba
        print("\n🎤 Generando audio de prueba...")
        test_text = "Hola, soy MILO. Este es un test de Piper TTS en español."
        output_path = "temp/test_piper_output.wav"
        
        # Crear directorio temp si no existe
        os.makedirs("temp", exist_ok=True)
        
        tts.generate_audio(test_text, output_path)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ Audio generado correctamente: {output_path}")
            print(f"   Tamaño del archivo: {file_size / 1024:.2f} KB")
            print(f"\n🎵 Para reproducir el audio:")
            print(f"   ffplay {output_path}")
            print(f"   # o")
            print(f"   aplay {output_path}")
            return True
        else:
            print("❌ Error: El archivo de audio no se generó")
            return False
            
    except ImportError as e:
        print(f"\n❌ Error de importación: {e}")
        print("\n📦 Para instalar Piper TTS, ejecuta:")
        print("   pip install piper-tts onnxruntime")
        return False
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        logger.exception("Error en test de Piper")
        return False

def test_xtts():
    """Prueba la funcionalidad de XTTS (para comparación)"""
    
    print("\n" + "=" * 60)
    print("🧪 Test de XTTS v2 (para comparación)")
    print("=" * 60)
    
    if not os.path.exists("data/voice_embedding.pth"):
        print("⚠️  voice_embedding.pth no encontrado, saltando test de XTTS")
        return None
    
    try:
        print("\n🔧 Inicializando XTTS v2...")
        tts = TTSProcessor(backend_type="xtts")
        print(f"✅ XTTS v2 inicializado correctamente")
        print(f"   Sample rate: {tts.sample_rate} Hz")
        
        print("\n🎤 Generando audio de prueba...")
        test_text = "Hola, soy MILO. Este es un test de XTTS v2 en español."
        output_path = "temp/test_xtts_output.wav"
        
        os.makedirs("temp", exist_ok=True)
        tts.generate_audio(test_text, output_path)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ Audio generado correctamente: {output_path}")
            print(f"   Tamaño del archivo: {file_size / 1024:.2f} KB")
            return True
        else:
            print("❌ Error: El archivo de audio no se generó")
            return False
            
    except Exception as e:
        print(f"⚠️  Error en test de XTTS: {e}")
        return False

if __name__ == "__main__":
    piper_ok = test_piper()
    
    # Opcional: probar XTTS también
    print("\n" + "=" * 60)
    respuesta = input("¿Quieres probar XTTS v2 también? (s/n): ").lower()
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        xtts_ok = test_xtts()
    
    print("\n" + "=" * 60)
    print("📊 Resumen de tests")
    print("=" * 60)
    print(f"Piper TTS: {'✅ OK' if piper_ok else '❌ FALLÓ'}")
    
    if piper_ok:
        print("\n🎉 ¡Piper TTS está listo para usar!")
        print("   Configura TTS_BACKEND=piper en tu archivo .env")
    else:
        print("\n⚠️  Revisa los errores anteriores para solucionar los problemas")
    
    sys.exit(0 if piper_ok else 1)
