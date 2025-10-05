import asyncio
import websockets
import wave
import os
import json

import src.config as config
from src.stt_processor import stt_processor
from src.llm_processor import llm_processor
from src.tts_processor import tts_processor

async def process_llm_and_respond(websocket, user_text):
    await websocket.send("Inicio de Respuesta")
    print("---> Asistente pensando...")
    response_stream = llm_processor.get_response(user_text)
    
    full_response_text = ""
    for chunk in response_stream:
        token = chunk.choices[0].delta.content
        if token:
            full_response_text += token

    llm_processor.add_assistant_response(full_response_text)
    print(f"---> Asistente responde (JSON crudo): '{full_response_text}'")

    try:
        response_data = json.loads(full_response_text)
        mensaje_hablado = response_data.get("mensaje", "No recibí un mensaje para hablar.")
        objetos = response_data.get("objetos", [])

        if objetos:
            for obj in objetos:
                print(f"💡 Objeto recibido - Tipo: {obj.get('tipo')}, Contenido: {obj.get('contenido')}")

    except json.JSONDecodeError as e:
        print(f"<---> Error: La respuesta del LLM no era un JSON válido: {e}")
        mensaje_hablado = "Ocurrió un error de formato en mi respuesta."

    if not mensaje_hablado.strip():
        print("<---> El mensaje del LLM estaba vacío.")
        return

    sentences = tts_processor.split_into_sentences(mensaje_hablado)
    print(f"--->  Frases a hablar: {sentences}")

    try:
        await websocket.send("Inicio de Respuesta")
        for sentence in sentences:
            if not sentence: continue
            
            tts_processor.generate_audio(sentence, config.WAVE_OUTPUT_FILENAME)
            
            with open(config.WAVE_OUTPUT_FILENAME, "rb") as audio_file:
                await websocket.send(audio_file.read())
        
        await websocket.send("Fin de Respuesta")
        print("--- Respuesta de audio completa enviada ---")

    except Exception as e:
        print(f"<---> Error durante la generación o envío de audio: {e}")
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
    print(f"-> Audio transcrito: {user_text}")
    
    await process_llm_and_respond(websocket, user_text)
    
    os.remove(config.WAVE_INPUT_FILENAME)

async def handle_text_mode(websocket, text_message):
    print(f"-> Texto recibido: {text_message}")

    await process_llm_and_respond(websocket, text_message)

async def handler(websocket):
    print(f"Cliente conectado. Esperando modo de operación...")
    
    first_message = await websocket.recv()
    
    if isinstance(first_message, str) and first_message.lower() == "modo texto":
        print("--- Modo TEXTO activado ---")
        
        text_message = await websocket.recv()
        if isinstance(text_message, str):
            await handle_text_mode(websocket, text_message)
        else:
            print("<---> Error: Se esperaba un mensaje de texto")
            return
            
    elif isinstance(first_message, str) and first_message.lower() == "modo audio":
        print("--- Modo AUDIO activado ---")
        
        audio_frames = []
        async for message in websocket:
            if isinstance(message, str) and message == "Fin de Audio":
                print("--- Recibido 'Fin de Audio'---> Procesando...")
                break
            audio_frames.append(message)

        if audio_frames:
            await handle_audio_mode(websocket, audio_frames)
        else:
            print("-> No se recibieron frames de audio")
            return
            
    else:
        print("--- Modo AUDIO (retrocompatibilidad) ---")
        audio_frames = []
        
        if isinstance(first_message, bytes):
            audio_frames.append(first_message)
        
        async for message in websocket:
            if isinstance(message, str) and message == "Fin de Audio":
                print("--- Recibido 'Fin de Audio' ---> Procesando...")
                break
            audio_frames.append(message)

        if audio_frames:
            await handle_audio_mode(websocket, audio_frames)
        else:
            print("-> No se recibieron frames de audio")
            return

async def main():
    async with websockets.serve(handler, config.WEBSOCKET_HOST, config.WEBSOCKET_PORT):
        print(f"--> Asistente Virtual Modular listo en {config.WEBSOCKET_HOST}:{config.WEBSOCKET_PORT}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())