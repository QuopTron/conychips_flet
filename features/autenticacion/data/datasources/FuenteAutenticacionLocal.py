"""
FUENTE DE DATOS LOCAL (SQLite)
===============================
Implementación de operaciones de autenticación con SQLite
"""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from core.base_datos.ConfiguracionBD import (
    MODELO_USUARIO, 
    MODELO_ROL, 
    MODELO_SESION,
    OBTENER_SESION
)
from core.Constantes import EXPIRACION_REFRESH_TOKEN


class FuenteAutenticacionLocal:
    """
    Fuente de datos local que maneja operaciones con SQLite
    """
    
    def __init__(self):
        """Inicializa la fuente de datos"""
        pass
    
    def _OBTENER_SESION_BD(self) -> Session:
        """Obtiene nueva sesión de base de datos"""
        return OBTENER_SESION()
    
    async def OBTENER_USUARIO_POR_EMAIL(self, EMAIL: str) -> Optional[MODELO_USUARIO]:
        """
        Busca usuario por email en BD
        
        Args:
            EMAIL: Email del usuario
            
        Returns:
            Modelo de usuario o None
        """
        SESION = self._OBTENER_SESION_BD()
        
        try:
            USUARIO = SESION.query(MODELO_USUARIO)\
                .options(joinedload(MODELO_USUARIO.ROLES))\
                .filter_by(EMAIL=EMAIL)\
                .first()
            
            return USUARIO
        finally:
            SESION.close()
    
    async def OBTENER_USUARIO_POR_ID(self, USUARIO_ID: int) -> Optional[MODELO_USUARIO]:
        """
        Busca usuario por ID en BD
        
        Args:
            USUARIO_ID: ID del usuario
            
        Returns:
            Modelo de usuario o None
        """
        SESION = self._OBTENER_SESION_BD()
        
        try:
            USUARIO = SESION.query(MODELO_USUARIO)\
                .options(joinedload(MODELO_USUARIO.ROLES))\
                .filter_by(ID=USUARIO_ID)\
                .first()
            
            return USUARIO
        finally:
            SESION.close()
    
    async def OBTENER_USUARIO_POR_NOMBRE(self, NOMBRE_USUARIO: str) -> Optional[MODELO_USUARIO]:
        """
        Busca usuario por nombre de usuario
        
        Args:
            NOMBRE_USUARIO: Nombre de usuario
            
        Returns:
            Modelo de usuario o None
        """
        SESION = self._OBTENER_SESION_BD()
        
        try:
            USUARIO = SESION.query(MODELO_USUARIO)\
                .filter_by(NOMBRE_USUARIO=NOMBRE_USUARIO)\
                .first()
            
            return USUARIO
        finally:
            SESION.close()
    
    async def CREAR_USUARIO(
        self,
        EMAIL: str,
        NOMBRE_USUARIO: str,
        CONTRASENA_HASH: str,
        HUELLA_DISPOSITIVO: str
    ) -> MODELO_USUARIO:
        """
        Crea nuevo usuario en BD
        
        Args:
            EMAIL: Email del usuario
            NOMBRE_USUARIO: Nombre de usuario
            CONTRASENA_HASH: Hash de la contraseña
            HUELLA_DISPOSITIVO: Huella del dispositivo
            
        Returns:
            Usuario creado
        """
        SESION = self._OBTENER_SESION_BD()
        
        try:
            NUEVO_USUARIO = MODELO_USUARIO(
                EMAIL=EMAIL,
                NOMBRE_USUARIO=NOMBRE_USUARIO,
                CONTRASENA_HASH=CONTRASENA_HASH,
                HUELLA_DISPOSITIVO=HUELLA_DISPOSITIVO,
                ACTIVO=True,
                VERIFICADO=False,
                FECHA_CREACION=datetime.utcnow()
            )
            
            SESION.add(NUEVO_USUARIO)
            SESION.commit()
            SESION.refresh(NUEVO_USUARIO)
            
            print(f"✅ Usuario creado en BD: {EMAIL} (ID: {NUEVO_USUARIO.ID})")
            
            return NUEVO_USUARIO
        except Exception as ERROR:
            SESION.rollback()
            print(f"❌ Error al crear usuario: {ERROR}")
            raise
        finally:
            SESION.close()
    
    async def ACTUALIZAR_ULTIMA_CONEXION(self, USUARIO_ID: int):
        """
        Actualiza timestamp de última conexión
        
        Args:
            USUARIO_ID: ID del usuario
        """
        SESION = self._OBTENER_SESION_BD()
        
        try:
            USUARIO = SESION.query(MODELO_USUARIO).filter_by(ID=USUARIO_ID).first()
            
            if USUARIO:
                USUARIO.ULTIMA_CONEXION = datetime.utcnow()
                SESION.commit()
                print(f"✅ Última conexión actualizada para usuario {USUARIO_ID}")
        except Exception as ERROR:
            SESION.rollback()
            print(f"❌ Error al actualizar última conexión: {ERROR}")
        finally:
            SESION.close()
    
    async def CREAR_SESION(
        self,
        USUARIO_ID: int,
        REFRESH_TOKEN: str,
        HUELLA_DISPOSITIVO: str,
        IP: Optional[str] = None,
        NAVEGADOR: Optional[str] = None
    ):
        """
        Crea nueva sesión en BD
        
        Args:
            USUARIO_ID: ID del usuario
            REFRESH_TOKEN: Token de refresco
            HUELLA_DISPOSITIVO: Huella del dispositivo
            IP: Dirección IP (opcional)
            NAVEGADOR: User agent (opcional)
        """
        SESION = self._OBTENER_SESION_BD()
        
        try:
            FECHA_EXPIRACION = datetime.utcnow() + timedelta(seconds=EXPIRACION_REFRESH_TOKEN)
            
            NUEVA_SESION = MODELO_SESION(
                USUARIO_ID=USUARIO_ID,
                REFRESH_TOKEN=REFRESH_TOKEN,
                HUELLA_DISPOSITIVO=HUELLA_DISPOSITIVO,
                IP=IP,
                NAVEGADOR=NAVEGADOR,
                ACTIVA=True,
                FECHA_CREACION=datetime.utcnow(),
                FECHA_EXPIRACION=FECHA_EXPIRACION
            )
            
            SESION.add(NUEVA_SESION)
            SESION.commit()
            
            print(f"✅ Sesión creada para usuario {USUARIO_ID}")
        except Exception as ERROR:
            SESION.rollback()
            print(f"❌ Error al crear sesión: {ERROR}")
            raise
        finally:
            SESION.close()
    
    async def VERIFICAR_SESION_ACTIVA(
        self,
        USUARIO_ID: int,
        REFRESH_TOKEN: str
    ) -> bool:
        """
        Verifica si existe sesión activa y válida
        
        Args:
            USUARIO_ID: ID del usuario
            REFRESH_TOKEN: Token de refresco
            
        Returns:
            True si la sesión es válida, False si no
        """
        SESION = self._OBTENER_SESION_BD()
        
        try:
            SESION_BD = SESION.query(MODELO_SESION)\
                .filter_by(
                    USUARIO_ID=USUARIO_ID,
                    REFRESH_TOKEN=REFRESH_TOKEN,
                    ACTIVA=True
                )\
                .first()
            
            if not SESION_BD:
                return False
            
            # Verificar si no está expirada
            if SESION_BD.FECHA_EXPIRACION < datetime.utcnow():
                print(f"⚠️ Sesión expirada para usuario {USUARIO_ID}")
                return False
            
            return True
        finally:
            SESION.close()
    
    async def CERRAR_SESION(self, REFRESH_TOKEN: str):
        """
        Marca sesión como inactiva
        
        Args:
            REFRESH_TOKEN: Token de la sesión
        """
        SESION = self._OBTENER_SESION_BD()
        
        try:
            SESION_BD = SESION.query(MODELO_SESION)\
                .filter_by(REFRESH_TOKEN=REFRESH_TOKEN)\
                .first()
            
            if SESION_BD:
                SESION_BD.ACTIVA = False
                SESION.commit()
                print(f"✅ Sesión cerrada para usuario {SESION_BD.USUARIO_ID}")
        except Exception as ERROR:
            SESION.rollback()
            print(f"❌ Error al cerrar sesión: {ERROR}")
        finally:
            SESION.close()
    
    async def ASIGNAR_ROL_A_USUARIO(self, USUARIO_ID: int, NOMBRE_ROL: str):
        """
        Asigna rol a usuario
        
        Args:
            USUARIO_ID: ID del usuario
            NOMBRE_ROL: Nombre del rol
        """
        SESION = self._OBTENER_SESION_BD()
        
        try:
            USUARIO = SESION.query(MODELO_USUARIO).filter_by(ID=USUARIO_ID).first()
            ROL = SESION.query(MODELO_ROL).filter_by(NOMBRE=NOMBRE_ROL).first()
            
            if USUARIO and ROL:
                if ROL not in USUARIO.ROLES:
                    USUARIO.ROLES.append(ROL)
                    SESION.commit()
                    print(f"✅ Rol '{NOMBRE_ROL}' asignado a usuario {USUARIO_ID}")
                else:
                    print(f"⚠️ Usuario {USUARIO_ID} ya tiene el rol '{NOMBRE_ROL}'")
            else:
                print(f"❌ Usuario o rol no encontrado")
        except Exception as ERROR:
            SESION.rollback()
            print(f"❌ Error al asignar rol: {ERROR}")
        finally:
            SESION.close()
    
    async def REMOVER_ROL_DE_USUARIO(self, USUARIO_ID: int, NOMBRE_ROL: str):
        """
        Remueve rol de usuario
        
        Args:
            USUARIO_ID: ID del usuario
            NOMBRE_ROL: Nombre del rol
        """
        SESION = self._OBTENER_SESION_BD()
        
        try:
            USUARIO = SESION.query(MODELO_USUARIO).filter_by(ID=USUARIO_ID).first()
            ROL = SESION.query(MODELO_ROL).filter_by(NOMBRE=NOMBRE_ROL).first()
            
            if USUARIO and ROL:
                if ROL in USUARIO.ROLES:
                    USUARIO.ROLES.remove(ROL)
                    SESION.commit()
                    print(f"✅ Rol '{NOMBRE_ROL}' removido de usuario {USUARIO_ID}")
        except Exception as ERROR:
            SESION.rollback()
            print(f"❌ Error al remover rol: {ERROR}")
        finally:
            SESION.close()
    
    async def OBTENER_SESIONES_ACTIVAS(self, USUARIO_ID: int) -> List[MODELO_SESION]:
        """
        Obtiene todas las sesiones activas de un usuario
        
        Args:
            USUARIO_ID: ID del usuario
            
        Returns:
            Lista de sesiones activas
        """
        SESION = self._OBTENER_SESION_BD()
        
        try:
            SESIONES = SESION.query(MODELO_SESION)\
                .filter_by(USUARIO_ID=USUARIO_ID, ACTIVA=True)\
                .filter(MODELO_SESION.FECHA_EXPIRACION > datetime.utcnow())\
                .all()
            
            return SESIONES
        finally:
            SESION.close()