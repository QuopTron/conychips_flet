"""Fuente de datos local para usuarios - PostgreSQL"""
import bcrypt
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_USUARIO,
    MODELO_ROL,
    MODELO_SUCURSAL,
    MODELO_AUDITORIA
)


class FuenteUsuariosLocal:
    """Fuente de datos local para gestión de usuarios"""
    
    def OBTENER_USUARIOS(
        self,
        rol_filtro: Optional[str] = None,
        estado_filtro: Optional[bool] = None,
        sucursal_id: Optional[int] = None
    ) -> List:
        """Obtiene usuarios con filtros opcionales"""
        from sqlalchemy.orm import joinedload
        
        sesion: Session = OBTENER_SESION()
        
        try:
            # Eager loading de ROLES y SUCURSAL para evitar lazy load errors
            query = sesion.query(MODELO_USUARIO).options(
                joinedload(MODELO_USUARIO.ROLES),
                joinedload(MODELO_USUARIO.SUCURSAL)
            )
            
            # Filtro por rol
            if rol_filtro and rol_filtro != "TODOS":
                query = query.join(MODELO_USUARIO.ROLES).filter(
                    MODELO_ROL.NOMBRE == rol_filtro
                )
            
            # Filtro por estado activo/inactivo
            if estado_filtro is not None:
                query = query.filter(MODELO_USUARIO.ACTIVO == estado_filtro)
            
            # Filtro por sucursal
            if sucursal_id:
                query = query.filter(MODELO_USUARIO.SUCURSAL_ID == sucursal_id)
            
            usuarios = query.order_by(MODELO_USUARIO.ID.desc()).all()
            
            # Expunge para que los objetos puedan usarse fuera de la sesión
            for usuario in usuarios:
                sesion.expunge(usuario)
            
            return usuarios
            
        finally:
            sesion.close()
    
    def OBTENER_USUARIO_POR_ID(self, usuario_id: int):
        """Obtiene un usuario por ID"""
        sesion = OBTENER_SESION()
        
        try:
            return sesion.query(MODELO_USUARIO).filter_by(ID=usuario_id).first()
        finally:
            sesion.close()
    
    def CREAR_USUARIO(
        self,
        nombre_usuario: str,
        email: str,
        contrasena: str,
        nombre_completo: str,
        rol: str,
        sucursal_id: int,
        activo: bool = True
    ) -> int:
        """Crea un nuevo usuario"""
        sesion = OBTENER_SESION()
        
        try:
            # Verificar que no exista el usuario
            existe = sesion.query(MODELO_USUARIO).filter(
                (MODELO_USUARIO.NOMBRE_USUARIO == nombre_usuario) |
                (MODELO_USUARIO.EMAIL == email)
            ).first()
            
            if existe:
                raise ValueError("El usuario o email ya existe")
            
            # Hashear contraseña
            contrasena_hash = bcrypt.hashpw(
                contrasena.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Obtener rol
            rol_obj = sesion.query(MODELO_ROL).filter_by(NOMBRE=rol).first()
            if not rol_obj:
                raise ValueError(f"Rol '{rol}' no existe")
            
            # Crear usuario
            nuevo_usuario = MODELO_USUARIO(
                NOMBRE_USUARIO=nombre_usuario,
                EMAIL=email,
                CONTRASENA=contrasena_hash,
                NOMBRE_COMPLETO=nombre_completo,
                SUCURSAL_ID=sucursal_id,
                ACTIVO=activo
            )
            nuevo_usuario.ROLES.append(rol_obj)
            
            sesion.add(nuevo_usuario)
            sesion.commit()
            
            # Registrar en auditoría
            self._REGISTRAR_AUDITORIA(
                sesion,
                evento="USUARIO_CREADO",
                usuario_id=nuevo_usuario.ID,
                detalles=f"Usuario '{nombre_usuario}' creado con rol '{rol}'"
            )
            
            return nuevo_usuario.ID
            
        except Exception as e:
            sesion.rollback()
            raise e
        finally:
            sesion.close()
    
    def ACTUALIZAR_USUARIO(self, usuario_id: int, datos: Dict) -> bool:
        """Actualiza un usuario existente"""
        sesion = OBTENER_SESION()
        
        try:
            usuario = sesion.query(MODELO_USUARIO).filter_by(ID=usuario_id).first()
            
            if not usuario:
                raise ValueError(f"Usuario con ID {usuario_id} no existe")
            
            # Actualizar campos permitidos
            if "email" in datos:
                usuario.EMAIL = datos["email"]
            
            if "nombre_completo" in datos:
                usuario.NOMBRE_COMPLETO = datos["nombre_completo"]
            
            if "activo" in datos:
                usuario.ACTIVO = datos["activo"]
            
            if "rol" in datos:
                rol_obj = sesion.query(MODELO_ROL).filter_by(NOMBRE=datos["rol"]).first()
                if rol_obj:
                    usuario.ROLES.clear()
                    usuario.ROLES.append(rol_obj)
            
            if "contrasena_nueva" in datos and datos["contrasena_nueva"]:
                contrasena_hash = bcrypt.hashpw(
                    datos["contrasena_nueva"].encode('utf-8'),
                    bcrypt.gensalt()
                ).decode('utf-8')
                usuario.CONTRASENA = contrasena_hash
            
            sesion.commit()
            
            self._REGISTRAR_AUDITORIA(
                sesion,
                evento="USUARIO_ACTUALIZADO",
                usuario_id=usuario_id,
                detalles=f"Usuario '{usuario.NOMBRE_USUARIO}' actualizado"
            )
            
            return True
            
        except Exception as e:
            sesion.rollback()
            raise e
        finally:
            sesion.close()
    
    def ELIMINAR_USUARIO(self, usuario_id: int) -> bool:
        """Soft delete - marca el usuario como inactivo"""
        sesion = OBTENER_SESION()
        
        try:
            usuario = sesion.query(MODELO_USUARIO).filter_by(ID=usuario_id).first()
            
            if not usuario:
                raise ValueError(f"Usuario con ID {usuario_id} no existe")
            
            usuario.ACTIVO = False
            sesion.commit()
            
            self._REGISTRAR_AUDITORIA(
                sesion,
                evento="USUARIO_ELIMINADO",
                usuario_id=usuario_id,
                detalles=f"Usuario '{usuario.NOMBRE_USUARIO}' marcado como inactivo"
            )
            
            return True
            
        except Exception as e:
            sesion.rollback()
            raise e
        finally:
            sesion.close()
    
    def CAMBIAR_ESTADO_USUARIO(self, usuario_id: int, activo: bool) -> bool:
        """Cambia el estado activo/inactivo"""
        sesion = OBTENER_SESION()
        
        try:
            usuario = sesion.query(MODELO_USUARIO).filter_by(ID=usuario_id).first()
            
            if not usuario:
                raise ValueError(f"Usuario con ID {usuario_id} no existe")
            
            usuario.ACTIVO = activo
            sesion.commit()
            
            estado = "activado" if activo else "desactivado"
            self._REGISTRAR_AUDITORIA(
                sesion,
                evento="USUARIO_CAMBIO_ESTADO",
                usuario_id=usuario_id,
                detalles=f"Usuario '{usuario.NOMBRE_USUARIO}' {estado}"
            )
            
            return True
            
        except Exception as e:
            sesion.rollback()
            raise e
        finally:
            sesion.close()
    
    def CAMBIAR_ROL_USUARIO(self, usuario_id: int, nuevo_rol: str) -> bool:
        """Cambia el rol de un usuario"""
        sesion = OBTENER_SESION()
        
        try:
            usuario = sesion.query(MODELO_USUARIO).filter_by(ID=usuario_id).first()
            
            if not usuario:
                raise ValueError(f"Usuario con ID {usuario_id} no existe")
            
            rol_obj = sesion.query(MODELO_ROL).filter_by(NOMBRE=nuevo_rol).first()
            
            if not rol_obj:
                raise ValueError(f"Rol '{nuevo_rol}' no existe")
            
            usuario.ROLES.clear()
            usuario.ROLES.append(rol_obj)
            sesion.commit()
            
            self._REGISTRAR_AUDITORIA(
                sesion,
                evento="USUARIO_CAMBIO_ROL",
                usuario_id=usuario_id,
                detalles=f"Rol de '{usuario.NOMBRE_USUARIO}' cambiado a '{nuevo_rol}'"
            )
            
            return True
            
        except Exception as e:
            sesion.rollback()
            raise e
        finally:
            sesion.close()
    
    def RESETEAR_CONTRASENA(self, usuario_id: int, nueva_contrasena: str) -> bool:
        """Resetea la contraseña de un usuario"""
        sesion = OBTENER_SESION()
        
        try:
            usuario = sesion.query(MODELO_USUARIO).filter_by(ID=usuario_id).first()
            
            if not usuario:
                raise ValueError(f"Usuario con ID {usuario_id} no existe")
            
            contrasena_hash = bcrypt.hashpw(
                nueva_contrasena.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
            
            usuario.CONTRASENA = contrasena_hash
            sesion.commit()
            
            self._REGISTRAR_AUDITORIA(
                sesion,
                evento="USUARIO_RESET_CONTRASENA",
                usuario_id=usuario_id,
                detalles=f"Contraseña de '{usuario.NOMBRE_USUARIO}' reseteada"
            )
            
            return True
            
        except Exception as e:
            sesion.rollback()
            raise e
        finally:
            sesion.close()
    
    def OBTENER_ROLES_DISPONIBLES(self) -> List:
        """Obtiene todos los roles disponibles"""
        sesion = OBTENER_SESION()
        
        try:
            return sesion.query(MODELO_ROL).all()
        finally:
            sesion.close()
    
    def _REGISTRAR_AUDITORIA(
        self,
        sesion: Session,
        evento: str,
        usuario_id: int,
        detalles: str
    ):
        """Registra una acción en la tabla de auditoría"""
        try:
            auditoria = MODELO_AUDITORIA(
                EVENTO=evento,
                USUARIO_ID=usuario_id,
                ACCION="GESTION_USUARIOS",
                DETALLES=detalles
            )
            sesion.add(auditoria)
            sesion.commit()
        except Exception as e:
            print(f"⚠️ Error registrando auditoría: {e}")
