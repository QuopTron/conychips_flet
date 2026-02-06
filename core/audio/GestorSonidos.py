"""
📢 Gestor de Sonidos y Audio - Notificaciones auditivas del sistema
"""

import platform
import subprocess
import os
from pathlib import Path


class GestorSonidos:
    """Gestor centralizado de sonidos y notificaciones auditivas"""
    
    # Rutas de sonidos
    SONIDOS = {
        "mensaje_nuevo": "notification_message.mp3",
        "alerta": "notification_alert.mp3",
        "exito": "notification_success.mp3",
        "error": "notification_error.mp3",
    }
    
    # Ruta base para assets
    RUTA_ASSETS = Path(__file__).parent.parent.parent / "assets" / "sounds"
    
    @staticmethod
    def REPRODUCIR_SONIDO(tipo: str = "mensaje_nuevo") -> bool:
        """
        Reproduce un sonido de notificación
        
        Args:
            tipo: Tipo de sonido ('mensaje_nuevo', 'alerta', 'exito', 'error')
            
        Returns:
            bool: True si se reprodujo exitosamente, False si hubo error
        """
        try:
            # Obtener el sistema operativo
            sistema = platform.system()
            
            # Intentar reproducir sonido del sistema
            if sistema == "Darwin":  # macOS
                # Usar el sonido del sistema en macOS
                subprocess.Popen(
                    ["afplay", "/System/Library/Sounds/Glass.aiff"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True
                
            elif sistema == "Windows":
                # Usar sonidos del sistema en Windows
                try:
                    import winsound
                    winsound.Beep(1000, 200)  # Frecuencia 1000Hz, duración 200ms
                    return True
                except ImportError:
                    pass
                    
            elif sistema == "Linux":
                # Usar paplay o aplay en Linux
                try:
                    # Intenta usar paplay primero (PulseAudio)
                    subprocess.Popen(
                        ["paplay", "/usr/share/sounds/freedesktop/stereo/message.oga"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    return True
                except (FileNotFoundError, OSError):
                    try:
                        # Fallback a aplay (ALSA)
                        subprocess.Popen(
                            ["aplay", "/usr/share/sounds/freedesktop/stereo/message.oga"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        return True
                    except (FileNotFoundError, OSError):
                        # Fallback a beep
                        os.system("echo -ne '\a'")
                        return True
            
            return False
            
        except Exception as e:
            print(f"Error reproduciendo sonido: {e}")
            return False
    
    @staticmethod
    def NOTIFICAR_MENSAJE_NUEVO(pedido_id: int = None, cliente_nombre: str = "Cliente"):
        """
        Reproduce notificación para mensaje nuevo
        
        Args:
            pedido_id: ID del pedido (opcional)
            cliente_nombre: Nombre del cliente que envió el mensaje
        """
        GestorSonidos.REPRODUCIR_SONIDO("mensaje_nuevo")
    
    @staticmethod
    def NOTIFICAR_ALERTA(titulo: str):
        """
        Reproduce notificación de alerta
        
        Args:
            titulo: Título de la alerta
        """
        GestorSonidos.REPRODUCIR_SONIDO("alerta")
    
    @staticmethod
    def NOTIFICAR_EXITO(titulo: str):
        """
        Reproduce notificación de éxito
        
        Args:
            titulo: Título del éxito
        """
        GestorSonidos.REPRODUCIR_SONIDO("exito")
    
    @staticmethod
    def NOTIFICAR_ERROR(titulo: str):
        """
        Reproduce notificación de error
        
        Args:
            titulo: Título del error
        """
        GestorSonidos.REPRODUCIR_SONIDO("error")
