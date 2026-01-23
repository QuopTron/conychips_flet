"""
CASO DE USO: REGISTRAR USUARIO
===============================
Lógica de negocio para registro de nuevos usuarios
"""

from typing import Dict
import bcrypt
from features.autenticacion.domain.RepositorioAutenticacion import RepositorioAutenticacion
from core.seguridad.GeneradorHuella import GeneradorHuella
from core.Constantes import ROLES


class RegistrarUsuario:
    """
    Caso de uso para registrar nuevos usuarios
    
    Flujo completo:
    1. Valida que email no exista
    2. Valida que nombre de usuario no exista
    3. Hashea contraseña con bcrypt
    4. Genera huella de dispositivo
    5. Crea usuario en BD con rol por defecto
    6. Envía email de verificación (opcional)
    """
    
    def __init__(self, REPOSITORIO: RepositorioAutenticacion):
        """
        Inicializa el caso de uso
        
        Args:
            REPOSITORIO: Repositorio de autenticación
        """
        self._REPOSITORIO = REPOSITORIO
    
    async def EJECUTAR(
        self, 
        EMAIL: str, 
        NOMBRE_USUARIO: str, 
        CONTRASENA: str
    ) -> Dict:
        """
        Ejecuta el caso de uso de registro
        
        Args:
            EMAIL: Email del nuevo usuario
            NOMBRE_USUARIO: Nombre de usuario único
            CONTRASENA: Contraseña en texto plano
            
        Returns:
            Diccionario con resultado:
            {
                "EXITO": bool,
                "USUARIO_ID": int (si exitoso),
                "ERROR": str (si falla),
                "CODIGO": int
            }
        """
        print(f"📝 Registrando nuevo usuario: {EMAIL}")
        
        try:
            # PASO 1: Validar que el email no exista
            USUARIO_EXISTENTE = await self._REPOSITORIO.OBTENER_POR_EMAIL(EMAIL)
            
            if USUARIO_EXISTENTE:
                print(f"❌ Email ya registrado: {EMAIL}")
                return {
                    "EXITO": False,
                    "ERROR": "Este email ya está registrado",
                    "CODIGO": 409
                }
            
            # PASO 2: Validar que el nombre de usuario no exista
            USUARIO_EXISTENTE = await self._REPOSITORIO.OBTENER_POR_NOMBRE_USUARIO(NOMBRE_USUARIO)
            
            if USUARIO_EXISTENTE:
                print(f"❌ Nombre de usuario ya existe: {NOMBRE_USUARIO}")
                return {
                    "EXITO": False,
                    "ERROR": "Este nombre de usuario ya está en uso",
                    "CODIGO": 409
                }
            
            # PASO 3: Hashear contraseña con bcrypt
            SAL = bcrypt.gensalt(rounds=12)
            CONTRASENA_HASH = bcrypt.hashpw(CONTRASENA.encode('utf-8'), SAL)
            
            # PASO 4: Generar huella del dispositivo
            HUELLA_DISPOSITIVO = GeneradorHuella.OBTENER_HUELLA()
            
            # PASO 5: Crear usuario en BD
            NUEVO_USUARIO = await self._REPOSITORIO.CREAR_USUARIO(
                EMAIL=EMAIL,
                NOMBRE_USUARIO=NOMBRE_USUARIO,
                CONTRASENA_HASH=CONTRASENA_HASH.decode('utf-8'),
                HUELLA_DISPOSITIVO=HUELLA_DISPOSITIVO
            )
            
            # PASO 6: Asignar rol por defecto (usuario)
            await self._REPOSITORIO.ASIGNAR_ROL(NUEVO_USUARIO.ID, ROLES.USUARIO)
            
            print(f"✅ Usuario registrado exitosamente: {EMAIL} (ID: {NUEVO_USUARIO.ID})")
            
            # PASO 7: Enviar email de verificación (opcional)
            # await self._ENVIAR_EMAIL_VERIFICACION(EMAIL)
            
            return {
                "EXITO": True,
                "USUARIO_ID": NUEVO_USUARIO.ID,
                "EMAIL": EMAIL,
                "CODIGO": 201
            }
        
        except Exception as ERROR:
            print(f"❌ Error al registrar usuario: {ERROR}")
            return {
                "EXITO": False,
                "ERROR": "Error interno del servidor",
                "CODIGO": 500
            }
    
    async def _ENVIAR_EMAIL_VERIFICACION(self, EMAIL: str):
        """
        Envía email de verificación al usuario
        (Implementar según servicio de email)
        """
        # TODO: Implementar envío de email
        print(f"📧 Email de verificación enviado a: {EMAIL}")