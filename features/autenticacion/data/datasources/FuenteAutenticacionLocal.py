from typing import Optional, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session, joinedload
from core.base_datos.ConfiguracionBD import (
    MODELO_USUARIO,
    MODELO_ROL,
    MODELO_SESION,
    OBTENER_SESION,
)
from core.Constantes import EXPIRACION_REFRESH_TOKEN

class FuenteAutenticacionLocal:

    def __init__(self):

        pass

    def _OBTENER_SESION_BD(self) -> Session:

        return OBTENER_SESION()

    async def OBTENER_USUARIO_POR_EMAIL(self, EMAIL: str) -> Optional[MODELO_USUARIO]:

        SESION = self._OBTENER_SESION_BD()

        try:
            USUARIO = (
                SESION.query(MODELO_USUARIO)
                .options(joinedload(MODELO_USUARIO.ROLES))
                .filter_by(EMAIL=EMAIL)
                .first()
            )

            return USUARIO
        finally:
            SESION.close()

    async def OBTENER_USUARIO_POR_ID(self, USUARIO_ID: int) -> Optional[MODELO_USUARIO]:

        SESION = self._OBTENER_SESION_BD()

        try:
            USUARIO = (
                SESION.query(MODELO_USUARIO)
                .options(joinedload(MODELO_USUARIO.ROLES))
                .filter_by(ID=USUARIO_ID)
                .first()
            )

            return USUARIO
        finally:
            SESION.close()

    async def OBTENER_USUARIO_POR_NOMBRE(
        self, NOMBRE_USUARIO: str
    ) -> Optional[MODELO_USUARIO]:

        SESION = self._OBTENER_SESION_BD()

        try:
            USUARIO = (
                SESION.query(MODELO_USUARIO)
                .filter_by(NOMBRE_USUARIO=NOMBRE_USUARIO)
                .first()
            )

            return USUARIO
        finally:
            SESION.close()

    async def CREAR_USUARIO(
        self,
        EMAIL: str,
        NOMBRE_USUARIO: str,
        CONTRASENA_HASH: str,
        HUELLA_DISPOSITIVO: str,
    ) -> MODELO_USUARIO:

        SESION = self._OBTENER_SESION_BD()

        try:
            NUEVO_USUARIO = MODELO_USUARIO(
                EMAIL=EMAIL,
                NOMBRE_USUARIO=NOMBRE_USUARIO,
                CONTRASENA_HASH=CONTRASENA_HASH,
                HUELLA_DISPOSITIVO=HUELLA_DISPOSITIVO,
                ACTIVO=True,
                VERIFICADO=False,
                FECHA_CREACION=datetime.now(timezone.utc),
            )

            SESION.add(NUEVO_USUARIO)
            SESION.commit()
            SESION.refresh(NUEVO_USUARIO)

            print(f" Usuario creado en BD: {EMAIL} (ID: {NUEVO_USUARIO.ID})")

            return NUEVO_USUARIO
        except Exception as ERROR:
            SESION.rollback()
            print(f" Error al crear usuario: {ERROR}")
            raise
        finally:
            SESION.close()

    async def ACTUALIZAR_ULTIMA_CONEXION(self, USUARIO_ID: int):

        SESION = self._OBTENER_SESION_BD()

        try:
            USUARIO = SESION.query(MODELO_USUARIO).filter_by(ID=USUARIO_ID).first()

            if USUARIO:
                USUARIO.ULTIMA_CONEXION = datetime.now(timezone.utc)
                SESION.commit()
                print(f" Última conexión actualizada para usuario {USUARIO_ID}")
        except Exception as ERROR:
            SESION.rollback()
            print(f" Error al actualizar última conexión: {ERROR}")
        finally:
            SESION.close()

    async def CREAR_SESION(
        self,
        USUARIO_ID: int,
        REFRESH_TOKEN: str,
        HUELLA_DISPOSITIVO: str,
        IP: Optional[str] = None,
        NAVEGADOR: Optional[str] = None,
    ):

        SESION = self._OBTENER_SESION_BD()

        try:
            FECHA_EXPIRACION = datetime.now(timezone.utc) + timedelta(
                seconds=EXPIRACION_REFRESH_TOKEN
            )

            NUEVA_SESION = MODELO_SESION(
                USUARIO_ID=USUARIO_ID,
                REFRESH_TOKEN=REFRESH_TOKEN,
                HUELLA_DISPOSITIVO=HUELLA_DISPOSITIVO,
                IP=IP,
                NAVEGADOR=NAVEGADOR,
                ACTIVA=True,
                FECHA_CREACION=datetime.now(timezone.utc),
                FECHA_EXPIRACION=FECHA_EXPIRACION,
            )

            SESION.add(NUEVA_SESION)
            SESION.commit()

            print(f" Sesión creada para usuario {USUARIO_ID}")
        except Exception as ERROR:
            SESION.rollback()
            print(f" Error al crear sesión: {ERROR}")
            raise
        finally:
            SESION.close()

    async def VERIFICAR_SESION_ACTIVA(
        self, USUARIO_ID: int, REFRESH_TOKEN: str
    ) -> bool:

        SESION = self._OBTENER_SESION_BD()

        try:
            SESION_BD = (
                SESION.query(MODELO_SESION)
                .filter_by(
                    USUARIO_ID=USUARIO_ID, REFRESH_TOKEN=REFRESH_TOKEN, ACTIVA=True
                )
                .first()
            )

            if not SESION_BD:
                return False

            if SESION_BD.FECHA_EXPIRACION < datetime.now(timezone.utc):
                print(f" Sesión expirada para usuario {USUARIO_ID}")
                return False

            return True
        finally:
            SESION.close()

    async def CERRAR_SESION(self, REFRESH_TOKEN: str):

        SESION = self._OBTENER_SESION_BD()

        try:
            SESION_BD = (
                SESION.query(MODELO_SESION)
                .filter_by(REFRESH_TOKEN=REFRESH_TOKEN)
                .first()
            )

            if SESION_BD:
                SESION_BD.ACTIVA = False
                SESION.commit()
                print(f" Sesión cerrada para usuario {SESION_BD.USUARIO_ID}")
        except Exception as ERROR:
            SESION.rollback()
            print(f" Error al cerrar sesión: {ERROR}")
        finally:
            SESION.close()

    async def ASIGNAR_ROL_A_USUARIO(self, USUARIO_ID: int, NOMBRE_ROL: str):

        SESION = self._OBTENER_SESION_BD()

        try:
            USUARIO = SESION.query(MODELO_USUARIO).filter_by(ID=USUARIO_ID).first()
            ROL = SESION.query(MODELO_ROL).filter_by(NOMBRE=NOMBRE_ROL).first()

            if USUARIO and ROL:
                if ROL not in USUARIO.ROLES:
                    USUARIO.ROLES.append(ROL)
                    SESION.commit()
                    print(f" Rol '{NOMBRE_ROL}' asignado a usuario {USUARIO_ID}")
                else:
                    print(f" Usuario {USUARIO_ID} ya tiene el rol '{NOMBRE_ROL}'")
            else:
                print(f" Usuario o rol no encontrado")
        except Exception as ERROR:
            SESION.rollback()
            print(f" Error al asignar rol: {ERROR}")
        finally:
            SESION.close()

    async def REMOVER_ROL_DE_USUARIO(self, USUARIO_ID: int, NOMBRE_ROL: str):

        SESION = self._OBTENER_SESION_BD()

        try:
            USUARIO = SESION.query(MODELO_USUARIO).filter_by(ID=USUARIO_ID).first()
            ROL = SESION.query(MODELO_ROL).filter_by(NOMBRE=NOMBRE_ROL).first()

            if USUARIO and ROL:
                if ROL in USUARIO.ROLES:
                    USUARIO.ROLES.remove(ROL)
                    SESION.commit()
                    print(f" Rol '{NOMBRE_ROL}' removido de usuario {USUARIO_ID}")
        except Exception as ERROR:
            SESION.rollback()
            print(f" Error al remover rol: {ERROR}")
        finally:
            SESION.close()

    async def OBTENER_SESIONES_ACTIVAS(self, USUARIO_ID: int) -> List[MODELO_SESION]:

        SESION = self._OBTENER_SESION_BD()

        try:
            SESIONES = (
                SESION.query(MODELO_SESION)
                .filter_by(USUARIO_ID=USUARIO_ID, ACTIVA=True)
                .filter(MODELO_SESION.FECHA_EXPIRACION > datetime.now(timezone.utc))
                .all()
            )

            return SESIONES
        finally:
            SESION.close()

    async def ACTUALIZAR_TOKEN_RESET(
        self, USUARIO_ID: int, TOKEN: str, EXPIRA: datetime
    ):
        SESION = self._OBTENER_SESION_BD()
        try:
            USUARIO = SESION.query(MODELO_USUARIO).filter_by(ID=USUARIO_ID).first()
            if USUARIO:
                USUARIO.TOKEN_RESET = TOKEN
                USUARIO.TOKEN_RESET_EXPIRA = EXPIRA
                SESION.commit()
        finally:
            SESION.close()

    async def OBTENER_USUARIO_POR_TOKEN_RESET(
        self, TOKEN: str
    ) -> Optional[MODELO_USUARIO]:
        SESION = self._OBTENER_SESION_BD()
        try:
            USUARIO = SESION.query(MODELO_USUARIO).filter_by(TOKEN_RESET=TOKEN).first()
            return USUARIO
        finally:
            SESION.close()

    async def ACTUALIZAR_CONTRASENA(self, USUARIO_ID: int, NUEVA_CONTRASENA_HASH: str):
        SESION = self._OBTENER_SESION_BD()
        try:
            USUARIO = SESION.query(MODELO_USUARIO).filter_by(ID=USUARIO_ID).first()
            if USUARIO:
                USUARIO.CONTRASENA_HASH = NUEVA_CONTRASENA_HASH
                SESION.commit()
        finally:
            SESION.close()

    async def LIMPIAR_TOKEN_RESET(self, USUARIO_ID: int):
        SESION = self._OBTENER_SESION_BD()
        try:
            USUARIO = SESION.query(MODELO_USUARIO).filter_by(ID=USUARIO_ID).first()
            if USUARIO:
                USUARIO.TOKEN_RESET = None
                USUARIO.TOKEN_RESET_EXPIRA = None
                SESION.commit()
        finally:
            SESION.close()

    async def VERIFICAR_EMAIL(self, USUARIO_ID: int):
        SESION = self._OBTENER_SESION_BD()
        try:
            USUARIO = SESION.query(MODELO_USUARIO).filter_by(ID=USUARIO_ID).first()
            if USUARIO:
                USUARIO.VERIFICADO = True
                SESION.commit()
        finally:
            SESION.close()
