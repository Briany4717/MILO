import asyncio
import websockets
import wave
import os
import json

import src.config as config
from src.stt_processor import stt_processor
from src.llm_processor import llm_processor
from src.tts_processor import tts_processor
from src.logger import get_logger

# Configurar logger para este módulo
logger = get_logger(__name__)

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

    sentences = tts_processor.split_into_sentences(mensaje_hablado)
    logger.info(f"Generando audio para {len(sentences)} frases")

    try:
        await websocket.send("Inicio de Respuesta")
        for sentence in sentences:
            if not sentence: continue
            
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

async def handle_audio_mode(websocket, audio_frames):
    with wave.open(config.WAVE_INPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(config.CHANNELS)
        wf.setsampwidth(config.SAMPLE_WIDTH)
        wf.setframerate(config.FRAME_RATE)
        wf.writeframes(b''.join(audio_frames))
    
    user_text = stt_processor.transcribe(config.WAVE_INPUT_FILENAME)
    logger.info(f"Audio transcrito: '{user_text}'")
    
    await process_llm_and_respond(websocket, user_text)
    
    os.remove(config.WAVE_INPUT_FILENAME)

async def handle_text_mode(websocket, text_message):
    logger.info(f"Texto recibido: '{text_message}'")

    await process_llm_and_respond(websocket, text_message)

async def handler(websocket):
    logger.info("Cliente conectado - Esperando modo de operación")
    
    first_message = await websocket.recv()
    
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
    async with websockets.serve(handler, config.WEBSOCKET_HOST, config.WEBSOCKET_PORT):
        logger.info(f"MILO Server iniciado en {config.WEBSOCKET_HOST}:{config.WEBSOCKET_PORT}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())