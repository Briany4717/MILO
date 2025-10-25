import torch
import builtins
import os
import warnings
import numpy as np
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
    """Backend usando XTTS v2 de Coqui TTS (con o sin clonación de voz)"""
    
    def __init__(self, model_name, device="cuda", mode="preset", preset_voice=None, speaker_wav=None, 
                 temperature=0.85, speed=1.5, emotion="Happy"):
        super().__init__()
        logger.info(f"Inicializando XTTS v2: {model_name} (modo: {mode})")
        effective_device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Dispositivo seleccionado: {effective_device}")
        
        self.mode = mode
        self.tts = TTS(model_name, progress_bar=False).to(effective_device)
        self.punctuation = Punctuation("es")
        self.sample_rate = self.tts.synthesizer.output_sample_rate
        self.device = effective_device
        self.temperature = temperature
        self.speed = speed
        self.emotion = emotion
        
        if mode == "clone":
            # Modo clonación: usar embedding pre-calculado o speaker_wav
            logger.info("Modo CLONACIÓN activado - cargando embedding de voz")
            map_location = 'cuda' if torch.cuda.is_available() else 'cpu'

            if os.path.exists("data/voice_embedding.pth"):
                embedding_data = torch.load("data/voice_embedding.pth", map_location=map_location, weights_only=False)
                self.gpt_cond_latent = embedding_data["gpt_cond_latent"].to(effective_device)
                self.speaker_embedding = embedding_data["speaker_embedding"].to(effective_device)
                logger.info("Embedding de voz cargado correctamente")
            elif speaker_wav and os.path.exists(speaker_wav):
                logger.info(f"Generando embedding desde: {speaker_wav}")
                # Generar embedding sobre la marcha (más lento en primera ejecución)
                self.gpt_cond_latent, self.speaker_embedding = self.tts.synthesizer.tts_model.get_conditioning_latents(
                    audio_path=speaker_wav,
                    gpt_cond_len=30,
                    gpt_cond_chunk_len=4,
                    max_ref_length=60
                )
                logger.info("Embedding generado correctamente")
            else:
                logger.error("No se encontró voice_embedding.pth ni speaker_wav para modo clone")
                raise FileNotFoundError(
                    "Modo 'clone' requiere voice_embedding.pth en data/ o un archivo speaker_wav válido"
                )
        
        elif mode == "preset":
            # Modo preset: usar voces predefinidas (mucho más rápido)
            self.preset_voice = preset_voice or config.XTTS_PRESET_VOICE
            logger.info(f"Modo PRESET activado - usando voz predefinida: {self.preset_voice}")
            logger.info(f"⚡ Este modo es significativamente más rápido que la clonación")
            logger.info(f"🎭 Emoción: {self.emotion} | Temperature: {self.temperature} | Speed: {self.speed}")
            # No necesitamos cargar embeddings en modo preset
            self.gpt_cond_latent = None
            self.speaker_embedding = None
        
        else:
            raise ValueError(f"Modo XTTS no válido: {mode}. Opciones: 'clone', 'preset'")

    def generate_audio(self, text, output_path):
        logger.debug(f"Generando audio con XTTS ({self.mode}): '{text[:50]}...'")
        
        if self.mode == "clone":
            # Dividir en frases para mejor naturalidad
            sentences = self.split_into_sentences(text)
            logger.info(f"Texto dividido en {len(sentences)} frase(s)")
            
            audio_chunks = []
            for i, sentence in enumerate(sentences, 1):
                logger.debug(f"Generando frase {i}/{len(sentences)}: '{sentence[:30]}...'")
                
                # Usar clonación con embeddings pre-calculados
                out = self.tts.synthesizer.tts_model.inference(
                    sentence,
                    "es",
                    self.gpt_cond_latent,
                    self.speaker_embedding,
                    temperature=self.temperature,
                    speed=self.speed,
                )
                audio_chunks.append(torch.tensor(out["wav"]))
            
            # Concatenar todas las frases
            audio_data = torch.cat(audio_chunks, dim=0).cpu().numpy()
            logger.debug(f"Audio completo generado ({len(sentences)} frases)")
            
        elif self.mode == "preset":
            # Usar voz predefinida (API simplificada y más rápida)
            # split_sentences=True mejora la naturalidad al procesar cada frase
            out = self.tts.tts(
                text=text,
                language="es",
                speaker=self.preset_voice,
                split_sentences=True,  # Mejora naturalidad
                emotion=self.emotion,  # Emoción: Happy, Sad, Angry, Neutral, etc.
            )
            
            # tts.tts() puede devolver lista o numpy array, normalizar
            if isinstance(out, list):
                # Si es lista, convertir a numpy array
                audio_data = np.array(out, dtype=np.float32)
            else:
                audio_data = out
        
        # Guardar el audio
        write_wav(output_path, self.sample_rate, audio_data)
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


