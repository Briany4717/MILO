#!/usr/bin/env python3
"""
Test rápido de conexión ESP32
"""
import asyncio
import websockets
import json


async def main():
    uri = "ws://localhost:8765"
    print(f"🔌 Conectando a {uri}...")
    
    async with websockets.connect(uri) as ws:
        print("✅ Conectado")
        
        # Identificarse como ESP32
        print("📤 Enviando: 'esp32'")
        await ws.send("esp32")
        
        # Recibir confirmación
        msg = await ws.recv()
        print(f"📥 Respuesta: {msg}")
        
        # Enviar heartbeat
        print("💓 Enviando heartbeat...")
        await ws.send(json.dumps({"type": "heartbeat", "uptime": 100}))
        
        # Esperar un poco
        print("⏳ Esperando 5 segundos...")
        await asyncio.sleep(5)
        
        print("✅ Test completado - cerrando conexión")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Interrumpido por el usuario")
