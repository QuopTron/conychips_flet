from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Table,
    ForeignKey,
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import os
import shutil
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE = declarative_base()

TABLA_USUARIO_ROLES = Table(
    "USUARIO_ROLES",
    BASE.metadata,
    Column("USUARIO_ID", Integer, ForeignKey("USUARIOS.ID")),
    Column("ROL_ID", Integer, ForeignKey("ROLES.ID")),
)


class MODELO_USUARIO(BASE):

    __tablename__ = "USUARIOS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    EMAIL = Column(String(255), unique=True, nullable=False, index=True)
    NOMBRE_USUARIO = Column(String(100), unique=True, nullable=False)
    CONTRASENA_HASH = Column(String(255), nullable=False)
    HUELLA_DISPOSITIVO = Column(String(255), nullable=False)
    FOTO_PERFIL = Column(String(500), nullable=True)  # Ruta de imagen
    ACTIVO = Column(Boolean, default=True)
    VERIFICADO = Column(Boolean, default=False)
    TOKEN_RESET = Column(String(255), nullable=True)
    TOKEN_RESET_EXPIRA = Column(DateTime, nullable=True)
    FECHA_CREACION = Column(DateTime, default=datetime.utcnow)
    ULTIMA_CONEXION = Column(DateTime, nullable=True)

    ROLES = relationship(
        "MODELO_ROL", secondary=TABLA_USUARIO_ROLES, back_populates="USUARIOS"
    )
    SESIONES = relationship(
        "MODELO_SESION", back_populates="USUARIO", cascade="all, delete-orphan"
    )


class MODELO_ROL(BASE):

    __tablename__ = "ROLES"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    NOMBRE = Column(String(50), unique=True, nullable=False)
    DESCRIPCION = Column(String(255))

    USUARIOS = relationship(
        "MODELO_USUARIO", secondary=TABLA_USUARIO_ROLES, back_populates="ROLES"
    )


class MODELO_SESION(BASE):

    __tablename__ = "SESIONES"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    USUARIO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    REFRESH_TOKEN = Column(String(500), unique=True, nullable=False)
    HUELLA_DISPOSITIVO = Column(String(255), nullable=False)
    IP = Column(String(45))
    NAVEGADOR = Column(String(255))
    ACTIVA = Column(Boolean, default=True)
    FECHA_CREACION = Column(DateTime, default=datetime.utcnow)
    FECHA_EXPIRACION = Column(DateTime, nullable=False)

    USUARIO = relationship("MODELO_USUARIO", back_populates="SESIONES")


class MODELO_PRODUCTO(BASE):
    __tablename__ = "PRODUCTOS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    NOMBRE = Column(String(150), unique=True, nullable=False)
    DESCRIPCION = Column(String(500))
    PRECIO = Column(Integer, nullable=False, default=0)  # En Bs
    IMAGEN = Column(String(500), nullable=True)  # Ruta o URL de imagen
    DISPONIBLE = Column(Boolean, default=True)
    FECHA_CREACION = Column(DateTime, default=datetime.utcnow)

    SUCURSALES = relationship(
        "MODELO_SUCURSAL", secondary="PRODUCTO_SUCURSAL", back_populates="PRODUCTOS"
    )
    EXTRAS = relationship(
        "MODELO_EXTRA", secondary="PRODUCTO_EXTRA", back_populates="PRODUCTOS"
    )


class MODELO_SUCURSAL(BASE):
    __tablename__ = "SUCURSALES"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    NOMBRE = Column(String(100), unique=True, nullable=False)
    DIRECCION = Column(String(255))
    ACTIVA = Column(Boolean, default=True)
    FECHA_CREACION = Column(DateTime, default=datetime.utcnow)

    PRODUCTOS = relationship(
        "MODELO_PRODUCTO", secondary="PRODUCTO_SUCURSAL", back_populates="SUCURSALES"
    )
    PEDIDOS = relationship("MODELO_PEDIDO", back_populates="SUCURSAL")
    CAJAS = relationship("MODELO_CAJA", back_populates="SUCURSAL")


TABLA_PRODUCTO_SUCURSAL = Table(
    "PRODUCTO_SUCURSAL",
    BASE.metadata,
    Column("PRODUCTO_ID", Integer, ForeignKey("PRODUCTOS.ID")),
    Column("SUCURSAL_ID", Integer, ForeignKey("SUCURSALES.ID")),
)


