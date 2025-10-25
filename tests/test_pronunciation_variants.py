#!/usr/bin/env python3
"""
Script de prueba para verificar las variantes de pronunciación.
"""
import asyncio
import websockets


async def test_variant(variant: str, description: str):
    """Prueba una variante de pronunciación."""
    uri = "ws://localhost:8765"
    
    print(f"\n{'─' * 80}")
    print(f"TEST: {description}")
    print(f"Enviando: '{variant}'")
    print('─' * 80)
    
    try:
        async with websockets.connect(uri) as websocket:
            # Enviar modo texto
            await websocket.send("modo texto")
            
            # Enviar la variante
            await websocket.send(variant)
            
            # Recibir respuestas
            audio_chunks = 0
            while True:
                message = await websocket.recv()
                
                if isinstance(message, str):
                    if message == "Inicio de Respuesta":
                        print("   📢 Respuesta iniciada")
                    elif message == "Fin de Respuesta":
                        print(f"   ✅ Completado ({audio_chunks} chunks de audio)")
                        break
                elif isinstance(message, bytes):
                    audio_chunks += 1
                    if audio_chunks == 1:
                        print("   🔊 Recibiendo audio...", end="", flush=True)
                    elif audio_chunks % 5 == 0:
                        print(".", end="", flush=True)
            
            print()
            
    except Exception as e:
        print(f"   ❌ Error: {e}\n")


async def main():
    """Ejecuta pruebas de variantes de pronunciación."""
    
    print("\n" + "=" * 80)
    print("PRUEBA DE VARIANTES DE PRONUNCIACIÓN")
    print("=" * 80)
    print("\nProbando diferentes formas de decir las mismas acciones...\n")
    
    # Variantes a probar
    tests = [
        # Variantes de "LED"
        ("Enciende el LED rojo", "LED en mayúsculas"),
        ("Enciende el let rojo", "let en lugar de LED"),
        ("ENCIENDE EL LED ROJO", "Todo en mayúsculas"),
        ("enciende el led rojo", "Todo en minúsculas"),
        
        # Variantes de acción
        ("Prende el led azul", "prende en lugar de enciende"),
        ("Activa el led verde", "activa en lugar de enciende"),
        
        # Puntuación al final
        ("Enciende el led rojo.", "Con punto al final"),
        ("Dime la hora.", "Hora con punto"),
        ("Apaga el led azul!", "Con signo de exclamación"),
        ("Enciende el led verde?", "Con signo de interrogación"),
        ("Dime la hora,", "Con coma"),
        
        # Hora
        ("Dime la hora", "Mayúsculas/minúsculas mezcladas"),
        ("dime la hora", "Todo en minúsculas"),
        ("DIME LA HORA", "Todo en mayúsculas"),
    ]
    
    for variant, description in tests:
        await test_variant(variant, description)
        await asyncio.sleep(0.5)  # Pausa entre pruebas
    
    print("\n" + "=" * 80)
    print("RESUMEN DE PRUEBAS")
    print("=" * 80)
    print("""
✅ Si todas las pruebas funcionaron correctamente, significa que:
   - Las variantes de pronunciación son reconocidas
   - La normalización a minúsculas funciona
   - El sistema es más robusto ante errores de transcripción

❌ Si alguna prueba falló:
   - Revisa los logs del servidor para ver el texto normalizado
   - Agrega más variantes al diccionario PRONUNCIATION_VARIANTS
   - Verifica que la acción normalizada esté en COMMON_ACTIONS
""")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Pruebas interrumpidas por el usuario\n")
