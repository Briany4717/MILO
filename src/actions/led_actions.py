
import src.esp32_manager as esp32_manager


def encender_led(color: str):
    """Enciende el LED con el color especificado."""
    esp32_manager.send_command("led_control", {"color": color, "state": "on"})

def apagar_led(color: str):
    """Apaga el LED con el color especificado."""
    esp32_manager.send_command("led_control", {"color": color, "state": "off"})

def parpadear_led(color: str, duracion: float):
    """Hace parpadear el LED con el color especificado durante la duración dada."""
    esp32_manager.send_command("led_control", {"color": color, "state": "blink", "duration": duracion})