class MODELO_EXTRA(BASE):
    __tablename__ = "EXTRAS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    NOMBRE = Column(String(100), nullable=False)
    DESCRIPCION = Column(String(255))
    PRECIO_ADICIONAL = Column(Integer, default=0)  # En Bs
    ACTIVO = Column(Boolean, default=True)
    FECHA_CREACION = Column(DateTime, default=datetime.utcnow)

    PRODUCTOS = relationship(
        "MODELO_PRODUCTO", secondary="PRODUCTO_EXTRA", back_populates="EXTRAS"
    )


TABLA_PRODUCTO_EXTRA = Table(
    "PRODUCTO_EXTRA",
    BASE.metadata,
    Column("PRODUCTO_ID", Integer, ForeignKey("PRODUCTOS.ID")),
    Column("EXTRA_ID", Integer, ForeignKey("EXTRAS.ID")),
)


class MODELO_PEDIDO(BASE):
    __tablename__ = "PEDIDOS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    CLIENTE_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    SUCURSAL_ID = Column(Integer, ForeignKey("SUCURSALES.ID"), nullable=False)
    TIPO = Column(String(20), default="delivery")  # 'delivery' o 'presencial'
    ESTADO = Column(
        String(50), default="pendiente"
    )  # pendiente, confirmado, preparado, entregado
    MONTO_TOTAL = Column(Integer, nullable=False)
    QR_PAGO = Column(String(1000), nullable=True)
    NOTAS = Column(String(500), nullable=True)
    FECHA_CREACION = Column(DateTime, default=datetime.utcnow)
    FECHA_CONFIRMACION = Column(DateTime, nullable=True)

    CLIENTE = relationship("MODELO_USUARIO")
    SUCURSAL = relationship("MODELO_SUCURSAL", back_populates="PEDIDOS")
    DETALLES = relationship(
        "MODELO_DETALLE_PEDIDO", back_populates="PEDIDO", cascade="all, delete-orphan"
    )


class MODELO_DETALLE_PEDIDO(BASE):
    __tablename__ = "DETALLE_PEDIDO"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    PEDIDO_ID = Column(Integer, ForeignKey("PEDIDOS.ID"), nullable=False)
    PRODUCTO_ID = Column(Integer, ForeignKey("PRODUCTOS.ID"), nullable=False)
    CANTIDAD = Column(Integer, default=1)
    PRECIO_UNITARIO = Column(Integer, nullable=False)
    EXTRAS_SELECCIONADOS = Column(String(1000), nullable=True)  # JSON o lista de IDs

    PEDIDO = relationship("MODELO_PEDIDO", back_populates="DETALLES")
    PRODUCTO = relationship("MODELO_PRODUCTO")


class MODELO_ASISTENCIA(BASE):
    __tablename__ = "ASISTENCIAS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    USUARIO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    FECHA = Column(DateTime, default=datetime.utcnow)
    ASISTIO = Column(Boolean, default=True)
    NOTAS = Column(String(255), nullable=True)

    USUARIO = relationship("MODELO_USUARIO")


class MODELO_REPORTE_LIMPIEZA(BASE):
    __tablename__ = "REPORTES_LIMPIEZA"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    USUARIO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    SUCURSAL_ID = Column(Integer, ForeignKey("SUCURSALES.ID"), nullable=False)
    FECHA = Column(DateTime, default=datetime.utcnow)
    FOTO_LOCAL = Column(String(500), nullable=True)  # Ruta de imagen
    NOTAS = Column(String(500), nullable=True)

    USUARIO = relationship("MODELO_USUARIO")
    SUCURSAL = relationship("MODELO_SUCURSAL")


class MODELO_CAJA(BASE):
    __tablename__ = "CAJAS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    USUARIO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    SUCURSAL_ID = Column(Integer, ForeignKey("SUCURSALES.ID"), nullable=False)
    FECHA_APERTURA = Column(DateTime, default=datetime.utcnow)
    FECHA_CIERRE = Column(DateTime, nullable=True)
    MONTO_INICIAL = Column(Integer, default=0)
    MONTO_FINAL = Column(Integer, nullable=True)
    GANANCIAS = Column(Integer, default=0)
    ACTIVA = Column(Boolean, default=True)

    USUARIO = relationship("MODELO_USUARIO")
    SUCURSAL = relationship("MODELO_SUCURSAL", back_populates="CAJAS")


