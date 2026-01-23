import hashlib
import platform
import uuid

class GeneradorHuella:
    
    
    @staticmethod
    def OBTENER_HUELLA() -> str:
        
        COMPONENTES = []
        
        try:
            MAC = ':'.join(['{:02x}'.format((uuid.getnode() >> elementos) & 0xff) 
                           for elementos in range(0, 8*6, 8)][::-1])
            COMPONENTES.append(f"MAC:{MAC}")
        except:
            COMPONENTES.append("MAC:unknown")
        
        COMPONENTES.append(f"NODE:{platform.node()}")
        COMPONENTES.append(f"OS:{platform.system()}")
        COMPONENTES.append(f"RELEASE:{platform.release()}")
        COMPONENTES.append(f"ARCH:{platform.machine()}")
        
        try:
            COMPONENTES.append(f"PROC:{platform.processor()}")
        except:
            COMPONENTES.append("PROC:unknown")
        
        CADENA_COMPLETA = "|".join(COMPONENTES)
        HUELLA = hashlib.sha256(CADENA_COMPLETA.encode()).hexdigest()
        
        return HUELLA
    
    @staticmethod
    def VALIDAR_HUELLA(HUELLA_ALMACENADA: str) -> bool:
        
        HUELLA_ACTUAL = GeneradorHuella.OBTENER_HUELLA()
        return HUELLA_ACTUAL == HUELLA_ALMACENADA
