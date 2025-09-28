import asyncio
import websockets
import wave
import os
import io

# --- LIBRERÍAS DE IA LOCAL ---
import torch
import whisper
from openai import OpenAI
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig # <-- 1. AÑADE ESTA LÍNEA DE IMPORTACIÓN
from TTS.tts.models.xtts import XttsAudioConfig
from TTS.config.shared_configs import BaseDatasetConfig # <-- La nueva clase
from TTS.tts.models.xtts import XttsArgs
# --------------------------------

# --- LA SOLUCIÓN: AÑADIR EL PERMISO PARA PYTORCH ---
# 2. Añadimos la clase de configuración de XTTS a la lista segura de PyTorch
torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs])
torch.serialization.safe_globals([XttsAudioConfig])
# ---------------------------------------------------

# --- Carga de modelos ---
# Detecta si tienes una GPU con CUDA para acelerar el proceso
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Usando dispositivo para TTS: {device}")

print("Cargando modelo de Whisper local...")
whisper_model = whisper.load_model("base")
print("✅ Modelo de Whisper cargado.")

# Carga el modelo XTTS v2 en la memoria (se descarga automáticamente la primera vez)
print("Cargando modelo de TTS local (XTTS)...")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True).to(device)
print("✅ Modelo de TTS cargado.")
# ---------------------------------------------------

# --- Cliente de Ollama (sin cambios) ---
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama',
)
# ------------------------------------

# --- Configuración y Memoria (sin cambios) ---
WAVE_INPUT_FILENAME = "temp_input.wav"
CHANNELS = 1
SAMPLE_WIDTH = 2
FRAME_RATE = 16000
system_prompt = { "role": "system", "content": "Eres MILO, un asistente virtual servicial y amigable..." }
conversation_history = [system_prompt]
# ------------------------------------

async def handler(websocket):
    global conversation_history
    print(f"✅ Cliente conectado. Escuchando...")
    audio_frames = []
    # ... (El código para recibir audio y transcribirlo con Whisper es el mismo) ...
        
    # ... (El código para llamar a Llama 3 con Ollama es el mismo) ...
    # Supongamos que ya tenemos la 'response_text' de Llama 3
    
    # [AQUÍ PEGARÍAS LA LÓGICA DE WEBSOCKETS, WHISPER Y OLLAMA DEL SCRIPT ANTERIOR]
    # Por simplicidad, simularemos que ya tenemos una respuesta de Llama 3:
    try: # Este try/except es solo para el ejemplo
        async for message in websocket:
            audio_frames.append(message)
        with wave.open(WAVE_INPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(SAMPLE_WIDTH)
            wf.setframerate(FRAME_RATE)
            wf.writeframes(b''.join(audio_frames))
        # --- 3. Transcribe el audio con el modelo LOCAL de Whisper ---
        result = whisper_model.transcribe(WAVE_INPUT_FILENAME, language="es", fp16=False)
        user_text = result["text"]
         # ---------------------------------------------------------
            
        print(f"🧠 Usuario dijo (local): '{user_text}'")
        conversation_history.append({"role": "user", "content": user_text})

        # --- 4. Llama al modelo LOCAL (Llama 3) a través de Ollama ---
        response = client.chat.completions.create(
            model="llama3", # Usamos el nombre del modelo de Ollama
            messages=conversation_history,
            temperature=0.7
        )
        response_text = response.choices[0].message.content
        print(f"🤖 Asistente responde (local): '{response_text}'")

        # --- SECCIÓN DE TTS ACTUALIZADA ---
        print("Generando audio con XTTS...")
        # Convierte el texto a voz localmente, clonando la voz del archivo .wav
        # ¡Asegúrate de que el archivo 'mi_voz.wav' exista en tu carpeta!
        tts.tts_to_file(
            text=response_text,
            file_path="response.wav",     # Guarda como .wav, que es de mejor calidad
            speaker_wav="mi_voz.wav",     # ¡La magia de la clonación!
            language="es"
        )
        print("✅ Audio de respuesta guardado como response.wav")
        # --------------------------------
        try:
            with open("response.wav", "rb") as audio_file:
                audio_bytes = audio_file.read()
                await websocket.send(audio_bytes)
                print(f"⬅️ Enviando {len(audio_bytes)} bytes de audio de respuesta al ESP32.")
        except Exception as e:
            print(f"🚨 Error al enviar el audio de respuesta: {e}")

    except Exception as e:
        print(f"🚨 Error: {e}")


# --- CÓDIGO DEL SERVIDOR (simplificado para mostrar solo la parte de TTS) ---
# En tu archivo real, mantén el código completo del websocket handler
async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("🚀 Asistente Virtual 100% LOCAL listo en el puerto 8765.")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())