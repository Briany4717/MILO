import torch
from TTS.api import TTS
import src.config as config
from scipy.io.wavfile import write as write_wav
import re

from TTS.tts.utils.text.punctuation import Punctuation
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs])

class TTSProcessor:
    def __init__(self, model_name, device="cuda"):
        print(f"---> Cargando modelo TTS ({model_name})...")
        effective_device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = TTS(model_name, progress_bar=True).to(effective_device)
        
        self.punctuation = Punctuation("es")

        print("---> Cargando embedding de voz pre-calculado...")
        embedding_data = torch.load("voice_embedding.pth")
        self.gpt_cond_latent = embedding_data["gpt_cond_latent"].to(effective_device)
        self.speaker_embedding = embedding_data["speaker_embedding"].to(effective_device)
        print("---> Embedding de voz cargado y listo.")

    def split_into_sentences(self, text):
        pattern = r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡])'
        
        sentences = re.split(pattern, text.strip())
        
        sentences = [s.strip() for s in sentences if s.strip()]
        print(f"---> Texto dividido en frases: {sentences}")
        
        return sentences

    def generate_audio(self, text, output_path):
        print(f"---> Generando audio para la frase: '{text}'")
        out = self.tts.synthesizer.tts_model.inference(
            text,
            "es",
            self.gpt_cond_latent,
            self.speaker_embedding,
            temperature=0.7,
        )

        sample_rate = self.tts.synthesizer.output_sample_rate
        write_wav(output_path, sample_rate, out["wav"])

tts_processor = TTSProcessor(model_name=config.TTS_MODEL)