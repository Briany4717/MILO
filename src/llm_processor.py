from openai import OpenAI
import src.config as config
from src.logger import get_logger

logger = get_logger(__name__)

class LLMProcessor:
    def __init__(self, model_name):
        logger.info(f"Inicializando cliente LLM con modelo: {model_name}")
        self.client = OpenAI(
            base_url='http://localhost:11434/v1',
            api_key='ollama',
        )
        self.model = model_name
        self.history = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        logger.info("Cliente LLM inicializado correctamente")

    def get_response(self, user_text):
        logger.info(f"Procesando consulta con {self.model}")
        logger.debug(f"Consulta del usuario: '{user_text[:100]}...'")
        self.history.append({"role": "user", "content": user_text})
        
        response_stream = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            stream=True
        )
        
        return response_stream

    def add_assistant_response(self, response_text):
        self.history.append({"role": "assistant", "content": response_text})
        history_size = len(self.history)
        while len(self.history) > 10:
            self.history.pop(1)
        if history_size != len(self.history):
            logger.debug(f"Historial recortado de {history_size} a {len(self.history)} mensajes")

llm_processor = LLMProcessor(model_name=config.OLLAMA_MODEL)
