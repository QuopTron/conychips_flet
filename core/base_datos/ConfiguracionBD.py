from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Table,
    ForeignKey,
    event,
    pool,
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session
from datetime import datetime
import os
import shutil
import time
import logging
from dotenv import load_dotenv

load_dotenv()

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
    EMAIL = Column(String(100), unique=True, nullable=False, index=True)
    NOMBRE_USUARIO = Column(String(50), unique=True, nullable=False)
    CONTRASENA_HASH = Column(String(100), nullable=False)  # bcrypt hash
    HUELLA_DISPOSITIVO = Column(String(64), nullable=False)  # SHA256 hash
    FOTO_PERFIL = Column(String(300), nullable=True)  # Ruta de imagen
    ACTIVO = Column(Boolean, default=True)
    VERIFICADO = Column(Boolean, default=False)
    TOKEN_RESET = Column(String(64), nullable=True)  # Token UUID
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
    DESCRIPCION = Column(String(200), nullable=True)
    PERMISOS = Column(String(2000), nullable=True)  # JSON de permisos
    ACTIVO = Column(Boolean, default=True)
    FECHA_CREACION = Column(DateTime, default=datetime.utcnow)

    USUARIOS = relationship(
        "MODELO_USUARIO", secondary=TABLA_USUARIO_ROLES, back_populates="ROLES"
    )


class MODELO_SESION(BASE):

    __tablename__ = "SESIONES"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    USUARIO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    REFRESH_TOKEN = Column(String, unique=True, nullable=False)  # JWT token RS256 (TEXT en PostgreSQL)
    HUELLA_DISPOSITIVO = Column(String(64), nullable=False)  # SHA256 hash
    IP = Column(String(45), nullable=True)  # IPv4/IPv6
    NAVEGADOR = Column(String(150), nullable=True)
    ACTIVA = Column(Boolean, default=True)
    FECHA_CREACION = Column(DateTime, default=datetime.utcnow)
    FECHA_EXPIRACION = Column(DateTime, nullable=False)

    USUARIO = relationship("MODELO_USUARIO", back_populates="SESIONES")


class MODELO_PRODUCTO(BASE):
    __tablename__ = "PRODUCTOS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    NOMBRE = Column(String(100), unique=True, nullable=False)
    DESCRIPCION = Column(String(300), nullable=True)
    PRECIO = Column(Integer, nullable=False, default=0)  # En Bs
    IMAGEN = Column(String(300), nullable=True)  # Ruta o URL de imagen
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
    TIPO = Column(String(15), default="delivery")  # 'delivery' o 'presencial'
    ESTADO = Column(
        String(30), default="pendiente"
    )  # pendiente, confirmado, preparado, entregado
    MONTO_TOTAL = Column(Integer, nullable=False)
    QR_PAGO = Column(String(300), nullable=True)  # Ruta imagen QR
    NOTAS = Column(String(300), nullable=True)
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
    EXTRAS_SELECCIONADOS = Column(String(500), nullable=True)  # JSON array de IDs

    PEDIDO = relationship("MODELO_PEDIDO", back_populates="DETALLES")
    PRODUCTO = relationship("MODELO_PRODUCTO")


class MODELO_ASISTENCIA(BASE):  # OPCIONAL
    __tablename__ = "ASISTENCIAS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    USUARIO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    FECHA = Column(DateTime, default=datetime.utcnow)
    ASISTIO = Column(Boolean, default=True)
    NOTAS = Column(String(200), nullable=True)

    USUARIO = relationship("MODELO_USUARIO")


class MODELO_REPORTE_LIMPIEZA(BASE):  # OPCIONAL
    __tablename__ = "REPORTES_LIMPIEZA"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    USUARIO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    SUCURSAL_ID = Column(Integer, ForeignKey("SUCURSALES.ID"), nullable=False)
    FECHA = Column(DateTime, default=datetime.utcnow)
    FOTO_LOCAL = Column(String(300), nullable=True)  # Ruta de imagen
    NOTAS = Column(String(300), nullable=True)

    USUARIO = relationship("MODELO_USUARIO")
    SUCURSAL = relationship("MODELO_SUCURSAL")


# EGRESOS
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


