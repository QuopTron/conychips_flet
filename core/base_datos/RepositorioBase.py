"""
REPOSITORIO BASE
================
Clase base para todos los repositorios con operaciones CRUD comunes
"""

from typing import TypeVar, Generic, Optional, List, Type
from sqlalchemy.orm import Session
from core.base_datos.ConfiguracionBD import BASE

T = TypeVar('T', bound=BASE)


class RepositorioBase(Generic[T]):
    """Repositorio genérico con operaciones CRUD básicas"""
    
    def __init__(self, MODELO: Type[T], SESION: Session):
        """
        Inicializa repositorio
        
        Args:
            MODELO: Clase del modelo SQLAlchemy
            SESION: Sesión de base de datos
        """
        self._MODELO = MODELO
        self._SESION = SESION
    
    def CREAR(self, ENTIDAD: T) -> T:
        """
        Crea nueva entidad en BD
        
        Args:
            ENTIDAD: Instancia del modelo a crear
            
        Returns:
            Entidad creada con ID asignado
        """
        try:
            self._SESION.add(ENTIDAD)
            self._SESION.commit()
            self._SESION.refresh(ENTIDAD)
            return ENTIDAD
        except Exception as ERROR:
            self._SESION.rollback()
            print(f"❌ Error al crear entidad: {ERROR}")
            raise
    
    def OBTENER_POR_ID(self, ID: int) -> Optional[T]:
        """
        Obtiene entidad por ID
        
        Args:
            ID: Identificador de la entidad
            
        Returns:
            Entidad encontrada o None
        """
        return self._SESION.query(self._MODELO).filter_by(ID=ID).first()
    
    def OBTENER_TODOS(self, LIMITE: int = 100, OFFSET: int = 0) -> List[T]:
        """
        Obtiene todas las entidades con paginación
        
        Args:
            LIMITE: Cantidad máxima de resultados
            OFFSET: Posición inicial
            
        Returns:
            Lista de entidades
        """
        return self._SESION.query(self._MODELO).limit(LIMITE).offset(OFFSET).all()
    
    def ACTUALIZAR(self, ID: int, **CAMPOS) -> Optional[T]:
        """
        Actualiza campos de una entidad
        
        Args:
            ID: Identificador de la entidad
            **CAMPOS: Campos a actualizar
            
        Returns:
            Entidad actualizada o None si no existe
        """
        try:
            ENTIDAD = self.OBTENER_POR_ID(ID)
            
            if not ENTIDAD:
                return None
            
            for CAMPO, VALOR in CAMPOS.items():
                if hasattr(ENTIDAD, CAMPO):
                    setattr(ENTIDAD, CAMPO, VALOR)
            
            self._SESION.commit()
            self._SESION.refresh(ENTIDAD)
            
            return ENTIDAD
            
        except Exception as ERROR:
            self._SESION.rollback()
            print(f"❌ Error al actualizar entidad: {ERROR}")
            raise
    
    def ELIMINAR(self, ID: int) -> bool:
        """
        Elimina entidad por ID
        
        Args:
            ID: Identificador de la entidad
            
        Returns:
            True si se eliminó, False si no
        """
        try:
            ENTIDAD = self.OBTENER_POR_ID(ID)
            
            if not ENTIDAD:
                return False
            
            self._SESION.delete(ENTIDAD)
            self._SESION.commit()
            
            return True
            
        except Exception as ERROR:
            self._SESION.rollback()
            print(f"❌ Error al eliminar entidad: {ERROR}")
            raise
    
    def EXISTE(self, ID: int) -> bool:
        """Verifica si existe una entidad con el ID dado"""
        return self._SESION.query(self._MODELO).filter_by(ID=ID).count() > 0
    
    def CONTAR(self) -> int:
        """Cuenta total de entidades"""
        return self._SESION.query(self._MODELO).count()