class VITSBackend(BaseTTSBackend):
    """Backend usando VITS (más rápido y mejor control emocional que XTTS)"""
    
    def __init__(self, model_name=None, emotion="neutral", speed=1.0):
        super().__init__()
        model_name = model_name or config.VITS_MODEL
        logger.info(f"Inicializando VITS: {model_name}")
        
        effective_device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Dispositivo seleccionado: {effective_device}")
        
        try:
            self.tts = TTS(model_name, progress_bar=False).to(effective_device)
            self.sample_rate = self.tts.synthesizer.output_sample_rate
            self.emotion = emotion
            self.speed = speed
            self.device = effective_device
            
            logger.info(f"VITS inicializado correctamente")
            logger.info(f"🎭 Emoción: {self.emotion} | Speed: {self.speed}")
            
        except Exception as e:
            logger.error(f"Error al inicializar VITS: {e}")
            # Fallback a modelo por defecto si falla
            logger.warning("Intentando con modelo VITS por defecto...")
            self.tts = TTS("tts_models/es/css10/vits", progress_bar=False).to(effective_device)
            self.sample_rate = self.tts.synthesizer.output_sample_rate
            self.emotion = emotion
            self.speed = speed
            self.device = effective_device
            logger.info("VITS inicializado con modelo por defecto")

    def generate_audio(self, text, output_path):
        logger.debug(f"Generando audio con VITS: '{text[:50]}...'")
        
        try:
            # VITS soporta generación directa con control de velocidad
            # Algunos modelos VITS soportan emotion, otros no
            wav = self.tts.tts(text=text, emotion=self.emotion if self._supports_emotion() else None)
            
            # Normalizar salida (puede ser lista o array)
            if isinstance(wav, list):
                wav = np.array(wav, dtype=np.float32)
            
            # Aplicar ajuste de velocidad si es necesario
            if self.speed != 1.0:
                wav = self._adjust_speed(wav, self.speed)
            
            # 🔪 RECORTAR SILENCIOS al inicio y final (soluciona pausas largas)
            wav = self._trim_silence(wav)
            
            # Guardar audio
            write_wav(output_path, self.sample_rate, wav)
            logger.debug(f"Audio generado en: {output_path}")
            
        except Exception as e:
            logger.error(f"Error al generar audio con VITS: {e}")
            # Intentar sin emoción si falla
            try:
                logger.warning("Reintentando sin parámetro de emoción...")
                wav = self.tts.tts(text=text)
                
                if isinstance(wav, list):
                    wav = np.array(wav, dtype=np.float32)
                
                # También recortar silencios en fallback
                wav = self._trim_silence(wav)
                
                write_wav(output_path, self.sample_rate, wav)
                logger.debug(f"Audio generado en: {output_path} (sin emoción)")
            except Exception as e2:
                logger.error(f"Error crítico en VITS: {e2}")
                raise
    
    def _supports_emotion(self):
        """Verifica si el modelo VITS actual soporta control de emoción"""
        # Los modelos VITS con emotion suelen tenerlo en el nombre o config
        model_name = str(self.tts.model_name).lower()
        return "emotion" in model_name or "expressive" in model_name
    
    def _adjust_speed(self, audio, speed_factor):
        """Ajusta la velocidad del audio usando resampling simple"""
        try:
            from scipy import signal
            # Resamplear para cambiar velocidad
            num_samples = int(len(audio) / speed_factor)
            audio_adjusted = signal.resample(audio, num_samples)
            return audio_adjusted.astype(np.float32)
        except Exception as e:
            logger.warning(f"No se pudo ajustar velocidad: {e}, usando audio original")
            return audio
    
    def _trim_silence(self, audio, threshold=0.01, frame_length=2048):
        """
        Recorta silencios del inicio y final del audio.
        
        Args:
            audio: Array de audio
            threshold: Umbral de energía para considerar silencio (0.01 = 1%)
            frame_length: Tamaño de ventana para análisis
        
        Returns:
            Audio recortado sin silencios largos
        """
        try:
            # Calcular energía RMS por frame
            def get_rms_energy(frame):
                return np.sqrt(np.mean(frame ** 2))
            
            # Encontrar inicio del audio (primer frame con energía)
            start_idx = 0
            for i in range(0, len(audio) - frame_length, frame_length):
                frame = audio[i:i + frame_length]
                if get_rms_energy(frame) > threshold:
                    start_idx = max(0, i - frame_length)  # Dejar un poco de margen
                    break
            
            # Encontrar final del audio (último frame con energía)
            end_idx = len(audio)
            for i in range(len(audio) - frame_length, 0, -frame_length):
                frame = audio[i:i + frame_length]
                if get_rms_energy(frame) > threshold:
                    end_idx = min(len(audio), i + frame_length * 2)  # Dejar un poco de margen
                    break
            
            # Recortar
            trimmed = audio[start_idx:end_idx]
            
            # Log si se recortó mucho
            removed_ms = (len(audio) - len(trimmed)) / self.sample_rate * 1000
            if removed_ms > 100:  # Si se quitaron más de 100ms
                logger.debug(f"🔪 Recortados {removed_ms:.0f}ms de silencio")
            
            return trimmed
            
        except Exception as e:
            logger.warning(f"No se pudo recortar silencio: {e}, usando audio original")
            return audio


