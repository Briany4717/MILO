"""
Gestor de conexión con el módulo sensorial ESP32.
El ESP32 se conecta AL servidor, no al revés.
El servidor mantiene esta conexión separada de las conexiones de usuarios.
"""

import asyncio
import json
from typing import Optional, Dict, Any
from websockets.server import WebSocketServerProtocol
from src.logger import get_logger

logger = get_logger(__name__)


class ESP32ConnectionManager:
    """
    Gestiona la conexión entrante del módulo sensorial ESP32.
    El ESP32 se conecta al servidor y se identifica.
    """
    
    def __init__(self):
        """Inicializa el gestor de conexión."""
        self.esp32_websocket: Optional[WebSocketServerProtocol] = None
        self.is_connected = False
        self._command_timeout = 5.0
        self._message_handler_task: Optional[asyncio.Task] = None
    
    def is_esp32_connected(self) -> bool:
        """
        Verifica si el ESP32 está conectado.
        
        Returns:
            True si está conectado, False en caso contrario
        """
        return self.is_connected and self.esp32_websocket is not None
    
    async def register_esp32(self, websocket: WebSocketServerProtocol):
        """
        Registra una nueva conexión como el módulo ESP32.
        
        Args:
            websocket: Conexión WebSocket del ESP32
        """
        # Si ya hay un ESP32 conectado, desconectar el anterior
        if self.esp32_websocket:
            logger.warning("ESP32 ya conectado - Reemplazando conexión anterior")
            await self.disconnect_esp32()
        
        self.esp32_websocket = websocket
        self.is_connected = True
        
        # Obtener información del cliente
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"ESP32 registrado correctamente desde {client_info}")
        
        # Iniciar tarea para manejar mensajes entrantes del ESP32
        self._message_handler_task = asyncio.create_task(self._handle_esp32_messages())
    
    async def _handle_esp32_messages(self):
        """Tarea que maneja mensajes entrantes del ESP32."""
        try:
            async for message in self.esp32_websocket:
                if isinstance(message, str):
                    await self.handle_esp32_message(message)
        except asyncio.CancelledError:
            logger.debug("Tarea de manejo de mensajes ESP32 cancelada")
            raise
        except Exception as e:
            logger.warning(f"Conexión ESP32 finalizada: {e}")
        finally:
            self.handle_esp32_disconnection()
    
    async def disconnect_esp32(self):
        """Desconecta el ESP32 actual de forma limpia."""
        if self._message_handler_task:
            self._message_handler_task.cancel()
            try:
                await self._message_handler_task
            except asyncio.CancelledError:
                pass
            self._message_handler_task = None
        
        if self.esp32_websocket:
            try:
                await self.esp32_websocket.close()
                logger.info("ESP32 desconectado correctamente")
            except Exception as e:
                logger.warning(f"Error al cerrar conexión ESP32: {e}")
            finally:
                self.esp32_websocket = None
                self.is_connected = False
    
    def handle_esp32_disconnection(self):
        """Maneja la desconexión inesperada del ESP32."""
        logger.warning("ESP32 desconectado inesperadamente")
        self.esp32_websocket = None
        self.is_connected = False
        if self._message_handler_task:
            self._message_handler_task.cancel()
            self._message_handler_task = None
    
    async def send_command(self, command: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Envía un comando al ESP32.
        
        Args:
            command: Nombre del comando a enviar
            data: Datos adicionales del comando (opcional)
        
        Returns:
            True si el comando se envió correctamente, False en caso contrario
        """
        if not self.is_esp32_connected():
            logger.warning(f"No se puede enviar comando '{command}': ESP32 no conectado")
            return False
        
        try:
            message = {
                "command": command,
                "data": data or {}
            }
            
            await self.esp32_websocket.send(json.dumps(message))
            logger.debug(f"Comando '{command}' enviado al ESP32")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando comando '{command}' al ESP32: {e}")
            self.handle_esp32_disconnection()
            return False
    
    async def send_command_and_wait_response(
        self, 
        command: str, 
        data: Optional[Dict[str, Any]] = None,
        timeout: float = None
    ) -> Optional[Dict[str, Any]]:
        """
        Envía un comando y espera una respuesta del ESP32.
        
        Args:
            command: Nombre del comando
            data: Datos del comando
            timeout: Tiempo máximo de espera en segundos
        
        Returns:
            Respuesta del ESP32 como diccionario, o None si falla
        """
        if timeout is None:
            timeout = self._command_timeout
        
        if not await self.send_command(command, data):
            return None
        
        try:
            # Esperar respuesta con timeout
            response_str = await asyncio.wait_for(
                self.esp32_websocket.recv(),
                timeout=timeout
            )
            
            response = json.loads(response_str)
            logger.debug(f"Respuesta recibida del ESP32: {response}")
            return response
            
        except asyncio.TimeoutError:
            logger.warning(f"Timeout esperando respuesta del comando '{command}'")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando respuesta del ESP32: {e}")
            return None
        except Exception as e:
            logger.error(f"Error recibiendo respuesta del ESP32: {e}")
            self.handle_esp32_disconnection()
            return None
    
    async def handle_esp32_message(self, message: str):
        """
        Procesa mensajes entrantes del ESP32 (telemetría, eventos, etc.).
        
        Args:
            message: Mensaje JSON del ESP32
        """
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")
            
            if message_type == "telemetry":
                # Telemetría del ESP32 (temperatura, sensores, etc.)
                logger.debug(f"Telemetría ESP32: {data.get('data')}")
            elif message_type == "event":
                # Eventos del ESP32 (botón presionado, movimiento detectado, etc.)
                event_name = data.get('event', 'unknown')
                logger.info(f"Evento ESP32: {event_name}")
            elif message_type == "response":
                # Respuesta a un comando (ya manejado en send_command_and_wait_response)
                logger.debug(f"Respuesta ESP32: {data}")
            elif message_type == "heartbeat":
                # Heartbeat para mantener la conexión viva
                logger.debug("Heartbeat ESP32 recibido")
            else:
                logger.debug(f"Mensaje ESP32 tipo '{message_type}': {data}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando mensaje ESP32: {e}")
        except Exception as e:
            logger.error(f"Error procesando mensaje ESP32: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual de la conexión ESP32.
        
        Returns:
            Diccionario con información del estado
        """
        status = {
            "connected": self.is_connected,
            "websocket_open": False,
            "client_address": None
        }
        
        if self.esp32_websocket:
            status["websocket_open"] = not self.esp32_websocket.closed
            status["client_address"] = f"{self.esp32_websocket.remote_address[0]}:{self.esp32_websocket.remote_address[1]}"
        
        return status


# Instancia global del gestor
esp32_manager = ESP32ConnectionManager()


def get_esp32_manager() -> ESP32ConnectionManager:
    """
    Obtiene la instancia global del gestor ESP32.
    
    Returns:
        Instancia del gestor
    """
    return esp32_manager
