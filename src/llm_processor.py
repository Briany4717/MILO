from openai import OpenAI
import google.generativeai as genai
import src.config as config
from src.logger import get_logger

logger = get_logger(__name__)

class LLMProcessor:
    def __init__(self, provider=None, model_name=None):
        """
        Inicializa el procesador LLM con el proveedor especificado.
        
        Args:
            provider: "ollama" o "gemini". Si es None, usa config.LLM_PROVIDER
            model_name: Nombre del modelo. Si es None, usa el modelo por defecto del proveedor
        """
        self.provider = provider or config.LLM_PROVIDER
        
        logger.info(f"Inicializando LLM con proveedor: {self.provider}")
        
        if self.provider == "ollama":
            self.model = model_name or config.OLLAMA_MODEL
            logger.info(f"Configurando Ollama con modelo: {self.model}")
            self.client = OpenAI(
                base_url=config.OLLAMA_BASE_URL,
                api_key='ollama',
            )
            
        elif self.provider == "gemini":
            self.model = model_name or config.GEMINI_MODEL
            logger.info(f"Configurando Gemini con modelo: {self.model}")
            
            if not config.GEMINI_API_KEY:
                raise ValueError(
                    "GEMINI_API_KEY no está configurada. "
                    "Por favor, añade tu API key en el archivo .env: GEMINI_API_KEY=tu_api_key_aqui"
                )
            
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.client = genai.GenerativeModel(self.model)
            self.chat_session = self.client.start_chat(history=[])
            
        else:
            raise ValueError(f"Proveedor LLM no soportado: {self.provider}. Use 'ollama' o 'gemini'")
        
        self.history = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        logger.info(f"Cliente LLM inicializado correctamente con {self.provider}")

    def get_response(self, user_text):
        """
        Obtiene una respuesta del LLM según el proveedor configurado.
        
        Args:
            user_text: Texto de la consulta del usuario
            
        Returns:
            Stream de respuesta del LLM
        """
        logger.info(f"Procesando consulta con {self.provider} - {self.model}")
        logger.debug(f"Consulta del usuario: '{user_text[:100]}...'")
        self.history.append({"role": "user", "content": user_text})
        
        if self.provider == "ollama":
            return self._get_ollama_response()
        elif self.provider == "gemini":
            return self._get_gemini_response(user_text)
    
    def _get_ollama_response(self):
        """Obtiene respuesta de Ollama usando la API de OpenAI."""
        response_stream = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            stream=True
        )
        return response_stream
    
    def _get_gemini_response(self, user_text):
        """Obtiene respuesta de Gemini usando la API de Google."""
        # Construir el prompt completo con historial
        full_prompt = config.SYSTEM_PROMPT + "\n\n"
        
        # Añadir historial (excluyendo el system prompt y el último mensaje del usuario)
        for msg in self.history[1:-1]:  # Excluir el último mensaje que acabamos de agregar
            if msg["role"] == "user":
                full_prompt += f"Usuario: {msg['content']}\n"
            elif msg["role"] == "assistant":
                full_prompt += f"Asistente: {msg['content']}\n"
        
        full_prompt += f"\nUsuario: {user_text}\nAsistente:"
        
        logger.debug(f"Enviando prompt a Gemini (primeros 200 chars): {full_prompt[:200]}...")
        
        # Generar respuesta con streaming
        try:
            response = self.client.generate_content(
                full_prompt,
                stream=True,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                }
            )
            return response
        except Exception as e:
            logger.error(f"Error al obtener respuesta de Gemini: {e}")
            raise

    def add_assistant_response(self, response_text):
        """Agrega la respuesta del asistente al historial."""
        self.history.append({"role": "assistant", "content": response_text})
        history_size = len(self.history)
        while len(self.history) > 10:
            self.history.pop(1)
        if history_size != len(self.history):
            logger.debug(f"Historial recortado de {history_size} a {len(self.history)} mensajes")

# Inicializar el procesador LLM con la configuración del archivo config
llm_processor = LLMProcessor()
