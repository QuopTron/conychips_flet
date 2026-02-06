"""
🔒 Gestor de Chat - Sistema completo con WebSockets, estados y permisos
"""

import asyncio
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_MENSAJE_CHAT,
    MODELO_USUARIO,
    MODELO_PEDIDO,
    MODELO_ROL,
)
from core.websocket.GestorNotificaciones import GestorNotificaciones
from core.audio.GestorSonidos import GestorSonidos


@dataclass
class EstadoMensaje:
    """Estados posibles de un mensaje"""
    ENVIANDO = "enviando"
    ENVIADO = "enviado"
    ENTREGADO = "entregado"
    LEIDO = "leido"
    ERROR = "error"


@dataclass
class PermisoChat:
    """Permisos de acceso al chat"""
    CLIENTE = "CLIENTE"  # Solo el cliente puede ver
    ADMIN = "ADMIN"      # Admin y SuperAdmin pueden ver
    SUPERADMIN = "SUPERADMIN"  # Solo SuperAdmin
    TODOS = "TODOS"      # Todos los roles autorizados


class GestorChat:
    """Gestor centralizado del sistema de chat"""
    
    _INSTANCIA = None
    _USUARIOS_ESCRIBIENDO: Dict[int, Dict[int, datetime]] = {}  # {pedido_id: {usuario_id: timestamp}}
    _CALLBACKS_TYPING: Dict[int, List[Callable]] = {}  # {pedido_id: [callbacks]}
    
    def __new__(cls):
        if cls._INSTANCIA is None:
            cls._INSTANCIA = super().__new__(cls)
            cls._INSTANCIA._INICIALIZADO = False
        return cls._INSTANCIA
    
    def __init__(self):
        if self._INICIALIZADO:
            return
        
        self.GESTOR_NOTIFICACIONES = GestorNotificaciones()
        self.GESTOR_SONIDOS = GestorSonidos()
        self._INICIALIZADO = True
    
    @staticmethod
    def HASHEAR_MENSAJE(mensaje: str, usuario_id: int, timestamp: str) -> str:
        """
        Genera hash único para cada mensaje
        
        Args:
            mensaje: Contenido del mensaje
            usuario_id: ID del usuario que envía
            timestamp: Timestamp del mensaje
            
        Returns:
            str: Hash SHA256 del mensaje
        """
        contenido = f"{mensaje}{usuario_id}{timestamp}"
        return hashlib.sha256(contenido.encode()).hexdigest()
    
    def VERIFICAR_PERMISO_CHAT(self, usuario_id: int, pedido_id: int) -> bool:
        """
        Verifica si un usuario tiene permiso para acceder al chat de un pedido
        
        Args:
            usuario_id: ID del usuario
            pedido_id: ID del pedido
            
        Returns:
            bool: True si tiene permiso, False si no
        """
        sesion = OBTENER_SESION()
        
        try:
            # Obtener usuario y pedido
            usuario = sesion.query(MODELO_USUARIO).filter_by(ID=usuario_id).first()
            pedido = sesion.query(MODELO_PEDIDO).filter_by(ID=pedido_id).first()
            
            if not usuario or not pedido:
                return False
            
            # Obtener roles del usuario
            roles = [rol.NOMBRE for rol in usuario.ROLES]
            
            # SUPERADMIN y ADMIN siempre tienen acceso
            if "SUPERADMIN" in roles or "ADMIN" in roles:
                return True
            
            # Cliente solo puede ver sus propios pedidos
            if "CLIENTE" in roles and pedido.CLIENTE_ID == usuario_id:
                return True
            
            # Motorizado solo puede ver pedidos asignados
            if "MOTORIZADO" in roles and hasattr(pedido, 'MOTORIZADO_ID') and pedido.MOTORIZADO_ID == usuario_id:
                return True
            
            # Personal de atención puede ver todos los pedidos
            if "ATENCION" in roles:
                return True
            
            return False
            
        finally:
            sesion.close()
    
    async def ENVIAR_MENSAJE(
        self,
        pedido_id: int,
        usuario_id: int,
        mensaje: str,
        tipo: str = "texto"
    ) -> Dict:
        """
        Envía un mensaje al chat con estado y hash
        
        Args:
            pedido_id: ID del pedido
            usuario_id: ID del usuario que envía
            mensaje: Contenido del mensaje
            tipo: Tipo de mensaje (texto, imagen, archivo)
            
        Returns:
            dict: Información del mensaje enviado
        """
        # Verificar permiso
        if not self.VERIFICAR_PERMISO_CHAT(usuario_id, pedido_id):
            return {
                "exito": False,
                "error": "Sin permiso para enviar mensaje"
            }
        
        sesion = OBTENER_SESION()
        
        try:
            # Crear timestamp
            timestamp = datetime.now(timezone.utc)
            
            # Generar hash del mensaje
            mensaje_hash = self.HASHEAR_MENSAJE(mensaje, usuario_id, timestamp.isoformat())
            
            # Crear mensaje en BD
            mensaje_obj = MODELO_MENSAJE_CHAT(
                PEDIDO_ID=pedido_id,
                USUARIO_ID=usuario_id,
                MENSAJE=mensaje,
                TIPO=tipo,
                FECHA=timestamp,
            )
            
            # Agregar campos de estado si existen en el modelo
            if hasattr(mensaje_obj, 'ESTADO'):
                mensaje_obj.ESTADO = EstadoMensaje.ENVIADO
            if hasattr(mensaje_obj, 'HASH'):
                mensaje_obj.HASH = mensaje_hash
            
            sesion.add(mensaje_obj)
            sesion.commit()
            
            mensaje_id = mensaje_obj.ID
            
            # Preparar payload para broadcast
            payload = {
                "tipo": "chat",
                "accion": "nuevo_mensaje",
                "mensaje_id": mensaje_id,
                "pedido_id": pedido_id,
                "usuario_id": usuario_id,
                "mensaje": mensaje,
                "tipo_mensaje": tipo,
                "fecha": timestamp.isoformat(),
                "hash": mensaje_hash,
                "estado": EstadoMensaje.ENVIADO,
                "sonido": True,
            }
            
            # Broadcast a usuarios autorizados
            await self.GESTOR_NOTIFICACIONES._BROADCAST_PEDIDO(pedido_id, payload)
            
            # Marcar como entregado
            await self._MARCAR_ENTREGADO(mensaje_id)
            
            return {
                "exito": True,
                "mensaje_id": mensaje_id,
                "hash": mensaje_hash,
                "estado": EstadoMensaje.ENVIADO
            }
            
        except Exception as e:
            print(f"Error enviando mensaje: {e}")
            return {
                "exito": False,
                "error": str(e)
            }
        finally:
            sesion.close()
    
    async def _MARCAR_ENTREGADO(self, mensaje_id: int):
        """Marca un mensaje como entregado"""
        sesion = OBTENER_SESION()
        
        try:
            mensaje = sesion.query(MODELO_MENSAJE_CHAT).filter_by(ID=mensaje_id).first()
            if mensaje and hasattr(mensaje, 'ESTADO'):
                mensaje.ESTADO = EstadoMensaje.ENTREGADO
                sesion.commit()
                
                # Broadcast actualización de estado
                payload = {
                    "tipo": "chat",
                    "accion": "estado_actualizado",
                    "mensaje_id": mensaje_id,
                    "estado": EstadoMensaje.ENTREGADO
                }
                await self.GESTOR_NOTIFICACIONES._BROADCAST_PEDIDO(mensaje.PEDIDO_ID, payload)
        finally:
            sesion.close()
    
    async def MARCAR_LEIDO(self, mensaje_id: int, usuario_id: int):
        """
        Marca un mensaje como leído
        
        Args:
            mensaje_id: ID del mensaje
            usuario_id: ID del usuario que leyó
        """
        sesion = OBTENER_SESION()
        
        try:
            mensaje = sesion.query(MODELO_MENSAJE_CHAT).filter_by(ID=mensaje_id).first()
            
            if not mensaje:
                return
            
            # Verificar permiso
            if not self.VERIFICAR_PERMISO_CHAT(usuario_id, mensaje.PEDIDO_ID):
                return
            
            # Solo marcar como leído si no es el autor
            if mensaje.USUARIO_ID == usuario_id:
                return
            
            # Actualizar estado
            if hasattr(mensaje, 'ESTADO'):
                mensaje.ESTADO = EstadoMensaje.LEIDO
            if hasattr(mensaje, 'FECHA_LECTURA'):
                mensaje.FECHA_LECTURA = datetime.now(timezone.utc)
            
            sesion.commit()
            
            # Broadcast actualización
            payload = {
                "tipo": "chat",
                "accion": "estado_actualizado",
                "mensaje_id": mensaje_id,
                "estado": EstadoMensaje.LEIDO,
                "leido_por": usuario_id
            }
            await self.GESTOR_NOTIFICACIONES._BROADCAST_PEDIDO(mensaje.PEDIDO_ID, payload)
            
        finally:
            sesion.close()
    
    async def NOTIFICAR_ESCRIBIENDO(self, pedido_id: int, usuario_id: int, escribiendo: bool):
        """
        Notifica cuando un usuario está escribiendo
        
        Args:
            pedido_id: ID del pedido
            usuario_id: ID del usuario
            escribiendo: True si está escribiendo, False si dejó de escribir
        """
        if escribiendo:
            if pedido_id not in self._USUARIOS_ESCRIBIENDO:
                self._USUARIOS_ESCRIBIENDO[pedido_id] = {}
            self._USUARIOS_ESCRIBIENDO[pedido_id][usuario_id] = datetime.now()
        else:
            if pedido_id in self._USUARIOS_ESCRIBIENDO:
                self._USUARIOS_ESCRIBIENDO[pedido_id].pop(usuario_id, None)
        
        # Broadcast typing indicator
        payload = {
            "tipo": "chat",
            "accion": "typing",
            "pedido_id": pedido_id,
            "usuario_id": usuario_id,
            "escribiendo": escribiendo
        }
        
        await self.GESTOR_NOTIFICACIONES._BROADCAST_PEDIDO(pedido_id, payload)
    
    def OBTENER_MENSAJES(
        self,
        pedido_id: int,
        usuario_id: int,
        limite: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """
        Obtiene mensajes de un pedido
        
        Args:
            pedido_id: ID del pedido
            usuario_id: ID del usuario que solicita
            limite: Número máximo de mensajes
            offset: Offset para paginación
            
        Returns:
            List[Dict]: Lista de mensajes
        """
        # Verificar permiso
        if not self.VERIFICAR_PERMISO_CHAT(usuario_id, pedido_id):
            return []
        
        sesion = OBTENER_SESION()
        
        try:
            mensajes = (
                sesion.query(MODELO_MENSAJE_CHAT)
                .filter_by(PEDIDO_ID=pedido_id)
                .order_by(MODELO_MENSAJE_CHAT.FECHA.asc())
                .offset(offset)
                .limit(limite)
                .all()
            )
            
            resultado = []
            for msg in mensajes:
                usuario = sesion.query(MODELO_USUARIO).filter_by(ID=msg.USUARIO_ID).first()
                
                mensaje_dict = {
                    "id": msg.ID,
                    "pedido_id": msg.PEDIDO_ID,
                    "usuario_id": msg.USUARIO_ID,
                    "usuario_nombre": usuario.NOMBRE_USUARIO if usuario else "Desconocido",
                    "mensaje": msg.MENSAJE,
                    "tipo": msg.TIPO,
                    "fecha": msg.FECHA.isoformat(),
                    "es_mio": msg.USUARIO_ID == usuario_id,
                }
                
                # Agregar campos opcionales
                if hasattr(msg, 'ESTADO'):
                    mensaje_dict["estado"] = msg.ESTADO
                if hasattr(msg, 'HASH'):
                    mensaje_dict["hash"] = msg.HASH
                if hasattr(msg, 'FECHA_LECTURA'):
                    mensaje_dict["fecha_lectura"] = msg.FECHA_LECTURA.isoformat() if msg.FECHA_LECTURA else None
                
                resultado.append(mensaje_dict)
            
            return resultado
            
        finally:
            sesion.close()
    
    def OBTENER_USUARIOS_ESCRIBIENDO(self, pedido_id: int) -> List[int]:
        """
        Obtiene lista de usuarios que están escribiendo
        
        Args:
            pedido_id: ID del pedido
            
        Returns:
            List[int]: Lista de IDs de usuarios escribiendo
        """
        if pedido_id not in self._USUARIOS_ESCRIBIENDO:
            return []
        
        # Limpiar usuarios que dejaron de escribir hace más de 5 segundos
        ahora = datetime.now()
        usuarios_activos = []
        
        for usuario_id, timestamp in list(self._USUARIOS_ESCRIBIENDO[pedido_id].items()):
            if (ahora - timestamp).total_seconds() < 5:
                usuarios_activos.append(usuario_id)
            else:
                del self._USUARIOS_ESCRIBIENDO[pedido_id][usuario_id]
        
        return usuarios_activos
