from faster_whisper import WhisperModel
import src.config as config
from src.logger import get_logger

logger = get_logger(__name__)

class STTProcessor:
    def __init__(self, model_size="base", device="cpu"):
        logger.info(f"Inicializando modelo Whisper: {model_size} en {device}")
        self.model = WhisperModel(model_size, device=device, compute_type="int8")
        logger.info("Modelo Whisper cargado correctamente")

    def transcribe(self, audio_file_path):
        logger.info("Iniciando transcripción de audio")
        segments, info = self.model.transcribe(audio_file_path, beam_size=5, language="es")
        text = "".join(segment.text for segment in segments).strip()
        logger.info(f"Transcripción completada: '{text[:100]}{'...' if len(text) > 100 else ''}'")
        return text

stt_processor = STTProcessor(model_size=config.WHISPER_MODEL_SIZE)
