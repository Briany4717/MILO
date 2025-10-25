"""
Script de prueba para verificar la integración con ESP32.
Simula un ESP32 conectándose al servidor.
"""

import asyncio
import websockets
import json


async def test_esp32_connection():
    """Simula un ESP32 conectándose al servidor."""
    uri = "ws://localhost:8765"
    
    print("\n" + "=" * 80)
    print("TEST DE CONEXIÓN ESP32")
    print("=" * 80 + "\n")
    
    try:
        print(f"📡 Conectando al servidor: {uri}")
        async with websockets.connect(uri) as websocket:
            print("✅ Conexión establecida\n")
            
            # Paso 1: Identificarse como ESP32
            print("📤 Enviando identificación: 'esp32'")
            await websocket.send("esp32")
            
            # Paso 2: Esperar confirmación del servidor
            print("⏳ Esperando confirmación del servidor...")
            response = await websocket.recv()
            
            try:
                data = json.loads(response)
                print("✅ Respuesta recibida:")
                print(f"   {json.dumps(data, indent=2)}\n")
            except json.JSONDecodeError:
                print(f"❌ Respuesta no es JSON válido: {response}\n")
                return
            
            # Paso 3: Enviar heartbeat
            print("💓 Enviando heartbeat...")
            heartbeat = {
                "type": "heartbeat",
                "uptime": 12345,
                "free_heap": 98765
            }
            await websocket.send(json.dumps(heartbeat))
            print("✅ Heartbeat enviado\n")
            
            # Paso 4: Esperar comandos del servidor (o timeout)
            print("⏳ Esperando comandos del servidor (5 segundos)...")
            try:
                command = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                
                try:
                    cmd_data = json.loads(command)
                    print("📨 Comando recibido:")
                    print(f"   {json.dumps(cmd_data, indent=2)}\n")
                    
                    # Responder al comando
                    response = {
                        "type": "response",
                        "command": cmd_data.get("command"),
                        "success": True,
                        "message": "Comando ejecutado (simulado)"
                    }
                    await websocket.send(json.dumps(response))
                    print("✅ Respuesta enviada\n")
                    
                except json.JSONDecodeError:
                    print(f"❌ Comando no es JSON válido: {command}\n")
                    
            except asyncio.TimeoutError:
                print("⏱️  Timeout - No se recibieron comandos\n")
            
            # Paso 5: Probar envío de telemetría
            print("📊 Enviando telemetría...")
            telemetry = {
                "type": "telemetry",
                "data": {
                    "temperatura": 25.5,
                    "humedad": 60.0,
                    "presion": 1013.25
                }
            }
            await websocket.send(json.dumps(telemetry))
            print("✅ Telemetría enviada\n")
            
            # Paso 6: Probar envío de evento
            print("🔔 Enviando evento...")
            event = {
                "type": "event",
                "event": "boton_presionado",
                "data": {
                    "pin": 4
                }
            }
            await websocket.send(json.dumps(event))
            print("✅ Evento enviado\n")
            
            # Mantener conexión abierta un poco más
            print("⏳ Manteniendo conexión abierta (3 segundos)...")
            await asyncio.sleep(3)
            
            print("✅ Test completado exitosamente\n")
            
    except ConnectionRefusedError:
        print("❌ Error: No se pudo conectar al servidor")
        print(f"   Asegúrate de que el servidor esté ejecutándose en {uri}\n")
    except Exception as e:
        print(f"❌ Error inesperado: {e}\n")
    
    print("=" * 80)
    print("FIN DEL TEST")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    print("\n🧪 Test de Conexión ESP32")
    print("Este script simula un ESP32 conectándose al servidor.\n")
    print("Asegúrate de que el servidor MILO esté ejecutándose en localhost:8765\n")
    
    input("Presiona ENTER para comenzar el test...")
    
    asyncio.run(test_esp32_connection())
