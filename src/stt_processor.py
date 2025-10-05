from faster_whisper import WhisperModel
import src.config as config

class STTProcessor:
    def __init__(self, model_size="base", device="cpu"):
        print(f"---> Cargando modelo Whisper ({model_size}) en {device}...")
        self.model = WhisperModel(model_size, device=device, compute_type="int8")
        print("---> Modelo Whisper cargado.")

    def transcribe(self, audio_file_path):
        print("---> Transcribiendo audio con whisper...")
        segments, info = self.model.transcribe(audio_file_path, beam_size=5, language="es")
        text = "".join(segment.text for segment in segments).strip()
        print(f"---> Usuario dijo: '{text}'")
        return text

stt_processor = STTProcessor(model_size=config.WHISPER_MODEL_SIZE)
