"""
CONFIGURACIÓN BASE DE DATOS
===========================
Gestiona conexión SQLite multi-plataforma
"""
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import os

BASE = declarative_base()

# Tabla intermedia para relación many-to-many
TABLA_USUARIO_ROLES = Table(
    'USUARIO_ROLES',
    BASE.metadata,
    Column('USUARIO_ID', Integer, ForeignKey('USUARIOS.ID')),
    Column('ROL_ID', Integer, ForeignKey('ROLES.ID'))
)


class MODELO_USUARIO(BASE):
    """Modelo de usuario en base de datos"""
    __tablename__ = 'USUARIOS'
    
    ID = Column(Integer, primary_key=True, autoincrement=True)
    EMAIL = Column(String(255), unique=True, nullable=False, index=True)
    NOMBRE_USUARIO = Column(String(100), unique=True, nullable=False)
    CONTRASENA_HASH = Column(String(255), nullable=False)
    HUELLA_DISPOSITIVO = Column(String(255), nullable=False)
    ACTIVO = Column(Boolean, default=True)
    VERIFICADO = Column(Boolean, default=False)
    FECHA_CREACION = Column(DateTime, default=datetime.utcnow)
    ULTIMA_CONEXION = Column(DateTime, nullable=True)
    
    # Relaciones
    ROLES = relationship("MODELO_ROL", secondary=TABLA_USUARIO_ROLES, back_populates="USUARIOS")
    SESIONES = relationship("MODELO_SESION", back_populates="USUARIO", cascade="all, delete-orphan")


class MODELO_ROL(BASE):
    """Modelo de roles del sistema"""
    __tablename__ = 'ROLES'
    
    ID = Column(Integer, primary_key=True, autoincrement=True)
    NOMBRE = Column(String(50), unique=True, nullable=False)
    DESCRIPCION = Column(String(255))
    
    # Relaciones
    USUARIOS = relationship("MODELO_USUARIO", secondary=TABLA_USUARIO_ROLES, back_populates="ROLES")


class MODELO_SESION(BASE):
    """Modelo de sesiones activas"""
    __tablename__ = 'SESIONES'
    
    ID = Column(Integer, primary_key=True, autoincrement=True)
    USUARIO_ID = Column(Integer, ForeignKey('USUARIOS.ID'), nullable=False)
    REFRESH_TOKEN = Column(String(500), unique=True, nullable=False)
    HUELLA_DISPOSITIVO = Column(String(255), nullable=False)
    IP = Column(String(45))
    NAVEGADOR = Column(String(255))
    ACTIVA = Column(Boolean, default=True)
    FECHA_CREACION = Column(DateTime, default=datetime.utcnow)
    FECHA_EXPIRACION = Column(DateTime, nullable=False)
    
    # Relaciones
    USUARIO = relationship("MODELO_USUARIO", back_populates="SESIONES")


# Motor de base de datos
def OBTENER_RUTA_BD():
    """Obtiene ruta de BD según plataforma"""
    if os.name == 'nt':  # Windows
        return os.path.join(os.getenv('APPDATA'), 'AppSegura', 'app_segura.db')
    elif os.name == 'posix':  # Linux/Mac
        return os.path.join(os.path.expanduser('~'), '.app_segura', 'app_segura.db')
    else:  # Web/Móvil
        return 'app_segura.db'


RUTA_BD = OBTENER_RUTA_BD()
os.makedirs(os.path.dirname(RUTA_BD), exist_ok=True)

MOTOR = create_engine(f'sqlite:///{RUTA_BD}', echo=False)
SESION_FACTORY = sessionmaker(bind=MOTOR)


async def INICIALIZAR_BASE_DATOS():
    """Crea tablas y roles por defecto"""
    BASE.metadata.create_all(MOTOR)
    
    # Crear roles por defecto
    with SESION_FACTORY() as sesion:
        from core.Constantes import ROLES
        
        ROLES_DEFECTO = [
            MODELO_ROL(NOMBRE=ROLES.SUPER_ADMIN, DESCRIPCION="Control total del sistema"),
            MODELO_ROL(NOMBRE=ROLES.ADMIN, DESCRIPCION="Administrador del sistema"),
            MODELO_ROL(NOMBRE=ROLES.MODERADOR, DESCRIPCION="Moderador de contenido"),
            MODELO_ROL(NOMBRE=ROLES.USUARIO, DESCRIPCION="Usuario estándar"),
            MODELO_ROL(NOMBRE=ROLES.INVITADO, DESCRIPCION="Acceso limitado")
        ]
        
        for rol in ROLES_DEFECTO:
            existe = sesion.query(MODELO_ROL).filter_by(NOMBRE=rol.NOMBRE).first()
            if not existe:
                sesion.add(rol)
        
        sesion.commit()
    
    print("✅ Base de datos inicializada correctamente")


def OBTENER_SESION():
    """Retorna nueva sesión de BD"""
    return SESION_FACTORY()