import torch
from TTS.api import TTS
import os
import sys
import builtins
from logger import get_logger

logger = get_logger(__name__)

# Para evitar la pregunta interactiva de licencia en Docker
os.environ['COQUI_TOS_AGREED'] = '1'

from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
from TTS.tts.configs.shared_configs import BaseTrainingConfig, BaseAudioConfig

torch.serialization.add_safe_globals([
    XttsConfig, 
    XttsAudioConfig, 
    BaseDatasetConfig, 
    XttsArgs,
    BaseTrainingConfig,
    BaseAudioConfig
])

SPEAKER_WAV_PATH = "samples/alejandro_sample.wav"
EMBEDDING_FILE_PATH = "data/voice_embedding.pth"

logger.info("Inicializando modelo TTS para pre-calcular embedding de voz")
device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Dispositivo seleccionado: {device}")

# Bypass adicional para la licencia en entornos automatizados
try:
    # Método 1: Variable de entorno
    os.environ['COQUI_TOS_AGREED'] = '1'
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to(device)
except Exception as e:
    logger.warning(f"Error con variable de entorno: {e}")
    # Método 2: Monkey patch del input para aceptar automáticamente
    original_input = input
    def auto_yes(*args, **kwargs):
        logger.debug("Aceptando licencia automáticamente")
        return 'y'
    
    # Reemplazar temporalmente la función input
    import builtins
    builtins.input = auto_yes
    
    try:
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to(device)
    finally:
        # Restaurar input original
        builtins.input = original_input

logger.info(f"Calculando embedding de voz desde: {SPEAKER_WAV_PATH}")

gpt_cond_latent, speaker_embedding = tts.synthesizer.tts_model.get_conditioning_latents(audio_path=SPEAKER_WAV_PATH)

# Asegurar que el directorio data/ existe
os.makedirs(os.path.dirname(EMBEDDING_FILE_PATH), exist_ok=True)

torch.save({
    "gpt_cond_latent": gpt_cond_latent,
    "speaker_embedding": speaker_embedding
}, EMBEDDING_FILE_PATH)

logger.info(f"Embedding de voz guardado exitosamente en: {EMBEDDING_FILE_PATH}")
