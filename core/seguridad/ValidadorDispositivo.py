from typing import Optional
from core.seguridad.GeneradorHuella import GeneradorHuella

class ValidadorDispositivo:
    
    
    @staticmethod
    def VALIDAR_HUELLA(HUELLA_ESPERADA: str) -> bool:
        
        HUELLA_ACTUAL = GeneradorHuella.OBTENER_HUELLA()
        
        if HUELLA_ACTUAL != HUELLA_ESPERADA:
            print("🚨 ALERTA: Intento de acceso desde dispositivo no autorizado")
            print(f"   Esperada: {HUELLA_ESPERADA[:16]}...")
            print(f"   Actual: {HUELLA_ACTUAL[:16]}...")
            return False
        
        return True
    
    @staticmethod
    def OBTENER_INFO_DISPOSITIVO() -> dict:
        
        import platform
        
        return {
            "SISTEMA": platform.system(),
            "VERSION": platform.version(),
            "ARQUITECTURA": platform.machine(),
            "PROCESADOR": platform.processor(),
            "NOMBRE": platform.node()
        }
