"""
Test de precisión del sistema STT
Prueba diferentes configuraciones y mide la precisión
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.stt_processor import STTProcessor
from src.logger import setup_logger

logger = setup_logger("test_stt")

def test_current_config():
    """Test con la configuración actual del .env"""
    logger.info("=" * 60)
    logger.info("🎯 TEST DE PRECISIÓN STT - Configuración Actual")
    logger.info("=" * 60)
    
    # Inicializar con config actual
    stt = STTProcessor()
    
    logger.info(f"\n📊 Configuración:")
    logger.info(f"  Modelo: {stt.model_size}")
    logger.info(f"  Device: {stt.device}")
    
    # Nota para el usuario
    logger.info("\n" + "=" * 60)
    logger.info("💡 INSTRUCCIONES")
    logger.info("=" * 60)
    logger.info("Para probar la precisión:")
    logger.info("1. Graba un audio de prueba con palabras difíciles")
    logger.info("2. Guárdalo en: temp/test_audio.wav")
    logger.info("3. Ejecuta este script nuevamente")
    logger.info("\nPalabras difíciles recomendadas para probar:")
    logger.info("  - Español: exacerbación, idiosincrasia, murciélago")
    logger.info("  - Inglés: through, acknowledge, rhythm")
    logger.info("  - Números: veintitrés mil cuatrocientos cincuenta y seis")
    logger.info("  - Técnicas: inteligencia artificial, machine learning")
    logger.info("=" * 60)
    
    # Verificar si existe audio de prueba
    test_audio = "temp/test_audio.wav"
    if os.path.exists(test_audio):
        logger.info(f"\n🎤 Transcribiendo: {test_audio}")
        
        start = time.time()
        text = stt.transcribe(test_audio)
        elapsed = time.time() - start
        
        logger.info("\n" + "=" * 60)
        logger.info("📝 RESULTADO")
        logger.info("=" * 60)
        logger.info(f"Transcripción: {text}")
        logger.info(f"Tiempo: {elapsed:.2f}s")
        logger.info(f"Palabras: {len(text.split())}")
        logger.info("=" * 60)
    else:
        logger.warning(f"\n⚠️  No se encontró {test_audio}")
        logger.info("Crea un archivo de audio para probar la precisión")


def compare_models():
    """Comparar diferentes modelos (solo si quieres probar)"""
    logger.info("\n" + "=" * 60)
    logger.info("📊 COMPARACIÓN DE MODELOS")
    logger.info("=" * 60)
    
    test_audio = "temp/test_audio.wav"
    if not os.path.exists(test_audio):
        logger.warning("No hay audio de prueba, saltando comparación")
        return
    
    models = ["base", "small", "medium", "large-v3"]
    
    logger.info(f"\nProbando {len(models)} modelos...")
    logger.info("(Esto puede tardar varios minutos)\n")
    
    results = []
    
    for model in models:
        try:
            logger.info(f"🔄 Probando modelo: {model}")
            stt = STTProcessor(model_size=model)
            
            start = time.time()
            text = stt.transcribe(test_audio)
            elapsed = time.time() - start
            
            results.append({
                "model": model,
                "text": text,
                "time": elapsed,
                "words": len(text.split())
            })
            
            logger.info(f"  ✅ Completado en {elapsed:.2f}s")
            
            # Liberar memoria
            del stt
            
        except Exception as e:
            logger.error(f"  ❌ Error con {model}: {e}")
    
    # Mostrar resultados
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESULTADOS COMPARATIVOS")
    logger.info("=" * 60)
    
    for result in results:
        logger.info(f"\n🎤 {result['model'].upper()}")
        logger.info(f"  Tiempo: {result['time']:.2f}s")
        logger.info(f"  Palabras: {result['words']}")
        logger.info(f"  Texto: {result['text'][:100]}...")
    
    logger.info("\n" + "=" * 60)


if __name__ == "__main__":
    test_current_config()
    
    # Descomentar para comparar modelos:
    # compare_models()
