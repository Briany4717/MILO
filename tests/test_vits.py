"""
Script de prueba para verificar el backend VITS
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tts_processor import VITSBackend
from src.logger import setup_logger

logger = setup_logger("test_vits")

def test_vits_basic():
    """Prueba básica de VITS"""
    logger.info("=== Prueba 1: Inicialización básica de VITS ===")
    
    try:
        # Inicializar VITS con configuración por defecto
        backend = VITSBackend(
            model_name="tts_models/es/css10/vits",
            emotion="neutral",
            speed=1.0
        )
        
        logger.info(f"✅ VITS inicializado correctamente")
        logger.info(f"📊 Sample rate: {backend.sample_rate} Hz")
        logger.info(f"🎭 Emoción: {backend.emotion}")
        logger.info(f"⚡ Velocidad: {backend.speed}")
        
        return backend
    
    except Exception as e:
        logger.error(f"❌ Error al inicializar VITS: {e}")
        raise


def test_vits_generation(backend):
    """Prueba generación de audio con VITS"""
    logger.info("\n=== Prueba 2: Generación de audio ===")
    
    test_text = "Hola, soy MILO y estoy probando el sistema de voz VITS. Este modelo ofrece mejor expresión emocional."
    output_path = "temp/test_vits_output.wav"
    
    # Crear directorio temp si no existe
    os.makedirs("temp", exist_ok=True)
    
    try:
        logger.info(f"📝 Texto: '{test_text}'")
        backend.generate_audio(test_text, output_path)
        
        # Verificar que se creó el archivo
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            logger.info(f"✅ Audio generado: {output_path}")
            logger.info(f"📦 Tamaño: {file_size / 1024:.2f} KB")
        else:
            logger.error(f"❌ No se generó el archivo de audio")
            return False
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Error al generar audio: {e}")
        raise


def test_vits_emotions(backend):
    """Prueba generación con diferentes emociones (si el modelo las soporta)"""
    logger.info("\n=== Prueba 3: Test de emociones ===")
    
    emotions = ["neutral", "happy", "sad", "angry"]
    test_text = "Esta es una prueba de expresión emocional con VITS"
    
    os.makedirs("temp", exist_ok=True)
    
    for emotion in emotions:
        try:
            logger.info(f"\n🎭 Probando emoción: {emotion}")
            backend.emotion = emotion
            output_path = f"temp/test_vits_{emotion}.wav"
            
            backend.generate_audio(test_text, output_path)
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"✅ Audio con {emotion}: {file_size / 1024:.2f} KB")
            
        except Exception as e:
            logger.warning(f"⚠️  Emoción '{emotion}' no soportada o error: {e}")
            # Continuar con las demás emociones


def test_vits_speed(backend):
    """Prueba generación con diferentes velocidades"""
    logger.info("\n=== Prueba 4: Test de velocidad ===")
    
    speeds = [0.8, 1.0, 1.2]
    test_text = "Probando diferentes velocidades de síntesis"
    
    os.makedirs("temp", exist_ok=True)
    
    for speed in speeds:
        try:
            logger.info(f"\n⚡ Probando velocidad: {speed}x")
            backend.speed = speed
            output_path = f"temp/test_vits_speed_{speed}.wav"
            
            backend.generate_audio(test_text, output_path)
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"✅ Audio a {speed}x: {file_size / 1024:.2f} KB")
            
        except Exception as e:
            logger.error(f"❌ Error con velocidad {speed}x: {e}")


def main():
    """Ejecutar todas las pruebas"""
    logger.info("🚀 Iniciando pruebas de VITS\n")
    
    try:
        # Prueba 1: Inicialización
        backend = test_vits_basic()
        
        # Prueba 2: Generación básica
        test_vits_generation(backend)
        
        # Prueba 3: Emociones (puede fallar si el modelo no las soporta)
        test_vits_emotions(backend)
        
        # Prueba 4: Velocidades
        test_vits_speed(backend)
        
        logger.info("\n" + "="*60)
        logger.info("✅ Todas las pruebas completadas")
        logger.info("📁 Archivos de audio generados en: temp/")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"\n❌ Pruebas fallidas: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
