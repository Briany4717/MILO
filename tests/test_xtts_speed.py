#!/usr/bin/env python3
"""
Script de prueba para comparar velocidad entre modo CLONE y modo PRESET de XTTS
"""
import os
import sys
import time
from pathlib import Path

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
load_dotenv()

from src.tts_processor import XTTSBackend
from src.logger import get_logger
import src.config as config

logger = get_logger(__name__)

def test_xtts_mode(mode, preset_voice=None):
    """Prueba XTTS en un modo específico"""
    print("\n" + "="*80)
    print(f"PROBANDO XTTS EN MODO: {mode.upper()}")
    print("="*80)
    
    test_text = "Hola, esta es una prueba de velocidad del sistema de síntesis de voz."
    output_file = f"temp/test_xtts_{mode}.wav"
    
    # Crear directorio temp si no existe
    os.makedirs("temp", exist_ok=True)
    
    try:
        # Inicialización
        print(f"📦 Inicializando XTTS en modo {mode}...")
        start_init = time.time()
        
        if mode == "clone":
            backend = XTTSBackend(
                model_name=config.TTS_MODEL,
                device="cuda",
                mode="clone",
                speaker_wav=config.TTS_SPEAKER_WAV
            )
        else:  # preset
            backend = XTTSBackend(
                model_name=config.TTS_MODEL,
                device="cuda",
                mode="preset",
                preset_voice=preset_voice or "Daisy Studious"
            )
        
        init_time = time.time() - start_init
        print(f"✅ Inicialización completada en {init_time:.2f}s")
        
        # Generación de audio
        print(f"🎤 Generando audio: '{test_text}'")
        start_gen = time.time()
        
        backend.generate_audio(test_text, output_file)
        
        gen_time = time.time() - start_gen
        print(f"✅ Audio generado en {gen_time:.2f}s")
        print(f"📄 Archivo guardado: {output_file}")
        
        # Verificar tamaño del archivo
        file_size = os.path.getsize(output_file)
        print(f"📊 Tamaño del archivo: {file_size / 1024:.2f} KB")
        
        return {
            "mode": mode,
            "init_time": init_time,
            "gen_time": gen_time,
            "total_time": init_time + gen_time,
            "file_size": file_size,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"❌ Error en modo {mode}: {e}")
        logger.exception("Detalles:")
        return {
            "mode": mode,
            "success": False,
            "error": str(e)
        }

def main():
    """Ejecuta las pruebas de comparación"""
    print("\n" + "="*80)
    print("COMPARACIÓN DE VELOCIDAD: XTTS CLONE vs PRESET")
    print("="*80)
    
    results = []
    
    # Probar modo PRESET (más rápido)
    print("\n🚀 PROBANDO MODO PRESET (voces predefinidas - rápido)")
    result_preset = test_xtts_mode("preset", preset_voice="Daisy Studious")
    results.append(result_preset)
    
    # Probar modo CLONE (más lento pero personalizado)
    print("\n🎨 PROBANDO MODO CLONE (clonación de voz - personalizado)")
    if os.path.exists("data/voice_embedding.pth") or os.path.exists(config.TTS_SPEAKER_WAV):
        result_clone = test_xtts_mode("clone")
        results.append(result_clone)
    else:
        print("⚠️  Saltando modo CLONE - no se encontró voice_embedding.pth ni speaker_wav")
        results.append({
            "mode": "clone",
            "success": False,
            "error": "Archivos necesarios no encontrados"
        })
    
    # Mostrar resumen
    print("\n" + "="*80)
    print("RESUMEN DE RESULTADOS")
    print("="*80)
    
    for result in results:
        mode = result["mode"].upper()
        if result["success"]:
            print(f"\n✅ {mode}:")
            print(f"   ⏱️  Tiempo de inicialización: {result['init_time']:.2f}s")
            print(f"   🎤 Tiempo de generación: {result['gen_time']:.2f}s")
            print(f"   ⚡ Tiempo total: {result['total_time']:.2f}s")
            print(f"   📊 Tamaño: {result['file_size'] / 1024:.2f} KB")
        else:
            print(f"\n❌ {mode}: {result.get('error', 'Error desconocido')}")
    
    # Calcular mejora de velocidad
    if len([r for r in results if r["success"]]) == 2:
        preset_time = next(r["gen_time"] for r in results if r["mode"] == "preset" and r["success"])
        clone_time = next(r["gen_time"] for r in results if r["mode"] == "clone" and r["success"])
        speedup = clone_time / preset_time
        improvement = ((clone_time - preset_time) / clone_time) * 100
        
        print("\n" + "="*80)
        print("ANÁLISIS DE RENDIMIENTO")
        print("="*80)
        print(f"🚀 Modo PRESET es {speedup:.2f}x más rápido que CLONE")
        print(f"📈 Mejora de velocidad: {improvement:.1f}%")
        print(f"💡 Recomendación: Usa modo PRESET para producción (más rápido)")
        print(f"🎨 Usa modo CLONE solo si necesitas una voz específica personalizada")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
