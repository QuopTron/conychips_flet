"""
VALIDADOR DE DISPOSITIVO
========================
Valida que las peticiones vengan del dispositivo correcto
"""

from typing import Optional
from core.seguridad.GeneradorHuella import GeneradorHuella


class ValidadorDispositivo:
    """Valida la autenticidad del dispositivo"""
    
    @staticmethod
    def VALIDAR_HUELLA(HUELLA_ESPERADA: str) -> bool:
        """
        Valida si la huella actual coincide con la esperada
        
        Flujo:
        1. Genera huella del dispositivo actual
        2. Compara con huella esperada
        3. Registra intentos sospechosos
        
        Args:
            HUELLA_ESPERADA: Huella almacenada en BD o token
            
        Returns:
            True si coincide, False si no
        """
        HUELLA_ACTUAL = GeneradorHuella.OBTENER_HUELLA()
        
        if HUELLA_ACTUAL != HUELLA_ESPERADA:
            print("🚨 ALERTA: Intento de acceso desde dispositivo no autorizado")
            print(f"   Esperada: {HUELLA_ESPERADA[:16]}...")
            print(f"   Actual: {HUELLA_ACTUAL[:16]}...")
            return False
        
        return True
    
    @staticmethod
    def OBTENER_INFO_DISPOSITIVO() -> dict:
        """Retorna información del dispositivo actual"""
        import platform
        
        return {
            "SISTEMA": platform.system(),
            "VERSION": platform.version(),
            "ARQUITECTURA": platform.machine(),
            "PROCESADOR": platform.processor(),
            "NOMBRE": platform.node()
        }