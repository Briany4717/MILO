from faster_whisper import WhisperModel
import src.config as config
from src.logger import get_logger

logger = get_logger(__name__)

class STTProcessor:
    """
    Procesador de Speech-to-Text usando Whisper optimizado para máxima precisión.
    Soporta detección automática de idioma (español/inglés) y parámetros optimizados.
    """
    
    def __init__(self, model_size=None, device=None, compute_type=None):
        model_size = model_size or config.WHISPER_MODEL_SIZE
        device = device or config.WHISPER_DEVICE
        compute_type = compute_type or config.WHISPER_COMPUTE_TYPE
        
        logger.info(f"🎙️  Inicializando Whisper STT")
        logger.info(f"📦 Modelo: {model_size}")
        logger.info(f"🖥️  Device: {device}")
        logger.info(f"⚙️  Compute type: {compute_type}")
        
        # Inicializar modelo con configuración optimizada
        self.model = WhisperModel(
            model_size, 
            device=device, 
            compute_type=compute_type,
            num_workers=config.WHISPER_NUM_WORKERS,
            download_root=None,  # Usa cache por defecto
        )
        
        self.model_size = model_size
        self.device = device
        
        logger.info("✅ Modelo Whisper cargado correctamente")
        logger.info(f"🎯 Configurado para máxima precisión: beam_size={config.WHISPER_BEAM_SIZE}, best_of={config.WHISPER_BEST_OF}")

    def transcribe(self, audio_file_path, language=None):
        """
        Transcribe audio con máxima precisión.
        
        Args:
            audio_file_path: Ruta al archivo de audio
            language: Idioma ('es', 'en', None para auto-detección)
        
        Returns:
            str: Texto transcrito
        """
        language = language or config.WHISPER_LANGUAGE
        
        if language:
            logger.info(f"🎙️  Transcribiendo audio (idioma: {language})...")
        else:
            logger.info(f"🎙️  Transcribiendo audio (detección automática de idioma)...")
        
        try:
            # Transcribir con parámetros optimizados para precisión
            segments, info = self.model.transcribe(
                audio_file_path,
                language=language,  # None = auto-detección
                beam_size=config.WHISPER_BEAM_SIZE,  # Búsqueda más exhaustiva
                best_of=config.WHISPER_BEST_OF,  # Múltiples candidatos
                temperature=config.WHISPER_TEMPERATURE,  # Determinístico para precisión
                condition_on_previous_text=True,  # Usar contexto previo
                vad_filter=config.WHISPER_VAD_FILTER,  # Filtrar silencios
                vad_parameters={
                    "threshold": 0.5,
                    "min_speech_duration_ms": 250,
                    "min_silence_duration_ms": 100,
                } if config.WHISPER_VAD_FILTER else None,
            )
            
            # Detectar idioma si es auto
            detected_language = info.language
            language_probability = info.language_probability
            
            if not language:
                logger.info(f"🌍 Idioma detectado: {detected_language} (confianza: {language_probability:.2%})")
            
            # Unir segmentos
            text = "".join(segment.text for segment in segments).strip()
            
            if text:
                logger.info(f"✅ Transcripción: '{text[:80]}{'...' if len(text) > 80 else ''}'")
            else:
                logger.warning("⚠️  No se detectó voz en el audio")
            
            return text
            
        except Exception as e:
            logger.error(f"❌ Error en transcripción: {e}")
            raise

stt_processor = STTProcessor()