class MODELO_OFERTA(BASE):
    __tablename__ = "OFERTAS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    PRODUCTO_ID = Column(Integer, ForeignKey("PRODUCTOS.ID"), nullable=False)
    DESCUENTO_PORCENTAJE = Column(Integer, nullable=False)  # 0-100
    FECHA_INICIO = Column(DateTime, default=datetime.utcnow)
    FECHA_FIN = Column(DateTime, nullable=True)
    ACTIVA = Column(Boolean, default=True)

    PRODUCTO = relationship("MODELO_PRODUCTO")


class MODELO_HORARIO(BASE):
    __tablename__ = "HORARIOS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    USUARIO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    DIA_SEMANA = Column(String(10), nullable=False)  # 'lunes', 'martes', etc.
    HORA_INICIO = Column(String(5), nullable=False)  # '08:00'
    HORA_FIN = Column(String(5), nullable=False)  # '17:00'
    ACTIVO = Column(Boolean, default=True)

    USUARIO = relationship("MODELO_USUARIO")


def OBTENER_RUTA_BD():
    if os.name == "nt":  # Windows
        appdata = os.getenv("APPDATA") or os.path.expanduser("~")
        return os.path.join(appdata, "AppSegura", "app_segura.db")
    elif os.name == "posix":  # Linux/Mac
        return os.path.join(os.path.expanduser("~"), ".app_segura", "app_segura.db")
    else:  # Web/Móvil
        return os.path.abspath("app_segura.db")


RUTA_BD = OBTENER_RUTA_BD()
dir_name = os.path.dirname(RUTA_BD)
if dir_name:
    try:
        os.makedirs(dir_name, exist_ok=True)
    except Exception as e:
        logger.warning("No se pudo crear el directorio de la BD %s: %s", dir_name, e)

MOTOR = create_engine(
    f"sqlite:///{RUTA_BD}", echo=False, connect_args={"check_same_thread": False}
)
SESION_FACTORY = sessionmaker(bind=MOTOR)


