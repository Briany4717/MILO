# --- Librerías de red y asincronía ---
websockets
aiofiles

# --- Librerías de audio ---
pydub
# TTS (se instala abajo con sus dependencias)

# --- Librerías de IA ---
openai
openai-whisper
TTS
gTTS

# --- Frameworks base de IA ---
# NOTA: Se recomienda instalar PyTorch manualmente primero
# desde su página oficial para asegurar la versión con CUDA para tu GPU.
torch
torchaudio
torchvision

# --- Dependencia específica para compatibilidad ---
# Forzamos esta versión para evitar errores con la librería TTS.
transformers==4.36.2