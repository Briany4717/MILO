import torch
import builtins
import os
from TTS.api import TTS
import src.config as config
from scipy.io.wavfile import write as write_wav
import re
from src.logger import get_logger

from TTS.tts.utils.text.punctuation import Punctuation
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs])

logger = get_logger(__name__)

# Auto-aceptar licencia TTS de Coqui (CPML) para uso en contenedor
def auto_accept_license(*args, **kwargs):
    """Auto-acepta la licencia CPML de Coqui TTS para uso no comercial"""
    return "y"  # Acepta automáticamente la licencia CPML

# Aplicar monkey patch para evitar prompt interactivo
original_input = builtins.input
builtins.input = auto_accept_license

class TTSProcessor:
    def __init__(self, model_name, device="cuda"):
        logger.info(f"Inicializando modelo TTS: {model_name}")
        effective_device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Dispositivo seleccionado: {effective_device}")
        self.tts = TTS(model_name, progress_bar=False).to(effective_device)
        
        self.punctuation = Punctuation("es")

        logger.info("Cargando embedding de voz pre-calculado")
        # Cargar el embedding mapeándolo a la CPU para compatibilidad
        map_location = 'cuda' if torch.cuda.is_available() else 'cpu'

        if os.path.exists("data/voice_embedding.pth"):
            embedding_data = torch.load("data/voice_embedding.pth", map_location=map_location)
            self.gpt_cond_latent = embedding_data["gpt_cond_latent"].to(effective_device)
            self.speaker_embedding = embedding_data["speaker_embedding"].to(effective_device)
            logger.info("Embedding de voz cargado correctamente")
        else:
            logger.error("voice_embedding.pth no encontrado en data/")
            # Aquí se asume que se puede generar un embedding de voz. Necesitarás reemplazar
            # 'ruta/a/tu/audio_de_referencia.wav' con un archivo de audio real.
            # Este es un placeholder y DEBE ser ajustado por el usuario.
            # tts.tts_model.get_conditioning_latents_from_filepath requiere un archivo de audio.
            # Por ejemplo, puedes usar un archivo de audio de referencia para generar el embedding.
            # self.gpt_cond_latent, self.speaker_embedding = self.tts.synthesizer.tts_model.get_conditioning_latents_from_filepath(
            #     audio_filepath="ruta/a/tu/audio_de_referencia.wav"
            # )
            # torch.save({"gpt_cond_latent": self.gpt_cond_latent, "speaker_embedding": self.speaker_embedding}, "voice_embedding.pth")
            # logger.info("Nuevo voice_embedding.pth generado y guardado")
            raise FileNotFoundError("voice_embedding.pth no encontrado y la generación automática no está implementada. Por favor, crea el archivo manualmente o proporciona un archivo de audio de referencia para generarlo.")

    def split_into_sentences(self, text):
        pattern = r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡])'
        
        sentences = re.split(pattern, text.strip())
        
        sentences = [s.strip() for s in sentences if s.strip()]
        logger.debug(f"Texto dividido en {len(sentences)} frases")
        
        return sentences

    def generate_audio(self, text, output_path):
        logger.debug(f"Generando audio: '{text[:50]}...'")
        out = self.tts.synthesizer.tts_model.inference(
            text,
            "es",
            self.gpt_cond_latent,
            self.speaker_embedding,
            temperature=0.7,
        )

        sample_rate = self.tts.synthesizer.output_sample_rate
        write_wav(output_path, sample_rate, out["wav"])
        logger.debug(f"Audio generado en: {output_path}")

tts_processor = TTSProcessor(model_name=config.TTS_MODEL)
