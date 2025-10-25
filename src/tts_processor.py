import torch
import builtins
import os
import warnings
from TTS.api import TTS
import src.config as config
from scipy.io.wavfile import write as write_wav
import re
from src.logger import get_logger
import wave
import json

from TTS.tts.utils.text.punctuation import Punctuation
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs])

# Suprimir warnings de torch.load sobre weights_only
# Necesitamos weights_only=False para cargar objetos complejos de TTS
warnings.filterwarnings('ignore', category=FutureWarning, module='torch')
warnings.filterwarnings('ignore', category=FutureWarning, message='.*weights_only.*')

logger = get_logger(__name__)

# Auto-aceptar licencia TTS de Coqui (CPML) para uso en contenedor
def auto_accept_license(*args, **kwargs):
    """Auto-acepta la licencia CPML de Coqui TTS para uso no comercial"""
    return "y"  # Acepta automáticamente la licencia CPML

# Aplicar monkey patch para evitar prompt interactivo
original_input = builtins.input
builtins.input = auto_accept_license


class BaseTTSBackend:
    """Clase base abstracta para backends TTS"""
    
    def __init__(self):
        self.sample_rate = 22050  # Valor por defecto
        
    def generate_audio(self, text, output_path):
        """Genera audio a partir de texto y lo guarda en output_path"""
        raise NotImplementedError("Este método debe ser implementado por la subclase")
    
    def split_into_sentences(self, text):
        """Divide el texto en oraciones"""
        pattern = r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡])'
        sentences = re.split(pattern, text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        logger.debug(f"Texto dividido en {len(sentences)} frases")
        return sentences


class XTTSBackend(BaseTTSBackend):
    """Backend usando XTTS v2 de Coqui TTS con clonación de voz"""
    
    def __init__(self, model_name, device="cuda"):
        super().__init__()
        logger.info(f"Inicializando XTTS v2: {model_name}")
        effective_device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Dispositivo seleccionado: {effective_device}")
        
        self.tts = TTS(model_name, progress_bar=False).to(effective_device)
        self.punctuation = Punctuation("es")
        self.sample_rate = self.tts.synthesizer.output_sample_rate

        logger.info("Cargando embedding de voz pre-calculado")
        map_location = 'cuda' if torch.cuda.is_available() else 'cpu'

        if os.path.exists("data/voice_embedding.pth"):
            embedding_data = torch.load("data/voice_embedding.pth", map_location=map_location, weights_only=False)
            self.gpt_cond_latent = embedding_data["gpt_cond_latent"].to(effective_device)
            self.speaker_embedding = embedding_data["speaker_embedding"].to(effective_device)
            logger.info("Embedding de voz cargado correctamente")
        else:
            logger.error("voice_embedding.pth no encontrado en data/")
            raise FileNotFoundError("voice_embedding.pth no encontrado y la generación automática no está implementada. Por favor, crea el archivo manualmente o proporciona un archivo de audio de referencia para generarlo.")

    def generate_audio(self, text, output_path):
        logger.debug(f"Generando audio con XTTS: '{text[:50]}...'")
        out = self.tts.synthesizer.tts_model.inference(
            text,
            "es",
            self.gpt_cond_latent,
            self.speaker_embedding,
            temperature=0.7,
        )
        write_wav(output_path, self.sample_rate, out["wav"])
        logger.debug(f"Audio generado en: {output_path}")


class PiperBackend(BaseTTSBackend):
    """Backend usando Piper TTS (más rápido y ligero)"""
    
    def __init__(self, model_path, config_path=None, speaker_id=0):
        super().__init__()
        logger.info(f"Inicializando Piper TTS: {model_path}")
        
        try:
            from piper import PiperVoice
        except ImportError:
            import subprocess
            subprocess.run(["pip", "install", "piper-tts"])
            from piper import PiperVoice
        
        # Construir la ruta absoluta del modelo
        script_dir = os.path.dirname(__file__)
        project_root = os.path.abspath(os.path.join(script_dir, ".."))
        absolute_model_path = os.path.join(project_root, model_path)

        # Verificar que el modelo existe
        if not os.path.exists(absolute_model_path):
            raise FileNotFoundError(f"Modelo de Piper no encontrado: {absolute_model_path}")
        
        # Cargar configuración si existe
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
                logger.info(f"Configuración de Piper cargada: {config_path}")
        else:
            logger.warning(f"Configuración de Piper no encontrada: {config_path}")
            self.config = None
        
        # Inicializar Piper Voice
        self.voice = PiperVoice.load(absolute_model_path, config_path=config_path, use_cuda=torch.cuda.is_available())
        self.speaker_id = speaker_id
        
        # Obtener sample rate del modelo
        if hasattr(self.voice, 'config'):
            audio_config = getattr(self.voice.config, 'audio', {})
            self.sample_rate = getattr(audio_config, 'sample_rate', 22050)
        else:
            self.sample_rate = 22050
            
        logger.info(f"Piper TTS inicializado correctamente (sample_rate: {self.sample_rate})")

    def generate_audio(self, text, output_path):
        logger.debug(f"Generando audio con Piper: '{text[:50]}...'")
        
        try:
            # Generar audio con Piper
            # synthesize() devuelve un iterable de AudioChunk
            audio_bytes = bytes()
            
            # Recolectar todos los chunks de audio
            for audio_chunk in self.voice.synthesize(text):
                # audio_int16_bytes contiene los datos de audio en formato int16
                audio_bytes += audio_chunk.audio_int16_bytes
            
            # Guardar el audio en un archivo WAV
            with wave.open(output_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit (2 bytes por sample)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_bytes)
            
            logger.debug(f"Audio generado en: {output_path} ({len(audio_bytes)} bytes de audio)")
            
        except Exception as e:
            logger.error(f"Error al generar audio con Piper: {e}")
            raise


class TTSProcessor:
    """Procesador TTS unificado que soporta múltiples backends"""
    
    def __init__(self, backend_type=None, **kwargs):
        self.backend_type = backend_type or config.TTS_BACKEND
        logger.info(f"Inicializando TTSProcessor con backend: {self.backend_type}")
        
        if self.backend_type.lower() == "xtts":
            model_name = kwargs.get('model_name', config.TTS_MODEL)
            device = kwargs.get('device', 'cuda')
            self.backend = XTTSBackend(model_name=model_name, device=device)
            
        elif self.backend_type.lower() == "piper":
            model_path = kwargs.get('model_path', config.PIPER_MODEL_PATH)
            config_path = kwargs.get('config_path', config.PIPER_CONFIG_PATH)
            speaker_id = kwargs.get('speaker_id', config.PIPER_SPEAKER_ID)
            self.backend = PiperBackend(model_path=model_path, config_path=config_path, speaker_id=speaker_id)
            
        else:
            raise ValueError(f"Backend TTS no soportado: {self.backend_type}. Opciones: 'xtts', 'piper'")
        
        logger.info(f"Backend {self.backend_type} inicializado correctamente")

    def split_into_sentences(self, text):
        """Delega la división de oraciones al backend"""
        return self.backend.split_into_sentences(text)

    def generate_audio(self, text, output_path):
        """Delega la generación de audio al backend"""
        return self.backend.generate_audio(text, output_path)
    
    @property
    def sample_rate(self):
        """Obtiene el sample rate del backend actual"""
        return self.backend.sample_rate


# Inicializar el procesador TTS con el backend configurado
tts_processor = TTSProcessor()
