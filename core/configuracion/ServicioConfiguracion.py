"""Servicio para obtener y actualizar configuraciones del sistema"""
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION, 
    MODELO_CONFIGURACION_SISTEMA,
    MODELO_LOG_CONFIGURACION
)
from datetime import datetime, timezone
from typing import Optional, Union


class ServicioConfiguracion:
    """Gestiona las configuraciones del sistema almacenadas en BD"""
    
    _cache = {}  # Cache simple en memoria
    
    @classmethod
    def obtener_valor(cls, clave: str, default: any = None) -> Union[int, float, bool, str, None]:
        """
        Obtiene el valor de una configuración desde BD (con cache)
        
        Args:
            clave: Clave de la configuración (ej: "vouchers.tiempo_bloqueo_minutos")
            default: Valor por defecto si no existe
            
        Returns:
            Valor parseado según su tipo (int, float, bool, str)
        """
        # Verificar cache
        if clave in cls._cache:
            return cls._cache[clave]
        
        # Obtener desde BD
        sesion = OBTENER_SESION()
        try:
            config = sesion.query(MODELO_CONFIGURACION_SISTEMA).filter_by(CLAVE=clave).first()
            
            if not config:
                cls._cache[clave] = default
                return default
            
            # Parsear según tipo
            valor = cls._parsear_valor(config.VALOR, config.TIPO)
            cls._cache[clave] = valor
            return valor
            
        finally:
            sesion.close()
    
    @classmethod
    def actualizar_valor(cls, clave: str, valor: any, usuario_id: Optional[int] = None) -> bool:
        """
        Actualiza una configuración en BD y registra el cambio en el log
        
        Args:
            clave: Clave de la configuración
            valor: Nuevo valor
            usuario_id: ID del usuario que modifica (opcional)
            
        Returns:
            True si se actualizó correctamente
        """
        sesion = OBTENER_SESION()
        try:
            config = sesion.query(MODELO_CONFIGURACION_SISTEMA).filter_by(CLAVE=clave).first()
            
            if not config:
                return False
            
            # Guardar valor anterior para el log
            valor_anterior = config.VALOR
            
            # Convertir valor a string
            config.VALOR = str(valor)
            config.FECHA_MODIFICACION = datetime.now(timezone.utc)
            if usuario_id:
                config.MODIFICADO_POR = usuario_id
            
            # Crear registro en el log
            log = MODELO_LOG_CONFIGURACION(
                CONFIGURACION_ID=config.ID,
                CLAVE=clave,
                VALOR_ANTERIOR=valor_anterior,
                VALOR_NUEVO=str(valor),
                USUARIO_ID=usuario_id,
                FECHA=datetime.now(timezone.utc)
            )
            sesion.add(log)
            
            sesion.commit()
            
            # Limpiar cache
            if clave in cls._cache:
                del cls._cache[clave]
            
            return True
            
        except Exception as e:
            sesion.rollback()
            print(f"[ERROR] No se pudo actualizar configuración {clave}: {e}")
            return False
        finally:
            sesion.close()
    
    @classmethod
    def obtener_todas(cls, categoria: Optional[str] = None) -> list:
        """
        Obtiene todas las configuraciones (opcionalmente filtradas por categoría)
        
        Args:
            categoria: Filtrar por categoría (opcional)
            
        Returns:
            Lista de configuraciones
        """
        sesion = OBTENER_SESION()
        try:
            query = sesion.query(MODELO_CONFIGURACION_SISTEMA)
            
            if categoria:
                query = query.filter_by(CATEGORIA=categoria)
            
            configs = query.all()
            return [
                {
                    "id": c.ID,
                    "clave": c.CLAVE,
                    "valor": cls._parsear_valor(c.VALOR, c.TIPO),
                    "tipo": c.TIPO,
                    "descripcion": c.DESCRIPCION,
                    "categoria": c.CATEGORIA,
                    "fecha_modificacion": c.FECHA_MODIFICACION
                }
                for c in configs
            ]
        finally:
            sesion.close()
    
    @staticmethod
    def _parsear_valor(valor_str: str, tipo: str) -> Union[int, float, bool, str]:
        """Convierte string a su tipo correspondiente"""
        try:
            if tipo == "int":
                return int(valor_str)
            elif tipo == "float":
                return float(valor_str)
            elif tipo == "bool":
                return valor_str.lower() in ("true", "1", "yes", "si", "sí")
            else:  # str
                return valor_str
        except Exception:
            return valor_str
    
    @classmethod
    def limpiar_cache(cls):
        """Limpia el cache de configuraciones"""
        cls._cache.clear()
    
    @classmethod
    def obtener_historial(cls, clave: Optional[str] = None, limite: int = 50) -> list:
        """
        Obtiene el historial de cambios de configuraciones
        
        Args:
            clave: Filtrar por clave específica (opcional)
            limite: Número máximo de registros a retornar
            
        Returns:
            Lista de cambios ordenados por fecha descendente
        """
        sesion = OBTENER_SESION()
        try:
            query = sesion.query(MODELO_LOG_CONFIGURACION)
            
            if clave:
                query = query.filter_by(CLAVE=clave)
            
            logs = query.order_by(MODELO_LOG_CONFIGURACION.FECHA.desc()).limit(limite).all()
            
            return [
                {
                    "id": log.ID,
                    "clave": log.CLAVE,
                    "valor_anterior": log.VALOR_ANTERIOR,
                    "valor_nuevo": log.VALOR_NUEVO,
                    "usuario_id": log.USUARIO_ID,
                    "usuario_nombre": log.USUARIO.NOMBRE_USUARIO if log.USUARIO else "Sistema",
                    "fecha": log.FECHA
                }
                for log in logs
            ]
        finally:
            sesion.close()