class TTSProcessor:
    """Procesador TTS unificado que soporta múltiples backends"""
    
    def __init__(self, backend_type=None, **kwargs):
        self.backend_type = backend_type or config.TTS_BACKEND
        logger.info(f"Inicializando TTSProcessor con backend: {self.backend_type}")
        
        if self.backend_type.lower() == "xtts":
            model_name = kwargs.get('model_name', config.TTS_MODEL)
            device = kwargs.get('device', 'cuda')
            mode = kwargs.get('mode', config.XTTS_MODE)
            preset_voice = kwargs.get('preset_voice', config.XTTS_PRESET_VOICE)
            speaker_wav = kwargs.get('speaker_wav', config.TTS_SPEAKER_WAV)
            temperature = kwargs.get('temperature', config.XTTS_TEMPERATURE)
            speed = kwargs.get('speed', config.XTTS_SPEED)
            emotion = kwargs.get('emotion', config.XTTS_EMOTION)
            
            self.backend = XTTSBackend(
                model_name=model_name, 
                device=device,
                mode=mode,
                preset_voice=preset_voice,
                speaker_wav=speaker_wav,
                temperature=temperature,
                speed=speed,
                emotion=emotion
            )
            
        elif self.backend_type.lower() == "piper":
            model_path = kwargs.get('model_path', config.PIPER_MODEL_PATH)
            config_path = kwargs.get('config_path', config.PIPER_CONFIG_PATH)
            speaker_id = kwargs.get('speaker_id', config.PIPER_SPEAKER_ID)
            self.backend = PiperBackend(model_path=model_path, config_path=config_path, speaker_id=speaker_id)
        
        elif self.backend_type.lower() == "vits":
            model_name = kwargs.get('model_name', config.VITS_MODEL)
            emotion = kwargs.get('emotion', config.VITS_EMOTION)
            speed = kwargs.get('speed', config.VITS_SPEED)
            self.backend = VITSBackend(model_name=model_name, emotion=emotion, speed=speed)
            
        else:
            raise ValueError(f"Backend TTS no soportado: {self.backend_type}. Opciones: 'xtts', 'piper', 'vits'")
        
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
