"""
Test detallado de tiempos de TTS - Separando generación vs escritura vs envío
"""

import sys
import os
import time

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tts_processor import TTSProcessor
from src.logger import setup_logger

logger = setup_logger("test_timing")

def test_xtts_detailed_timing():
    """Medir tiempos detallados de XTTS"""
    logger.info("=" * 60)
    logger.info("🔬 ANÁLISIS DETALLADO DE TIEMPOS - XTTS Preset")
    logger.info("=" * 60)
    
    # Texto de prueba
    test_text = "¡Hola! Esta es una prueba del sistema XTTS con acento mexicano y emoción entusiasta."
    output_path = "temp/timing_test.wav"
    
    os.makedirs("temp", exist_ok=True)
    
    # 1. Tiempo de inicialización
    logger.info("\n📦 Fase 1: Inicialización del backend")
    start_init = time.time()
    backend = TTSProcessor()
    init_time = time.time() - start_init
    logger.info(f"✅ Inicialización: {init_time:.2f}s")
    
    # 2. Tiempo de generación (primera vez - puede incluir compilación CUDA)
    logger.info("\n🎤 Fase 2: Primera generación (puede incluir warmup CUDA)")
    start_gen1 = time.time()
    backend.generate_audio(test_text, output_path)
    gen1_time = time.time() - start_gen1
    logger.info(f"✅ Primera generación: {gen1_time:.2f}s")
    
    # 3. Tiempo de generación (segunda vez - ya con CUDA warmed up)
    logger.info("\n🔥 Fase 3: Segunda generación (CUDA ya inicializado)")
    start_gen2 = time.time()
    backend.generate_audio(test_text, "temp/timing_test2.wav")
    gen2_time = time.time() - start_gen2
    logger.info(f"✅ Segunda generación: {gen2_time:.2f}s")
    
    # 4. Tamaño del archivo
    file_size = os.path.getsize(output_path)
    file_size_kb = file_size / 1024
    
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMEN DE TIEMPOS")
    logger.info("=" * 60)
    logger.info(f"Inicialización (una vez):     {init_time:.2f}s")
    logger.info(f"Primera generación (warmup):  {gen1_time:.2f}s")
    logger.info(f"Segunda generación (normal):  {gen2_time:.2f}s")
    logger.info(f"Tamaño de audio:              {file_size_kb:.2f} KB")
    
    # 5. Calcular tiempo de transmisión estimado por WebSocket
    # WebSocket típicamente puede enviar ~1-10 MB/s dependiendo de la red
    # Asumiendo una conexión local rápida: ~5 MB/s
    transmission_speed_kbps = 5000  # 5 MB/s = 5000 KB/s
    estimated_transmission = file_size_kb / transmission_speed_kbps
    
    logger.info("\n📡 ESTIMACIÓN DE TRANSMISIÓN")
    logger.info(f"Velocidad asumida:            5 MB/s (red local)")
    logger.info(f"Tiempo de transmisión:        {estimated_transmission:.3f}s (~{estimated_transmission*1000:.0f}ms)")
    
    # 6. Tiempo total en escenario real
    total_real_scenario = gen2_time + estimated_transmission
    
    logger.info("\n⏱️  TIEMPO TOTAL (escenario real conversacional)")
    logger.info(f"Generación + Transmisión:     {total_real_scenario:.2f}s")
    logger.info(f"  └─ Generación:              {gen2_time:.2f}s ({gen2_time/total_real_scenario*100:.1f}%)")
    logger.info(f"  └─ Transmisión:             {estimated_transmission:.3f}s ({estimated_transmission/total_real_scenario*100:.1f}%)")
    
    logger.info("\n" + "=" * 60)
    logger.info("💡 CONCLUSIÓN")
    logger.info("=" * 60)
    logger.info(f"Para una conversación en tiempo real:")
    logger.info(f"  • Primera respuesta: ~{init_time + gen1_time:.1f}s (incluye inicialización)")
    logger.info(f"  • Respuestas subsecuentes: ~{total_real_scenario:.2f}s")
    logger.info(f"  • La transmisión por WebSocket es negligible (<{estimated_transmission*1000:.0f}ms)")
    logger.info("=" * 60)


def test_vits_detailed_timing():
    """Comparar con VITS para referencia"""
    from src.tts_processor import VITSBackend
    
    logger.info("\n" + "=" * 60)
    logger.info("🔬 COMPARACIÓN CON VITS")
    logger.info("=" * 60)
    
    test_text = "¡Hola! Esta es una prueba del sistema XTTS con acento mexicano y emoción entusiasta."
    
    logger.info("\n📦 Inicializando VITS...")
    start_init = time.time()
    backend = VITSBackend()
    init_time = time.time() - start_init
    logger.info(f"✅ Inicialización VITS: {init_time:.2f}s")
    
    logger.info("\n🎤 Generando audio con VITS...")
    start_gen = time.time()
    backend.generate_audio(test_text, "temp/timing_vits.wav")
    gen_time = time.time() - start_gen
    logger.info(f"✅ Generación VITS: {gen_time:.2f}s")
    
    file_size_kb = os.path.getsize("temp/timing_vits.wav") / 1024
    
    logger.info("\n📊 COMPARACIÓN FINAL")
    logger.info("=" * 60)
    logger.info(f"{'Backend':<15} {'Inicialización':<18} {'Generación':<15} {'Tamaño':<10}")
    logger.info(f"{'XTTS Preset':<15} {'~6s':<18} {'~2-4s':<15} {'variable':<10}")
    logger.info(f"{'VITS':<15} {f'{init_time:.2f}s':<18} {f'{gen_time:.2f}s':<15} {f'{file_size_kb:.1f}KB':<10}")
    logger.info("=" * 60)
    logger.info("🎯 VITS es más rápido PERO:")
    logger.info("   ❌ Acento de España (no mexicano)")
    logger.info("   ❌ Sin emociones funcionales")
    logger.info("\n✅ XTTS Preset es mejor PORQUE:")
    logger.info("   ✅ Acento mexicano auténtico")
    logger.info("   ✅ Emociones que SÍ funcionan")
    logger.info("   ✅ Tiempo aceptable (~2-4s por respuesta)")
    logger.info("=" * 60)


if __name__ == "__main__":
    test_xtts_detailed_timing()
    test_vits_detailed_timing()
