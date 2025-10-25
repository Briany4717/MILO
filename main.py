import asyncio
import websockets
import wave
import os
import json
import signal
import sys

import src.config as config
from src.warnings_config import configure_warnings
from src.stt_processor import stt_processor
from src.llm_processor import llm_processor
from src.tts_processor import tts_processor
from src.esp32_manager import get_esp32_manager
from src.logger import get_logger
from src.common_actions import common_action_exists, get_common_action_response, execute_common_action

# Configurar supresión de warnings conocidos
configure_warnings()

# Configurar logger para este módulo
logger = get_logger(__name__)

# Obtener instancia global del gestor ESP32
esp32_manager = get_esp32_manager()

async def send_audio_response(websocket, response_text: str):
    """
    Convierte el texto a audio y lo envía al cliente.
    Esta función abstrae el proceso de TTS y envío de audio.
    
    Args:
        websocket: Conexión WebSocket del cliente
        response_text: Texto a convertir a audio y enviar
    """
    if not response_text.strip():
        logger.warning("El texto de respuesta está vacío - no se enviará audio")
        return
    
    sentences = tts_processor.split_into_sentences(response_text)
    logger.info(f"Generando audio para {len(sentences)} frases")
    
    try:
        await websocket.send("Inicio de Respuesta")
        
        for sentence in sentences:
            if not sentence:
                continue
            
            tts_processor.generate_audio(sentence, config.WAVE_OUTPUT_FILENAME)
            
            with open(config.WAVE_OUTPUT_FILENAME, "rb") as audio_file:
                await websocket.send(audio_file.read())
        
        await websocket.send("Fin de Respuesta")
        logger.info("Respuesta de audio enviada correctamente")
    
    except Exception as e:
        logger.error(f"Error durante generación/envío de audio: {e}")
    finally:
        if os.path.exists(config.WAVE_OUTPUT_FILENAME):
            os.remove(config.WAVE_OUTPUT_FILENAME)


async def process_user_request(websocket, user_text: str):
    """
    Procesa la solicitud del usuario.
    Verifica si es una acción común y la ejecuta directamente,
    o procesa con el LLM si no lo es.
    
    Args:
        websocket: Conexión WebSocket del cliente
        user_text: Texto de la solicitud del usuario
    """
    logger.info(f"Procesando solicitud: '{user_text}'")
    
    # Verificar si es una acción común
    if common_action_exists(user_text):
        logger.info(f"Acción común detectada: '{user_text}'")
        
        # Ejecutar la acción (si requiere hardware)
        await execute_common_action(user_text)
        
        # Obtener respuesta predefinida
        response_text = get_common_action_response(user_text)
        logger.info(f"Respuesta predefinida: '{response_text}'")
        
        # Enviar respuesta de audio
        await send_audio_response(websocket, response_text)
    else:
        # No es una acción común, procesar con el LLM
        logger.info("Procesando con LLM")
        await process_llm_and_respond(websocket, user_text)


async def process_llm_and_respond(websocket, user_text):
    await websocket.send("Inicio de Respuesta")
    logger.info("Asistente procesando consulta")
    response_stream = llm_processor.get_response(user_text)
    
    full_response_text = ""
    for chunk in response_stream:
        token = chunk.choices[0].delta.content
        if token:
            full_response_text += token

    llm_processor.add_assistant_response(full_response_text)
    
    # Mostrar la respuesta completa del LLM
    logger.info("=" * 80)
    logger.info("RESPUESTA DEL LLM:")
    logger.info("-" * 80)
    
    try:
        response_data = json.loads(full_response_text)
        mensaje_hablado = response_data.get("mensaje", "No recibí un mensaje para hablar.")
        objetos = response_data.get("objetos", [])
        
        # Mostrar el mensaje principal
        logger.info(f"Mensaje: {mensaje_hablado}")
        
        # Mostrar objetos si existen
        if objetos:
            logger.info("-" * 80)
            logger.info(f"Objetos adicionales ({len(objetos)}):")
            for idx, obj in enumerate(objetos, 1):
                tipo = obj.get('tipo', 'desconocido')
                contenido = obj.get('contenido', '')
                logger.info(f"  [{idx}] Tipo: {tipo}")
                logger.info(f"      Contenido: {contenido[:100]}{'...' if len(contenido) > 100 else ''}")
        
        logger.info("=" * 80)

    except json.JSONDecodeError as e:
        logger.error(f"Error: La respuesta del LLM no es un JSON válido: {e}")
        mensaje_hablado = "Ocurrió un error de formato en mi respuesta."

    if not mensaje_hablado.strip():
        logger.warning("El mensaje del LLM está vacío")
        return

    # Enviar respuesta de audio usando la función abstraída
    await send_audio_response(websocket, mensaje_hablado)

