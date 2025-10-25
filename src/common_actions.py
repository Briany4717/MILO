

"""
Gestión de acciones comunes del asistente.
Integración con el módulo sensorial ESP32 para control de hardware.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import re
from src.logger import get_logger
from src.esp32_manager import get_esp32_manager

logger = get_logger(__name__)

# Diccionario de variantes de pronunciación
# Mapea variantes comunes a la forma canónica
PRONUNCIATION_VARIANTS = {
    # Variantes de "LED"
    "led": "led",
    "let": "led",
    "l e d": "led",
    "l.e.d": "led",
    "ele e de": "led",
    
    # Variantes de colores
    "rojo": "rojo",
    "roxo": "rojo",
    "rollo": "rojo",
    
    "azul": "azul",
    "asul": "azul",
    
    "verde": "verde",
    "berde": "verde",
    
    # Variantes de acciones
    "enciende": "enciende",
    "encienda": "enciende",
    "prende": "enciende",
    "prenda": "enciende",
    "activa": "enciende",
    "activar": "enciende",
    
    "apaga": "apaga",
    "apagar": "apaga",
    "apague": "apaga",
    "desactiva": "apaga",
    "desactivar": "apaga",
    "desactive": "apaga",
    
    # Artículos y palabras comunes (mantenerlas como están)
    "el": "el",
    "la": "la",
    "los": "los",
    "las": "las",

    ".":"",
}

# Mapeo de acciones canónicas a comandos ESP32
ACTION_TO_ESP32_COMMAND = {
    "enciende el led azul": {"command": "led_control", "data": {"color": "blue", "state": "on"}},
    "apaga el led azul": {"command": "led_control", "data": {"color": "blue", "state": "off"}},
    "enciende el led rojo": {"command": "led_control", "data": {"color": "red", "state": "on"}},
    "apaga el led rojo": {"command": "led_control", "data": {"color": "red", "state": "off"}},
    "enciende el led verde": {"command": "led_control", "data": {"color": "green", "state": "on"}},
    "apaga el led verde": {"command": "led_control", "data": {"color": "green", "state": "off"}},
}

# Acciones comunes canónicas
COMMON_ACTIONS = [
    "dime la hora",
    "dime la temperatura",
    "enciende el led azul",
    "apaga el led azul",
    "enciende el led rojo",
    "apaga el led rojo",
    "enciende el led verde",
    "apaga el led verde"
]


def normalize_text(text: str) -> str:
    """
    Normaliza el texto de entrada:
    - Convierte a minúsculas
    - Reemplaza variantes de pronunciación
    - Limpia espacios extra
    
    Args:
        text: Texto a normalizar
    
    Returns:
        Texto normalizado
    """
    # Convertir a minúsculas
    text = text.lower().strip()
    
    # Reemplazar variantes de pronunciación palabra por palabra
    words = text.split()
    normalized_words = []
    
    for word in words:
        # Buscar la forma canónica de la palabra
        normalized_word = PRONUNCIATION_VARIANTS.get(word, word)
        normalized_words.append(normalized_word)
    
    # Unir las palabras normalizadas
    normalized_text = " ".join(normalized_words)
    
    # Limpiar espacios múltiples
    normalized_text = re.sub(r'\s+', ' ', normalized_text)
    
    logger.info(f"Texto normalizado: '{text}' → '{normalized_text}'")
    
    return normalized_text


def common_action_exists(action_name: str) -> bool:
    """
    Verifica si la acción común existe en el sistema.
    Normaliza el texto antes de comparar para manejar variantes de pronunciación.
    
    Args:
        action_name: Nombre de la acción a verificar
    
    Returns:
        True si la acción existe, False en caso contrario
    """
    normalized_action = normalize_text(action_name)
    exists = normalized_action in COMMON_ACTIONS
    
    if exists:
        logger.debug(f"Acción común encontrada: '{action_name}' → '{normalized_action}'")
    
    return exists


def get_common_action_response(action_name: str) -> str:
    """
    Devuelve una respuesta predefinida para la acción común.
    Normaliza el texto antes de buscar la respuesta.
    
    Args:
        action_name: Nombre de la acción
    
    Returns:
        Respuesta textual para la acción
    """
    # Normalizar la acción
    normalized_action = normalize_text(action_name)
    
    # Obtener hora actual
    current_time = datetime.now().strftime("%I:%M %p")
    
    # Respuestas predefinidas (todas en minúsculas, sin puntos finales)
    responses = {
        "dime la hora": f"La hora actual es {current_time}",
        "dime la temperatura": "La temperatura actual es de 22 grados Celsius",
        "enciende el led azul": "El LED azul ha sido encendido",
        "apaga el led azul": "El LED azul ha sido apagado",
        "enciende el led rojo": "El LED rojo ha sido encendido",
        "apaga el led rojo": "El LED rojo ha sido apagado",
        "enciende el led verde": "El LED verde ha sido encendido",
        "apaga el led verde": "El LED verde ha sido apagado"
    }
    
    return responses.get(normalized_action, "No tengo una respuesta para esa acción.")


async def execute_common_action(action_name: str) -> bool:
    """
    Ejecuta la acción común y devuelve el resultado.
    Verifica la conexión con el ESP32 antes de ejecutar acciones de hardware.
    Normaliza el texto antes de buscar el comando.
    
    Args:
        action_name: Nombre de la acción a ejecutar
    
    Returns:
        True si la acción se ejecutó correctamente, False en caso contrario
    """
    # Normalizar la acción
    normalized_action = normalize_text(action_name)
    
    logger.info(f"Ejecutando acción: {action_name} → {normalized_action}")
    
    # Acciones que no requieren ESP32
    if normalized_action in ["dime la hora", "dime la temperatura"]:
        logger.debug(f"Acción '{normalized_action}' no requiere ESP32")
        return True
    
    # Acciones que requieren ESP32
    if normalized_action in ACTION_TO_ESP32_COMMAND:
        esp32_manager = get_esp32_manager()
        
        # Verificar si el ESP32 está configurado
        if esp32_manager is None:
            logger.warning("ESP32 no configurado - Acción omitida")
            return False
        
        # Verificar conexión
        if not esp32_manager.is_esp32_connected():
            logger.warning(f"ESP32 no conectado - No se puede ejecutar '{normalized_action}'")
            return False
        
        # Enviar comando al ESP32
        cmd_info = ACTION_TO_ESP32_COMMAND[normalized_action]
        success = await esp32_manager.send_command(
            cmd_info["command"],
            cmd_info["data"]
        )
        
        if success:
            logger.info(f"Comando '{action_name}' ejecutado correctamente en ESP32")
        else:
            logger.error(f"Error al ejecutar comando '{action_name}' en ESP32")
        
        return success
    
    logger.warning(f"Acción '{action_name}' no reconocida")
    return False


def get_esp32_status() -> dict:
    """
    Obtiene el estado actual de la conexión con el ESP32.
    
    Returns:
        Diccionario con información del estado
    """
    esp32_manager = get_esp32_manager()
    
    if esp32_manager is None:
        return {
            "configured": False,
            "connected": False,
            "message": "ESP32 no configurado"
        }
    
    status = esp32_manager.get_status()
    return {
        "configured": True,
        "connected": status["connected"],
        "client_address": status.get("client_address"),
        "websocket_open": status["websocket_open"]
    }