async def INICIALIZAR_BASE_DATOS():

    try:
        from sqlalchemy import text

        with MOTOR.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(USUARIOS)"))
            columns = [row[1] for row in result.fetchall()]

            if "FOTO_PERFIL" not in columns:
                conn.execute(
                    text("ALTER TABLE USUARIOS ADD COLUMN FOTO_PERFIL VARCHAR(500)")
                )
                logger.info("Columna FOTO_PERFIL añadida a USUARIOS")
            if "ACTIVO" not in columns:
                conn.execute(
                    text("ALTER TABLE USUARIOS ADD COLUMN ACTIVO BOOLEAN DEFAULT 1")
                )
                logger.info("Columna ACTIVO añadida a USUARIOS")
            if "VERIFICADO" not in columns:
                conn.execute(
                    text("ALTER TABLE USUARIOS ADD COLUMN VERIFICADO BOOLEAN DEFAULT 0")
                )
                logger.info("Columna VERIFICADO añadida a USUARIOS")
            if "TOKEN_RESET" not in columns:
                conn.execute(
                    text("ALTER TABLE USUARIOS ADD COLUMN TOKEN_RESET VARCHAR(255)")
                )
                logger.info("Columna TOKEN_RESET añadida a USUARIOS")
            if "TOKEN_RESET_EXPIRA" not in columns:
                conn.execute(
                    text("ALTER TABLE USUARIOS ADD COLUMN TOKEN_RESET_EXPIRA DATETIME")
                )
                logger.info("Columna TOKEN_RESET_EXPIRA añadida a USUARIOS")
            if "ULTIMA_CONEXION" not in columns:
                conn.execute(
                    text("ALTER TABLE USUARIOS ADD COLUMN ULTIMA_CONEXION DATETIME")
                )
                logger.info("Columna ULTIMA_CONEXION añadida a USUARIOS")

            result = conn.execute(text("PRAGMA table_info(PRODUCTOS)"))
            columns = [row[1] for row in result.fetchall()]
            if "IMAGEN" not in columns:
                conn.execute(
                    text("ALTER TABLE PRODUCTOS ADD COLUMN IMAGEN VARCHAR(500)")
                )
                logger.info("Columna IMAGEN añadida a PRODUCTOS")
            if "TIPO" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE PRODUCTOS ADD COLUMN TIPO VARCHAR(50) DEFAULT 'gaseosa'"
                    )
                )
                logger.info("Columna TIPO añadida a PRODUCTOS")

            result = conn.execute(text("PRAGMA table_info(PEDIDOS)"))
            columns = [row[1] for row in result.fetchall()]

            if "SUCURSAL_ID" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE PEDIDOS ADD COLUMN SUCURSAL_ID INTEGER REFERENCES SUCURSALES(ID)"
                    )
                )
                logger.info("Columna SUCURSAL_ID añadida a PEDIDOS")
            if "TIPO" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE PEDIDOS ADD COLUMN TIPO VARCHAR(20) DEFAULT 'delivery'"
                    )
                )
                logger.info("Columna TIPO añadida a PEDIDOS")
            if "MONTO_TOTAL" not in columns:
                conn.execute(text("ALTER TABLE PEDIDOS ADD COLUMN MONTO_TOTAL INTEGER"))
                logger.info("Columna MONTO_TOTAL añadida a PEDIDOS")
            if "QR_PAGO" not in columns:
                conn.execute(
                    text("ALTER TABLE PEDIDOS ADD COLUMN QR_PAGO VARCHAR(1000)")
                )
                logger.info("Columna QR_PAGO añadida a PEDIDOS")
            if "NOTAS" not in columns:
                conn.execute(text("ALTER TABLE PEDIDOS ADD COLUMN NOTAS VARCHAR(500)"))
                logger.info("Columna NOTAS añadida a PEDIDOS")
            if "FECHA_CONFIRMACION" not in columns:
                conn.execute(
                    text("ALTER TABLE PEDIDOS ADD COLUMN FECHA_CONFIRMACION DATETIME")
                )
                logger.info("Columna FECHA_CONFIRMACION añadida a PEDIDOS")

            conn.commit()
    except Exception as e:
        logger.exception("Error en migración: %s", e)

    BASE.metadata.create_all(MOTOR)
    try:
        if os.path.exists(RUTA_BD):
            respaldo = f"{RUTA_BD}.backup.{int(time.time())}"
            shutil.copy2(RUTA_BD, respaldo)
            logger.info("Respaldo de BD creado: %s", respaldo)
    except Exception as e:
        logger.warning("Fallo al crear respaldo de BD: %s", e)

    with SESION_FACTORY() as sesion:
        try:
            usuarios = sesion.query(MODELO_USUARIO).all()
            if usuarios:
                for u in usuarios:
                    sesion.delete(u)
                sesion.commit()
                logger.info("Usuarios eliminados: %d", len(usuarios))
            else:
                logger.info("No había usuarios para eliminar.")
        except Exception as e:
            sesion.rollback()
            logger.exception("Error al eliminar usuarios: %s", e)
        from core.Constantes import ROLES

        ROLES_DEFECTO = [
            MODELO_ROL(
                NOMBRE=ROLES.SUPER_ADMIN, DESCRIPCION="Control total del sistema"
            ),
            MODELO_ROL(NOMBRE=ROLES.ADMIN, DESCRIPCION="Administrador del sistema"),
            MODELO_ROL(
                NOMBRE=ROLES.ATENCION, DESCRIPCION="Personal de atención al cliente"
            ),
            MODELO_ROL(NOMBRE=ROLES.COCINERO, DESCRIPCION="Personal de cocina"),
            MODELO_ROL(NOMBRE=ROLES.LIMPIEZA, DESCRIPCION="Personal de limpieza"),
            MODELO_ROL(
                NOMBRE=ROLES.CLIENTE, DESCRIPCION="Cliente / usuario del servicio"
            ),
        ]

        for rol in ROLES_DEFECTO:
            existe = sesion.query(MODELO_ROL).filter_by(NOMBRE=rol.NOMBRE).first()
            if not existe:
                sesion.add(rol)

        sesion.commit()

        try:
            import bcrypt

            DOMAIN = "conychips.com"

            DEFAULT_PASSWORDS = {
                ROLES.SUPER_ADMIN: "Super123.",
                ROLES.ADMIN: "Admin123.",
                ROLES.ATENCION: "Atencion123.",
                ROLES.COCINERO: "Cocinero123.",
                ROLES.LIMPIEZA: "Limpieza123.",
                ROLES.CLIENTE: "Cliente123.",
            }

            def crear_usuario_si_no_existe_short(nombre, rol_nombre):
                email = f"{nombre}@{DOMAIN}"
                existe_u = sesion.query(MODELO_USUARIO).filter_by(EMAIL=email).first()
                if existe_u:
                    return
                password = DEFAULT_PASSWORDS.get(rol_nombre, "PasswordWorking...123.")
                salt = bcrypt.gensalt(rounds=12)
                hash_pw = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
                usuario = MODELO_USUARIO(
                    EMAIL=email,
                    NOMBRE_USUARIO=nombre,
                    CONTRASENA_HASH=hash_pw,
                    HUELLA_DISPOSITIVO="seed-device",
                )
                rol_obj = sesion.query(MODELO_ROL).filter_by(NOMBRE=rol_nombre).first()
                if rol_obj:
                    usuario.ROLES.append(rol_obj)
                sesion.add(usuario)
                sesion.commit()

            crear_usuario_si_no_existe_short("super", ROLES.SUPER_ADMIN)
            crear_usuario_si_no_existe_short("admin", ROLES.ADMIN)
            crear_usuario_si_no_existe_short("atencion", ROLES.ATENCION)
            crear_usuario_si_no_existe_short("cocinero", ROLES.COCINERO)
            crear_usuario_si_no_existe_short("limpieza", ROLES.LIMPIEZA)
            crear_usuario_si_no_existe_short("cliente", ROLES.CLIENTE)
        except Exception as e:
            logger.exception("Error creando usuarios seed: %s", e)

        try:
            productos_defecto = [
                MODELO_PRODUCTO(
                    NOMBRE="Hamburguesa Clásica",
                    DESCRIPCION="Carne, queso, lechuga, tomate",
                    PRECIO=599,
                    IMAGEN="assets/hamburguesa.jpg",
                ),
                MODELO_PRODUCTO(
                    NOMBRE="Papas Fritas",
                    DESCRIPCION="Papas crujientes",
                    PRECIO=199,
                    IMAGEN="assets/papas.jpg",
                ),
                MODELO_PRODUCTO(
                    NOMBRE="Bebida Gaseosa",
                    DESCRIPCION="350ml",
                    PRECIO=149,
                    IMAGEN="assets/bebida.jpg",
                ),
            ]
            for prod in productos_defecto:
                existe_p = (
                    sesion.query(MODELO_PRODUCTO).filter_by(NOMBRE=prod.NOMBRE).first()
                )
                if not existe_p:
                    sesion.add(prod)
            sesion.commit()
        except Exception as e:
            logger.exception("Error creando productos seed: %s", e)

        try:
            sucursales_defecto = [
                MODELO_SUCURSAL(
                    NOMBRE="Sucursal Centro", DIRECCION="Calle Principal 123"
                ),
                MODELO_SUCURSAL(NOMBRE="Sucursal Norte", DIRECCION="Av. Norte 456"),
            ]
            for suc in sucursales_defecto:
                existe_s = (
                    sesion.query(MODELO_SUCURSAL).filter_by(NOMBRE=suc.NOMBRE).first()
                )
                if not existe_s:
                    sesion.add(suc)
            sesion.commit()
        except Exception as e:
            logger.exception("Error creando sucursales seed: %s", e)

        try:
            productos = sesion.query(MODELO_PRODUCTO).all()
            sucursales = sesion.query(MODELO_SUCURSAL).all()
            for prod in productos:
                for suc in sucursales:
                    if suc not in prod.SUCURSALES:
                        prod.SUCURSALES.append(suc)
            sesion.commit()
        except Exception as e:
            logger.exception("Error asignando productos a sucursales: %s", e)

        try:
            extras_defecto = [
                MODELO_EXTRA(
                    NOMBRE="Salsa Extra",
                    DESCRIPCION="Salsa adicional",
                    PRECIO_ADICIONAL=50,
                ),
                MODELO_EXTRA(
                    NOMBRE="Queso Extra",
                    DESCRIPCION="Queso adicional",
                    PRECIO_ADICIONAL=100,
                ),
            ]
            for ext in extras_defecto:
                existe_e = (
                    sesion.query(MODELO_EXTRA).filter_by(NOMBRE=ext.NOMBRE).first()
                )
                if not existe_e:
                    sesion.add(ext)
            sesion.commit()
        except Exception as e:
            logger.exception("Error creando extras seed: %s", e)

    logger.info("Base de datos inicializada correctamente")


def OBTENER_SESION():

    return SESION_FACTORY()
