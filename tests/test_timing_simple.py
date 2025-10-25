"""
Test simple de timing de TTS - sin cargar múltiples instancias
"""

import sys
import os
import time
import gc
import torch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.logger import setup_logger

logger = setup_logger("test_timing")

def clear_gpu_memory():
    """Liberar memoria GPU"""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        logger.info("🧹 Memoria GPU liberada")

def test_xtts_simple():
    """Test simple de XTTS - solo medir generación"""
    from src.tts_processor import TTSProcessor
    
    logger.info("=" * 60)
    logger.info("⏱️  TEST DE TIMING - XTTS Preset (Abrahan Mack + Happy)")
    logger.info("=" * 60)
    
    test_text = "¡Hola! ¿Cómo estás? Esta es una prueba de timing."
    
    # Inicialización (solo primera vez en servidor real)
    logger.info("\n📦 Inicializando backend...")
    start = time.time()
    backend = TTSProcessor()
    init_time = time.time() - start
    logger.info(f"✅ Inicialización: {init_time:.2f}s (solo primera vez)")
    
    # Primera generación (puede incluir warmup)
    logger.info("\n🎤 Generando audio (primera vez - con warmup CUDA)...")
    start = time.time()
    backend.generate_audio(test_text, "temp/timing1.wav")
    gen1_time = time.time() - start
    logger.info(f"✅ Primera generación: {gen1_time:.2f}s")
    
    # Segunda generación (tiempo real típico)
    logger.info("\n🔥 Generando audio (segunda vez - sin warmup)...")
    start = time.time()
    backend.generate_audio(test_text, "temp/timing2.wav")
    gen2_time = time.time() - start
    logger.info(f"✅ Segunda generación: {gen2_time:.2f}s")
    
    # Tercera para confirmar
    logger.info("\n🔥 Generando audio (tercera vez - confirmación)...")
    start = time.time()
    backend.generate_audio(test_text, "temp/timing3.wav")
    gen3_time = time.time() - start
    logger.info(f"✅ Tercera generación: {gen3_time:.2f}s")
    
    # Promedio de generación estable
    avg_gen = (gen2_time + gen3_time) / 2
    
    # Info del archivo
    file_size_kb = os.path.getsize("temp/timing1.wav") / 1024
    
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMEN")
    logger.info("=" * 60)
    logger.info(f"Inicialización (una sola vez):   {init_time:.2f}s")
    logger.info(f"Primera generación (con warmup): {gen1_time:.2f}s")
    logger.info(f"Generación promedio (normal):    {avg_gen:.2f}s")
    logger.info(f"Tamaño del audio:                {file_size_kb:.2f} KB")
    
    # Transmisión WebSocket (estimado)
    transmission_time = file_size_kb / 5000  # 5MB/s red local
    logger.info(f"\n📡 Transmisión WebSocket (~5MB/s): {transmission_time*1000:.1f}ms")
    
    total_response = avg_gen + transmission_time
    
    logger.info("\n" + "=" * 60)
    logger.info("⏰ TIEMPO TOTAL DE RESPUESTA")
    logger.info("=" * 60)
    logger.info(f"Generación TTS:       {avg_gen:.2f}s  ({avg_gen/total_response*100:.1f}%)")
    logger.info(f"Transmisión WS:       {transmission_time:.3f}s  ({transmission_time/total_response*100:.1f}%)")
    logger.info(f"TOTAL:                {total_response:.2f}s")
    
    logger.info("\n💡 CONCLUSIÓN:")
    logger.info(f"  • El tiempo de transmisión es NEGLIGIBLE ({transmission_time*1000:.0f}ms)")
    logger.info(f"  • El 99% del tiempo es GENERACIÓN TTS (~{avg_gen:.1f}s)")
    logger.info(f"  • En conversación real: ~{avg_gen:.1f}s por respuesta")
    logger.info("=" * 60)
    
    # Limpiar
    del backend
    clear_gpu_memory()

if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)
    test_xtts_simple()
