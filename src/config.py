import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# --- Configuración de Red ---
WEBSOCKET_HOST = os.getenv("WEBSOCKET_HOST", "0.0.0.0")
WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", 8765))

# --- Configuración ESP32 (Módulo Sensorial) ---
# El ESP32 se conecta AL servidor, no al revés
ESP32_ENABLED = os.getenv("ESP32_ENABLED", "true").lower() == "true"

# --- Configuración de Audio ---
WAVE_INPUT_FILENAME = "temp_input.wav"
WAVE_OUTPUT_FILENAME = "response.wav"
CHANNELS = 1
SAMPLE_WIDTH = 2
FRAME_RATE = 16000

# Modelos de Whisper: "tiny", "base", "small", "medium", "large"
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")

# --- Configuración de LLM (Proveedor de IA) ---
# Proveedor de LLM: "ollama" (local) o "gemini" (remoto)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

# Configuración de Ollama (Agente Local)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b-instruct-q4_K_M")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

# Configuración de Gemini (Agente Remoto)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Modelo de TTS y voz para clonar
# Backend TTS: "xtts", "piper", o "vits"
TTS_BACKEND = os.getenv("TTS_BACKEND", "xtts")
TTS_MODEL = os.getenv("TTS_MODEL", "tts_models/multilingual/multi-dataset/xtts_v2")

# Modo de XTTS: "clone" (clonación de voz) o "preset" (voces predefinidas - más rápido)
XTTS_MODE = os.getenv("XTTS_MODE", "preset")

# Configuración para modo clone (requiere voice_embedding.pth o speaker wav)
TTS_SPEAKER_WAV = os.getenv("TTS_SPEAKER_WAV", "samples/alejandro_sample_v2.wav")

# Configuración para modo preset (más rápido, sin clonación)
# Voces disponibles en XTTS v2:
# - Español Latino: Abrahan Mack, Dionisio Schuyler (masculinas)
# - Español Latino: Ana Florence, Alison Dietlinde (femeninas)
# - Español Peninsular: Claribel Dervla, Daisy Studious, Gracie Wise
# - Multilingües: Viktor Eka, Andrew Chipper, Badr Odhiambo
XTTS_PRESET_VOICE = os.getenv("XTTS_PRESET_VOICE", "Abrahan Mack")  # Voz masculina latino

# Configuración de emoción/estilo para XTTS
# Temperature: 0.1-1.5 (0.7 = neutral, >0.7 = más entusiasta/variada)
XTTS_TEMPERATURE = float(os.getenv("XTTS_TEMPERATURE", "0.85"))  # Ligeramente entusiasta
XTTS_SPEED = float(os.getenv("XTTS_SPEED", "1.5"))  # Velocidad de habla (0.5-2.0)

# Emotion: "Neutral", "Happy", "Sad", "Angry", "Dull", "Surprised"
XTTS_EMOTION = os.getenv("XTTS_EMOTION", "Happy")  # Emoción entusiasta

# Configuración específica de Piper
PIPER_MODEL_PATH = os.getenv("PIPER_MODEL_PATH", "models/piper/es_ES-sharvard-medium.onnx")
PIPER_CONFIG_PATH = os.getenv("PIPER_CONFIG_PATH", "models/piper/es_ES-sharvard-medium.onnx.json")
PIPER_SPEAKER_ID = int(os.getenv("PIPER_SPEAKER_ID", "0"))  # ID del hablante para modelos multi-speaker

# Configuración específica de VITS
# ⚠️  NOTA: VITS tiene LIMITACIONES importantes:
#     1. Solo español de España disponible (no latino/mexicano)
#     2. Control emocional muy limitado o inexistente en modelos disponibles
#     3. Para español latino con emociones, usa XTTS preset mode
# 
# VITS es útil principalmente para:
#     - Velocidad de generación (más rápido que XTTS)
#     - Menor uso de VRAM
#     - Español peninsular neutro
VITS_MODEL = os.getenv("VITS_MODEL", "tts_models/es/css10/vits")  # Español de España
VITS_EMOTION = os.getenv("VITS_EMOTION", "neutral")  # Limitado, la mayoría no funciona
VITS_SPEED = float(os.getenv("VITS_SPEED", "1.0"))  # Velocidad de habla

SYSTEM_PROMPT = """
Eres MILO, un asistente de IA inteligente y servicial.
Responde de forma concisa, clara y directa a las preguntas del usuario.
Mantén tus respuestas breves pero informativas.
"""
