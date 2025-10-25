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
# Backend TTS: "xtts" o "piper"
TTS_BACKEND = os.getenv("TTS_BACKEND", "xtts")
TTS_MODEL = os.getenv("TTS_MODEL", "tts_models/multilingual/multi-dataset/xtts_v2")
TTS_SPEAKER_WAV = os.getenv("TTS_SPEAKER_WAV", "samples/alejandro_sample_v2.wav")

# Configuración específica de Piper
PIPER_MODEL_PATH = os.getenv("PIPER_MODEL_PATH", "models/piper/es_ES-sharvard-medium.onnx")
PIPER_CONFIG_PATH = os.getenv("PIPER_CONFIG_PATH", "models/piper/es_ES-sharvard-medium.onnx.json")
PIPER_SPEAKER_ID = int(os.getenv("PIPER_SPEAKER_ID", "0"))  # ID del hablante para modelos multi-speaker

SYSTEM_PROMPT = """
Eres MILO, un asistente de IA inteligente y servicial.
Responde de forma concisa, clara y directa a las preguntas del usuario.
Mantén tus respuestas breves pero informativas.
"""
