from typing import TypeVar, Generic, Optional, List, Type
from sqlalchemy.orm import Session
from core.base_datos.ConfiguracionBD import BASE

T = TypeVar('T', bound=BASE)

class RepositorioBase(Generic[T]):
    
    
    def __init__(self, MODELO: Type[T], SESION: Session):
        
        self._MODELO = MODELO
        self._SESION = SESION
    
    def CREAR(self, ENTIDAD: T) -> T:
        
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
        
        return self._SESION.query(self._MODELO).filter_by(ID=ID).first()
    
    def OBTENER_TODOS(self, LIMITE: int = 100, OFFSET: int = 0) -> List[T]:
        
        return self._SESION.query(self._MODELO).limit(LIMITE).offset(OFFSET).all()
    
    def ACTUALIZAR(self, ID: int, **CAMPOS) -> Optional[T]:
        
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
        
        return self._SESION.query(self._MODELO).filter_by(ID=ID).count() > 0
    
    def CONTAR(self) -> int:
        
        return self._SESION.query(self._MODELO).count()