async def handle_audio_mode(websocket, audio_frames):
    """Procesa audio del usuario, lo transcribe y procesa la solicitud."""
    with wave.open(config.WAVE_INPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(config.CHANNELS)
        wf.setsampwidth(config.SAMPLE_WIDTH)
        wf.setframerate(config.FRAME_RATE)
        wf.writeframes(b''.join(audio_frames))
    
    user_text = stt_processor.transcribe(config.WAVE_INPUT_FILENAME)
    logger.info(f"Audio transcrito: '{user_text}'")
    
    # Procesar con la nueva función que verifica acciones comunes
    await process_user_request(websocket, user_text)
    
    os.remove(config.WAVE_INPUT_FILENAME)

async def handle_text_mode(websocket, text_message):
    """Procesa texto del usuario directamente."""
    logger.info(f"Texto recibido: '{text_message}'")
    
    # Procesar con la nueva función que verifica acciones comunes
    await process_user_request(websocket, text_message)

async def handler(websocket):
    """
    Maneja las conexiones WebSocket entrantes.
    Distingue entre conexiones de ESP32 y usuarios.
    """
    client_addr = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    logger.info(f"Cliente conectado desde {client_addr} - Esperando identificación")
    
    first_message = await websocket.recv()
    
    # Verificar si es el ESP32 identificándose
    if isinstance(first_message, str) and first_message.lower() == "esp32":
        logger.info(f"Conexión ESP32 identificada desde {client_addr}")
        
        # Enviar confirmación al ESP32
        await websocket.send(json.dumps({
            "type": "connection_ack",
            "status": "connected",
            "message": "ESP32 registrado correctamente"
        }))
        
        # Registrar el ESP32
        await esp32_manager.register_esp32(websocket)
        
        # Esperar a que el ESP32 se desconecte o la tarea termine
        # Esto mantiene el websocket abierto
        try:
            if esp32_manager._message_handler_task:
                await esp32_manager._message_handler_task
        except Exception as e:
            logger.debug(f"Tarea ESP32 finalizada: {e}")
        
        return
    
    # Si no es ESP32, es un usuario normal
    logger.info(f"Usuario conectado desde {client_addr}")
    
    if isinstance(first_message, str) and first_message.lower() == "modo texto":
        logger.info("Modo TEXTO activado")
        
        text_message = await websocket.recv()
        if isinstance(text_message, str):
            await handle_text_mode(websocket, text_message)
        else:
            logger.error("Error: Se esperaba un mensaje de texto")
            return
            
    elif isinstance(first_message, str) and first_message.lower() == "modo audio":
        logger.info("Modo AUDIO activado")
        
        audio_frames = []
        async for message in websocket:
            if isinstance(message, str) and message == "Fin de Audio":
                logger.info("Fin de audio recibido - Procesando")
                break
            audio_frames.append(message)

        if audio_frames:
            await handle_audio_mode(websocket, audio_frames)
        else:
            logger.warning("No se recibieron frames de audio")
            return
            
    else:
        logger.info("Modo AUDIO (retrocompatibilidad)")
        audio_frames = []
        
        if isinstance(first_message, bytes):
            audio_frames.append(first_message)
        
        async for message in websocket:
            if isinstance(message, str) and message == "Fin de Audio":
                logger.info("Fin de audio recibido - Procesando")
                break
            audio_frames.append(message)

        if audio_frames:
            await handle_audio_mode(websocket, audio_frames)
        else:
            logger.warning("No se recibieron frames de audio")
            return

async def main():
    """
    Función principal que inicia el servidor WebSocket.
    Maneja señales de interrupción para un cierre limpio.
    """
    # Obtener el loop de eventos actual
    loop = asyncio.get_running_loop()
    
    # Crear un evento para manejar el cierre limpio
    stop_event = asyncio.Event()
    
    def handle_shutdown(signum, frame):
        """Maneja las señales de interrupción (Ctrl+C, SIGTERM)"""
        logger.info("Señal de interrupción recibida - Cerrando servidor...")
        # Usar call_soon_threadsafe para establecer el evento de forma segura
        loop.call_soon_threadsafe(stop_event.set)
    
    # Registrar manejadores de señales
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    # Mostrar estado de ESP32
    if config.ESP32_ENABLED:
        logger.info("ESP32 habilitado - Esperando conexión del módulo sensorial")
    else:
        logger.info("ESP32 deshabilitado - Las acciones de hardware no estarán disponibles")

    try:
        # Iniciar el servidor
        async with websockets.serve(handler, config.WEBSOCKET_HOST, config.WEBSOCKET_PORT):
            logger.info("=" * 80)
            logger.info(f"MILO Server iniciado en {config.WEBSOCKET_HOST}:{config.WEBSOCKET_PORT}")
            logger.info(f"Esperando conexiones de usuarios y ESP32")
            logger.info("=" * 80)
            logger.info("Presiona Ctrl+C para detener el servidor")
            
            # Esperar hasta que se reciba una señal de interrupción
            await stop_event.wait()
    finally:
        # Limpiar conexión ESP32 si existe
        if esp32_manager.is_esp32_connected():
            logger.info("Cerrando conexión con ESP32...")
            await esp32_manager.disconnect_esp32()
    
    logger.info("Servidor detenido correctamente")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Este bloque captura el KeyboardInterrupt si ocurre antes de que asyncio.run termine
        logger.info("Interrupción detectada - Servidor detenido")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error crítico en el servidor: {e}")
        sys.exit(1)