TABLA_INSUMO_PROVEEDOR = Table(
    "INSUMO_PROVEEDOR",
    BASE.metadata,
    Column("INSUMO_ID", Integer, ForeignKey("INSUMOS.ID")),
    Column("PROVEEDOR_ID", Integer, ForeignKey("PROVEEDORES.ID")),
)


class MODELO_PROVEEDOR(BASE):
    __tablename__ = "PROVEEDORES"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    NOMBRE = Column(String(120), unique=True, nullable=False)
    TELEFONO = Column(String(20))
    EMAIL = Column(String(120))
    DIRECCION = Column(String(200))
    UBICACION = Column(String(200))
    ACTIVO = Column(Boolean, default=True)
    FECHA_CREACION = Column(DateTime, default=datetime.utcnow)

    INSUMOS = relationship(
        "MODELO_INSUMO", secondary=TABLA_INSUMO_PROVEEDOR, back_populates="PROVEEDORES"
    )


class MODELO_INSUMO(BASE):
    __tablename__ = "INSUMOS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    NOMBRE = Column(String(120), unique=True, nullable=False)
    UNIDAD = Column(String(20), default="unidad")
    STOCK = Column(Integer, default=0)
    COSTO_UNITARIO = Column(Integer, default=0)
    SUCURSAL_ID = Column(Integer, ForeignKey("SUCURSALES.ID"), nullable=True)
    ACTIVO = Column(Boolean, default=True)
    FECHA_CREACION = Column(DateTime, default=datetime.utcnow)

    PROVEEDORES = relationship(
        "MODELO_PROVEEDOR", secondary=TABLA_INSUMO_PROVEEDOR, back_populates="INSUMOS"
    )
    SUCURSAL = relationship("MODELO_SUCURSAL")


class MODELO_MOVIMIENTO_INSUMO(BASE):
    __tablename__ = "MOVIMIENTOS_INSUMO"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    INSUMO_ID = Column(Integer, ForeignKey("INSUMOS.ID"), nullable=False)
    USUARIO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    PROVEEDOR_ID = Column(Integer, ForeignKey("PROVEEDORES.ID"), nullable=True)
    TIPO = Column(String(20), default="compra")
    CANTIDAD = Column(Integer, default=0)
    COSTO_TOTAL = Column(Integer, default=0)
    FECHA = Column(DateTime, default=datetime.utcnow)
    NOTAS = Column(String(200))

    INSUMO = relationship("MODELO_INSUMO")
    USUARIO = relationship("MODELO_USUARIO")
    PROVEEDOR = relationship("MODELO_PROVEEDOR")


class MODELO_CAJA_MOVIMIENTO(BASE):
    __tablename__ = "CAJA_MOVIMIENTOS"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    USUARIO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    SUCURSAL_ID = Column(Integer, ForeignKey("SUCURSALES.ID"), nullable=True)
    TIPO = Column(String(20), default="ingreso")
    CATEGORIA = Column(String(60))
    MONTO = Column(Integer, default=0)
    DESCRIPCION = Column(String(200))
    FECHA = Column(DateTime, default=datetime.utcnow)

    USUARIO = relationship("MODELO_USUARIO")
    SUCURSAL = relationship("MODELO_SUCURSAL")


class MODELO_AUDITORIA(BASE):
    __tablename__ = "AUDITORIA"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    USUARIO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    ACCION = Column(String(120), nullable=False)
    ENTIDAD = Column(String(80))
    ENTIDAD_ID = Column(Integer)
    DETALLE = Column(String(300))
    FECHA = Column(DateTime, default=datetime.utcnow)

    USUARIO = relationship("MODELO_USUARIO")


class MODELO_RESENA_ATENCION(BASE):
    __tablename__ = "RESENAS_ATENCION"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    USUARIO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    CALIFICACION = Column(Integer, default=5)
    COMENTARIO = Column(String(300))
    FECHA = Column(DateTime, default=datetime.utcnow)

    USUARIO = relationship("MODELO_USUARIO")


class MODELO_HORARIO(BASE):#ASGINACION DE TIPOS DE HORARIO 
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

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://conychips_user:ConyCh1ps2026!@localhost:5432/conychips_db"
)

MOTOR = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
    poolclass=pool.QueuePool,
    connect_args={
        "connect_timeout": 10,
        "options": "-c timezone=utc"
    }
)

