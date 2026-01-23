"""
CASO DE USO: INICIAR SESIÓN
============================
Lógica de negocio para autenticación de usuarios
"""

from typing import Dict, Optional
import bcrypt
from datetime import datetime
from features.autenticacion.domain.RepositorioAutenticacion import RepositorioAutenticacion
from features.autenticacion.domain.entities.Usuario import Usuario
from core.seguridad.ManejadorJWT import ManejadorJWT
from core.seguridad.GeneradorHuella import GeneradorHuella
from core.seguridad.EncriptadorGPU import EncriptadorGPU


class IniciarSesion:
    """
    Caso de uso para iniciar sesión
    
    Flujo completo:
    1. Valida credenciales
    2. Genera huella del dispositivo
    3. Crea tokens JWT
    4. Guarda sesión en BD
    5. Retorna usuario y tokens
    """
    
    def __init__(self, REPOSITORIO: RepositorioAutenticacion):
        """
        Inicializa el caso de uso
        
        Args:
            REPOSITORIO: Repositorio de autenticación
        """
        self._REPOSITORIO = REPOSITORIO
        self._MANEJADOR_JWT = ManejadorJWT()
    
    async def EJECUTAR(self, EMAIL: str, CONTRASENA: str) -> Dict:
        """
        Ejecuta el caso de uso de inicio de sesión
        
        Args:
            EMAIL: Email del usuario
            CONTRASENA: Contraseña en texto plano
            
        Returns:
            Diccionario con resultado:
            {
                "EXITO": bool,
                "USUARIO": Usuario (si exitoso),
                "ACCESS_TOKEN": str (si exitoso),
                "REFRESH_TOKEN": str (si exitoso),
                "ERROR": str (si falla),
                "CODIGO": int
            }
        """
        print(f"🔐 Iniciando sesión para: {EMAIL}")
        
        try:
            # PASO 1: Buscar usuario por email
            USUARIO_BD = await self._REPOSITORIO.OBTENER_POR_EMAIL(EMAIL)
            
            if not USUARIO_BD:
                print(f"❌ Usuario no encontrado: {EMAIL}")
                return {
                    "EXITO": False,
                    "ERROR": "Credenciales inválidas",
                    "CODIGO": 401
                }
            
            # PASO 2: Verificar si el usuario está activo
            if not USUARIO_BD.ACTIVO:
                print(f"❌ Usuario inactivo: {EMAIL}")
                return {
                    "EXITO": False,
                    "ERROR": "Usuario inactivo. Contacta al administrador.",
                    "CODIGO": 403
                }
            
            # PASO 3: Verificar contraseña
            CONTRASENA_VALIDA = bcrypt.checkpw(
                CONTRASENA.encode('utf-8'),
                USUARIO_BD.CONTRASENA_HASH.encode('utf-8')
            )
            
            if not CONTRASENA_VALIDA:
                print(f"❌ Contraseña inválida para: {EMAIL}")
                return {
                    "EXITO": False,
                    "ERROR": "Credenciales inválidas",
                    "CODIGO": 401
                }
            
            # PASO 4: Generar huella del dispositivo
            HUELLA_DISPOSITIVO = GeneradorHuella.OBTENER_HUELLA()
            print(f"🔑 Huella generada: {HUELLA_DISPOSITIVO[:16]}...")
            
            # PASO 5: Convertir usuario BD a entidad de dominio
            USUARIO_DOMINIO = self._MAPEAR_A_DOMINIO(USUARIO_BD)
            
            # PASO 6: Obtener roles del usuario
            ROLES = [ROL.NOMBRE for ROL in USUARIO_BD.ROLES]
            
            if not ROLES:
                # Asignar rol de usuario por defecto
                from core.Constantes import ROLES as ROLES_SISTEMA
                ROLES = [ROLES_SISTEMA.USUARIO]
                print(f"⚠️ Usuario sin roles, asignando rol por defecto: {ROLES}")
            
            # PASO 7: Generar tokens JWT
            ACCESS_TOKEN = self._MANEJADOR_JWT.CREAR_ACCESS_TOKEN(
                USUARIO_ID=USUARIO_BD.ID,
                EMAIL=USUARIO_BD.EMAIL,
                ROLES=ROLES,
                HUELLA_DISPOSITIVO=HUELLA_DISPOSITIVO
            )
            
            REFRESH_TOKEN = self._MANEJADOR_JWT.CREAR_REFRESH_TOKEN(
                USUARIO_ID=USUARIO_BD.ID,
                HUELLA_DISPOSITIVO=HUELLA_DISPOSITIVO
            )
            
            # PASO 8: Guardar sesión en BD
            await self._REPOSITORIO.CREAR_SESION(
                USUARIO_ID=USUARIO_BD.ID,
                REFRESH_TOKEN=REFRESH_TOKEN,
                HUELLA_DISPOSITIVO=HUELLA_DISPOSITIVO
            )
            
            # PASO 9: Actualizar última conexión
            await self._REPOSITORIO.ACTUALIZAR_ULTIMA_CONEXION(USUARIO_BD.ID)
            
            print(f"✅ Login exitoso para: {EMAIL}")
            
            return {
                "EXITO": True,
                "USUARIO": USUARIO_DOMINIO,
                "ACCESS_TOKEN": ACCESS_TOKEN,
                "REFRESH_TOKEN": REFRESH_TOKEN,
                "CODIGO": 200
            }
        
        except Exception as ERROR:
            print(f"❌ Error al iniciar sesión: {ERROR}")
            return {
                "EXITO": False,
                "ERROR": "Error interno del servidor",
                "CODIGO": 500
            }
    
    def _MAPEAR_A_DOMINIO(self, USUARIO_BD) -> Usuario:
        """
        Convierte modelo de BD a entidad de dominio
        
        Args:
            USUARIO_BD: Modelo de SQLAlchemy
            
        Returns:
            Entidad Usuario del dominio
        """
        return Usuario(
            ID=USUARIO_BD.ID,
            EMAIL=USUARIO_BD.EMAIL,
            NOMBRE_USUARIO=USUARIO_BD.NOMBRE_USUARIO,
            ROLES=[ROL.NOMBRE for ROL in USUARIO_BD.ROLES],
            ACTIVO=USUARIO_BD.ACTIVO,
            VERIFICADO=USUARIO_BD.VERIFICADO,
            FECHA_CREACION=USUARIO_BD.FECHA_CREACION,
            ULTIMA_CONEXION=USUARIO_BD.ULTIMA_CONEXION
        )