#!/usr/bin/env python3
"""
Script de prueba para verificar el procesamiento de acciones comunes.
"""
import asyncio
import websockets


async def test_common_action(action: str):
    """Prueba una acción común específica."""
    uri = "ws://localhost:8765"
    
    print(f"\n{'=' * 80}")
    print(f"PRUEBA: {action}")
    print('=' * 80)
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado al servidor")
            
            # Enviar modo texto
            print("📤 Enviando: 'modo texto'")
            await websocket.send("modo texto")
            
            # Enviar la acción
            print(f"📤 Enviando acción: '{action}'")
            await websocket.send(action)
            
            # Recibir respuestas
            print("📥 Esperando respuestas...")
            
            audio_chunks_received = 0
            while True:
                message = await websocket.recv()
                
                if isinstance(message, str):
                    if message == "Inicio de Respuesta":
                        print("   📢 Inicio de respuesta de audio")
                    elif message == "Fin de Respuesta":
                        print("   ✅ Fin de respuesta de audio")
                        print(f"   📊 Total de chunks de audio recibidos: {audio_chunks_received}")
                        break
                    else:
                        print(f"   📨 Mensaje: {message}")
                elif isinstance(message, bytes):
                    audio_chunks_received += 1
                    if audio_chunks_received == 1:
                        print(f"   🔊 Recibiendo chunks de audio...", end="", flush=True)
                    elif audio_chunks_received % 5 == 0:
                        print(".", end="", flush=True)
            
            print("\n✅ Test completado exitosamente\n")
            
    except Exception as e:
        print(f"❌ Error: {e}\n")


async def main():
    """Ejecuta múltiples pruebas de acciones comunes."""
    
    print("\n" + "=" * 80)
    print("PRUEBA DE ACCIONES COMUNES")
    print("=" * 80)
    print("\nAsegúrate de que el servidor MILO esté ejecutándose.\n")
    
    # Lista de acciones a probar
    acciones = [
        "Dime la hora",
        "Enciende el led rojo",
        "Apaga el led rojo",
    ]
    
    for accion in acciones:
        await test_common_action(accion)
        await asyncio.sleep(1)  # Pausa entre pruebas
    
    print("=" * 80)
    print("TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Pruebas interrumpidas por el usuario\n")
