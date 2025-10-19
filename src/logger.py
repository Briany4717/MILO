"""
Módulo de logging centralizado y profesional para MILO Server.
Proporciona logging con colores y formato consistente en toda la aplicación.
"""

import logging
import sys
import coloredlogs

# Formato de logging profesional
LOG_FORMAT = '%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Estilos de colores para cada nivel de log
FIELD_STYLES = {
    'asctime': {'color': 'white'},
    'hostname': {'color': 'magenta'},
    'levelname': {'color': 'white', 'bold': True},
    'name': {'color': 'cyan'},
    'programname': {'color': 'cyan'},
}

LEVEL_STYLES = {
    'debug': {'color': 'blue'},
    'info': {'color': 'green'},
    'warning': {'color': 'yellow'},
    'error': {'color': 'red'},
    'critical': {'color': 'red', 'bold': True},
}


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configura y devuelve un logger con formato y colores.
    
    Args:
        name: Nombre del logger (generalmente __name__ del módulo)
        level: Nivel de logging (default: logging.INFO)
    
    Returns:
        Logger configurado con colores y formato profesional
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers si ya está configurado
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(level)
    
    # Instalar coloredlogs para este logger
    coloredlogs.install(
        level=level,
        logger=logger,
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        field_styles=FIELD_STYLES,
        level_styles=LEVEL_STYLES,
        stream=sys.stdout
    )
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene o crea un logger para el módulo especificado.
    
    Args:
        name: Nombre del logger (usar __name__ del módulo)
    
    Returns:
        Logger configurado
    """
    return setup_logger(name)
