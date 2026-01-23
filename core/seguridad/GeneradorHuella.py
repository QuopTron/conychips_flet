"""
GENERADOR DE HUELLA DE DISPOSITIVO
==================================
Crea identificador único por dispositivo usando características hardware
"""

import hashlib
import platform
import uuid


class GeneradorHuella:
    """Genera huella única e irreversible del dispositivo"""
    
    @staticmethod
    def OBTENER_HUELLA() -> str:
        """
        Genera huella única basada en características del dispositivo
        
        COMPONENTES:
        1. MAC Address
        2. Nombre del dispositivo
        3. Sistema operativo
        4. Arquitectura del procesador
        
        Returns:
            Hash SHA-256 de 64 caracteres
        """
        COMPONENTES = []
        
        # MAC Address
        try:
            MAC = ':'.join(['{:02x}'.format((uuid.getnode() >> elementos) & 0xff) 
                           for elementos in range(0, 8*6, 8)][::-1])
            COMPONENTES.append(f"MAC:{MAC}")
        except:
            COMPONENTES.append("MAC:unknown")
        
        # Información del sistema
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
        """Valida si la huella actual coincide con la almacenada"""
        HUELLA_ACTUAL = GeneradorHuella.OBTENER_HUELLA()
        return HUELLA_ACTUAL == HUELLA_ALMACENADA