import torch
from TTS.api import TTS
import os

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
EMBEDDING_FILE_PATH = "voice_embedding.pth"

print("---> Cargando modelo TTS para pre-calcular la voz...")
device = "cuda" if torch.cuda.is_available() else "cpu"

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True).to(device)

print(f"---> Calculando el embedding para la voz en '{SPEAKER_WAV_PATH}'...")

gpt_cond_latent, speaker_embedding = tts.synthesizer.tts_model.get_conditioning_latents(audio_path=SPEAKER_WAV_PATH)

torch.save({
    "gpt_cond_latent": gpt_cond_latent,
    "speaker_embedding": speaker_embedding
}, EMBEDDING_FILE_PATH)

print(f"---> ¡Éxito! La esencia de la voz ha sido guardada en '{EMBEDDING_FILE_PATH}'.")