@event.listens_for(MOTOR, "connect")
def RECIBIR_CONEXION(dbapi_conn, connection_record):
    connection_record.info['pid'] = os.getpid()

@event.listens_for(MOTOR, "checkout")
def VERIFICAR_CONEXION(dbapi_conn, connection_record, connection_proxy):
    pid = os.getpid()
    if connection_record.info.get('pid') != pid:
        connection_record.dbapi_connection = connection_proxy.dbapi_connection = None
        raise Exception(
            "Conexión creada en otro proceso, invalidando."
        )

SESION_FACTORY = scoped_session(
    sessionmaker(
        bind=MOTOR,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False
    )
)


def INICIALIZAR_BASE_DATOS():
    """
    Inicializa la base de datos y crea el usuario super admin por defecto.
    """
    # Primero crear todas las tablas
    BASE.metadata.create_all(MOTOR)
    
    logger.info("Base de datos PostgreSQL inicializada - tablas creadas")

    # PostgreSQL no necesita migraciones manuales - SQLAlchemy maneja el schema
    # Las columnas se crean automáticamente desde los modelos
    try:
        from sqlalchemy import text

        # PostgreSQL maneja automáticamente el schema desde los modelos
    except Exception as e:
        logger.exception("Error en migración de columnas: %s", e)

    with SESION_FACTORY() as sesion:
        try:
            import json
            from core.Constantes import ROLES

            roles_defecto = [
                ROLES.INVITADO,
                ROLES.COCINERO,
                ROLES.CLIENTE,
                ROLES.ATENCION,
                ROLES.ADMIN,
                ROLES.LIMPIEZA,
                ROLES.SUPERADMIN,
            ]

            for nombre in roles_defecto:
                existe = sesion.query(MODELO_ROL).filter_by(NOMBRE=nombre).first()
                if not existe:
                    permisos = ["*"] if nombre == ROLES.SUPERADMIN else []
                    rol = MODELO_ROL(
                        NOMBRE=nombre,
                        DESCRIPCION=nombre,
                        PERMISOS=json.dumps(permisos),
                        ACTIVO=True,
                        FECHA_CREACION=datetime.utcnow(),
                    )
                    sesion.add(rol)

            rol_antiguo = sesion.query(MODELO_ROL).filter_by(NOMBRE="super_admin").first()
            rol_super = sesion.query(MODELO_ROL).filter_by(NOMBRE=ROLES.SUPERADMIN).first()
            if rol_antiguo and not rol_super:
                rol_antiguo.NOMBRE = ROLES.SUPERADMIN
                rol_antiguo.DESCRIPCION = ROLES.SUPERADMIN
                rol_antiguo.PERMISOS = json.dumps(["*"])

            sesion.commit()

            import bcrypt

            email_super = "superadmin@conychips.com"
            password_super = "SuperAdmin123."

            existe_super = sesion.query(MODELO_USUARIO).filter_by(EMAIL=email_super).first()

            if not existe_super:
                salt = bcrypt.gensalt(rounds=12)
                hash_pw = bcrypt.hashpw(password_super.encode("utf-8"), salt).decode("utf-8")

                super_admin_usuario = MODELO_USUARIO(
                    EMAIL=email_super,
                    NOMBRE_USUARIO="superadmin",
                    CONTRASENA_HASH=hash_pw,
                    HUELLA_DISPOSITIVO="seed-device-super-admin",
                    ACTIVO=True,
                    VERIFICADO=True,
                    FECHA_CREACION=datetime.utcnow(),
                )

                rol_super = sesion.query(MODELO_ROL).filter_by(NOMBRE=ROLES.SUPERADMIN).first()
                if rol_super:
                    super_admin_usuario.ROLES.append(rol_super)

                sesion.add(super_admin_usuario)
                sesion.commit()

                logger.info("Usuario Super Admin creado: %s", email_super)
                logger.info("Contraseña Super Admin: %s", password_super)
            else:
                logger.info("Usuario Super Admin ya existe")

        except Exception as e:
            sesion.rollback()
            logger.exception("Error creando roles y super admin: %s", e)

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


