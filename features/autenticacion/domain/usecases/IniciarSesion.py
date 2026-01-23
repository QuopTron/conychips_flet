from typing import Dict, Optional
import bcrypt
from datetime import datetime
from features.autenticacion.domain.RepositorioAutenticacion import RepositorioAutenticacion
from features.autenticacion.domain.entities.Usuario import Usuario
from core.seguridad.ManejadorJWT import ManejadorJWT
from core.seguridad.GeneradorHuella import GeneradorHuella
from core.seguridad.EncriptadorGPU import EncriptadorGPU

class IniciarSesion:
    
    
    def __init__(self, REPOSITORIO: RepositorioAutenticacion):
        
        self._REPOSITORIO = REPOSITORIO
        self._MANEJADOR_JWT = ManejadorJWT()
    
    async def EJECUTAR(self, EMAIL: str, CONTRASENA: str) -> Dict:
        
        print(f"🔐 Iniciando sesión para: {EMAIL}")
        
        try:
            USUARIO_BD = await self._REPOSITORIO.OBTENER_POR_EMAIL(EMAIL)
            
            if not USUARIO_BD:
                print(f"❌ Usuario no encontrado: {EMAIL}")
                return {
                    "EXITO": False,
                    "ERROR": "Credenciales inválidas",
                    "CODIGO": 401
                }
            
            if not USUARIO_BD.ACTIVO:
                print(f"❌ Usuario inactivo: {EMAIL}")
                return {
                    "EXITO": False,
                    "ERROR": "Usuario inactivo. Contacta al administrador.",
                    "CODIGO": 403
                }
            
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
            
            HUELLA_DISPOSITIVO = GeneradorHuella.OBTENER_HUELLA()
            print(f"🔑 Huella generada: {HUELLA_DISPOSITIVO[:16]}...")
            
            USUARIO_DOMINIO = self._MAPEAR_A_DOMINIO(USUARIO_BD)
            
            ROLES = [ROL.NOMBRE for ROL in USUARIO_BD.ROLES]
            
            if not ROLES:
                from core.Constantes import ROLES as ROLES_SISTEMA
                ROLES = [ROLES_SISTEMA.USUARIO]
                print(f"⚠️ Usuario sin roles, asignando rol por defecto: {ROLES}")
            
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
            
            await self._REPOSITORIO.CREAR_SESION(
                USUARIO_ID=USUARIO_BD.ID,
                REFRESH_TOKEN=REFRESH_TOKEN,
                HUELLA_DISPOSITIVO=HUELLA_DISPOSITIVO
            )
            
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
