"""
Configuración global de warnings para MILO Server.
Suprime warnings conocidos y seguros de las dependencias.
"""
import warnings

def configure_warnings():
    """
    Configura los filtros de warnings para el proyecto.
    Debe llamarse al inicio de la aplicación.
    """
    # Suprimir FutureWarnings de torch.load sobre weights_only
    # Necesitamos weights_only=False para cargar objetos complejos de TTS y modelos
    warnings.filterwarnings('ignore', category=FutureWarning, module='torch')
    warnings.filterwarnings('ignore', category=FutureWarning, message='.*weights_only.*')
    
    # Suprimir warnings de TTS sobre torch.load
    warnings.filterwarnings('ignore', category=FutureWarning, module='TTS')
    
    # Opcional: Suprimir deprecation warnings de otras librerías
    # warnings.filterwarnings('ignore', category=DeprecationWarning)