class MODELO_VOUCHER(BASE):
    __tablename__ = "VOUCHERS"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    PEDIDO_ID = Column(Integer, ForeignKey("PEDIDOS.ID"), nullable=False)
    USUARIO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    IMAGEN_URL = Column(String(500), nullable=False)
    MONTO = Column(Integer, nullable=False)
    METODO_PAGO = Column(String(50), nullable=False)  # "transferencia", "pago_movil", etc
    VALIDADO = Column(Boolean, default=False)
    VALIDADO_POR = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=True)
    FECHA_SUBIDA = Column(DateTime, default=datetime.utcnow)
    FECHA_VALIDACION = Column(DateTime, nullable=True)


class MODELO_REPORTE_LIMPIEZA_FOTO(BASE):
    __tablename__ = "REPORTES_LIMPIEZA_FOTOS"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    REPORTE_ID = Column(Integer, ForeignKey("REPORTES_LIMPIEZA.ID"), nullable=False)
    IMAGEN_URL = Column(String(500), nullable=False)
    DESCRIPCION = Column(String(300), nullable=True)
    FECHA_SUBIDA = Column(DateTime, default=datetime.utcnow)


class MODELO_UBICACION_MOTORIZADO(BASE):
    __tablename__ = "UBICACIONES_MOTORIZADO"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    USUARIO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    PEDIDO_ID = Column(Integer, ForeignKey("PEDIDOS.ID"), nullable=True)
    LATITUD = Column(String(50), nullable=False)
    LONGITUD = Column(String(50), nullable=False)
    ESTADO = Column(String(50), nullable=False)  # "salida", "en_camino", "llegada"
    FECHA = Column(DateTime, default=datetime.utcnow)


class MODELO_MENSAJE_CHAT(BASE):
    __tablename__ = "MENSAJES_CHAT"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    PEDIDO_ID = Column(Integer, ForeignKey("PEDIDOS.ID"), nullable=False)
    USUARIO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    MENSAJE = Column(String(1000), nullable=False)
    TIPO = Column(String(20), default="texto")  # "texto", "imagen", "ubicacion"
    LEIDO = Column(Boolean, default=False)
    FECHA = Column(DateTime, default=datetime.utcnow)


class MODELO_NOTIFICACION(BASE):
    __tablename__ = "NOTIFICACIONES"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    USUARIO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    TITULO = Column(String(100), nullable=False)
    MENSAJE = Column(String(500), nullable=False)
    TIPO = Column(String(50), nullable=False)  # "pedido", "pago", "entrega", "sistema"
    LEIDA = Column(Boolean, default=False)
    DATOS_EXTRA = Column(String(1000), nullable=True)  # JSON con datos adicionales
    FECHA = Column(DateTime, default=datetime.utcnow)


class MODELO_CALIFICACION(BASE):
    __tablename__ = "CALIFICACIONES"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    PEDIDO_ID = Column(Integer, ForeignKey("PEDIDOS.ID"), nullable=False)
    USUARIO_ID = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    CALIFICACION_COMIDA = Column(Integer, nullable=False)  # 1-5 estrellas
    CALIFICACION_SERVICIO = Column(Integer, nullable=False)  # 1-5 estrellas
    CALIFICACION_ENTREGA = Column(Integer, nullable=False)  # 1-5 estrellas
    COMENTARIO = Column(String(500), nullable=True)
    FECHA = Column(DateTime, default=datetime.utcnow)


class MODELO_REFILL_SOLICITUD(BASE):
    __tablename__ = "REFILL_SOLICITUDES"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    INSUMO_ID = Column(Integer, ForeignKey("INSUMOS.ID"), nullable=False)
    USUARIO_SOLICITA = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=False)
    CANTIDAD_SOLICITADA = Column(Integer, nullable=False)
    ESTADO = Column(String(50), default="pendiente")  # "pendiente", "aprobado", "rechazado", "completado"
    APROBADO_POR = Column(Integer, ForeignKey("USUARIOS.ID"), nullable=True)
    FECHA_SOLICITUD = Column(DateTime, default=datetime.utcnow)
    FECHA_APROBACION = Column(DateTime, nullable=True)


def OBTENER_SESION():
    return SESION_FACTORY()


def CERRAR_SESION():
    SESION_FACTORY.remove()
