"""
💬 Componente de Chat Universal - Compatible con todos los roles
"""

import flet as ft
from datetime import datetime
from typing import Optional, Callable
import asyncio

from core.constantes import COLORES, TAMANOS, ICONOS
from core.chat.GestorChat import GestorChat, EstadoMensaje
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_USUARIO


class ChatDialog:
    """Diálogo de chat universal para todos los roles"""
    
    def __init__(
        self,
        pagina: ft.Page,
        pedido_id: int,
        usuario_id: int,
        on_cerrar: Optional[Callable] = None
    ):
        self.PAGINA = pagina
        self.PEDIDO_ID = pedido_id
        self.USUARIO_ID = usuario_id
        self.ON_CERRAR = on_cerrar
        
        self.GESTOR_CHAT = GestorChat()
        
        # Componentes UI
        self.MENSAJES_LISTA = ft.ListView(
            spacing=10,
            expand=True,
            auto_scroll=True,
            padding=10,
        )
        
        self.MENSAJE_INPUT = ft.TextField(
            hint_text="Escribe un mensaje...",
            expand=True,
            multiline=True,
            min_lines=1,
            max_lines=3,
            on_change=self._ON_TYPING,
            on_submit=self._ENVIAR_MENSAJE_SYNC,
        )
        
        self.TYPING_INDICATOR = ft.Text(
            "",
            size=12,
            color=COLORES.TEXTO_SECUNDARIO,
            italic=True,
        )
        
        self.DIALOG = None
        self._TYPING_TIMER = None
    
    def _ON_TYPING(self, e):
        """Maneja el evento de escritura"""
        # Cancelar timer anterior
        if self._TYPING_TIMER:
            self._TYPING_TIMER.cancel()
        
        # Notificar que está escribiendo
        asyncio.create_task(
            self.GESTOR_CHAT.NOTIFICAR_ESCRIBIENDO(
                self.PEDIDO_ID,
                self.USUARIO_ID,
                True
            )
        )
        
        # Programar detener escritura después de 3 segundos
        self._TYPING_TIMER = asyncio.get_event_loop().call_later(
            3.0,
            lambda: asyncio.create_task(
                self.GESTOR_CHAT.NOTIFICAR_ESCRIBIENDO(
                    self.PEDIDO_ID,
                    self.USUARIO_ID,
                    False
                )
            )
        )
    
    def CARGAR_MENSAJES(self):
        """Carga mensajes del chat"""
        mensajes = self.GESTOR_CHAT.OBTENER_MENSAJES(
            self.PEDIDO_ID,
            self.USUARIO_ID
        )
        
        self.MENSAJES_LISTA.controls.clear()
        
        if not mensajes:
            self.MENSAJES_LISTA.controls.append(
                ft.Container(
                    content=ft.Text(
                        "💬 Sin mensajes aún. ¡Empieza la conversación!",
                        color=COLORES.TEXTO_SECUNDARIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=20,
                )
            )
        else:
            for msg in mensajes:
                self.MENSAJES_LISTA.controls.append(
                    self._CREAR_BURBUJA_MENSAJE(msg)
                )
    
    def _CREAR_BURBUJA_MENSAJE(self, mensaje: dict) -> ft.Container:
        """Crea una burbuja de mensaje"""
        es_mio = mensaje["es_mio"]
        
        # Icono de estado (para mensajes propios)
        icono_estado = ""
        if es_mio and "estado" in mensaje:
            if mensaje["estado"] == EstadoMensaje.ENVIANDO:
                icono_estado = "⏳"
            elif mensaje["estado"] == EstadoMensaje.ENVIADO:
                icono_estado = "✓"
            elif mensaje["estado"] == EstadoMensaje.ENTREGADO:
                icono_estado = "✓✓"
            elif mensaje["estado"] == EstadoMensaje.LEIDO:
                icono_estado = "✓✓"
            elif mensaje["estado"] == EstadoMensaje.ERROR:
                icono_estado = "❌"
        
        # Contenido del mensaje
        contenido_mensaje = ft.Column([
            ft.Text(
                mensaje["usuario_nombre"],
                size=10,
                weight=ft.FontWeight.BOLD,
                color=COLORES.TEXTO_BLANCO if es_mio else COLORES.TEXTO_SECUNDARIO,
            ),
            ft.Text(
                mensaje["mensaje"],
                size=14,
                color=COLORES.TEXTO_BLANCO if es_mio else COLORES.TEXTO_PRINCIPAL,
            ),
            ft.Row([
                ft.Text(
                    datetime.fromisoformat(mensaje["fecha"]).strftime("%H:%M"),
                    size=10,
                    color=COLORES.TEXTO_BLANCO if es_mio else COLORES.TEXTO_SECUNDARIO,
                ),
                ft.Text(
                    icono_estado,
                    size=10,
                ) if icono_estado else ft.Container(),
            ], spacing=5),
        ], tight=True, spacing=3)
        
        # Contenedor de la burbuja
        return ft.Container(
            content=contenido_mensaje,
            padding=10,
            bgcolor=COLORES.PRIMARIO if es_mio else COLORES.FONDO_TARJETA,
            border_radius=ft.border_radius.only(
                top_left=15,
                top_right=15,
                bottom_left=0 if es_mio else 15,
                bottom_right=15 if es_mio else 0,
            ),
            alignment=ft.alignment.center_right if es_mio else ft.alignment.center_left,
            margin=ft.margin.only(
                left=50 if es_mio else 0,
                right=0 if es_mio else 50,
            ),
        )
    
    def _ENVIAR_MENSAJE_SYNC(self, e):
        """Wrapper sincrónico para enviar mensaje"""
        asyncio.create_task(self._ENVIAR_MENSAJE(e))
    
    async def _ENVIAR_MENSAJE(self, e):
        """Envía un mensaje al chat"""
        if not self.MENSAJE_INPUT.value or not self.MENSAJE_INPUT.value.strip():
            return
        
        mensaje_texto = self.MENSAJE_INPUT.value.strip()
        self.MENSAJE_INPUT.value = ""
        
        # Detener indicador de escritura
        await self.GESTOR_CHAT.NOTIFICAR_ESCRIBIENDO(
            self.PEDIDO_ID,
            self.USUARIO_ID,
            False
        )
        
        # Obtener nombre del usuario
        sesion = OBTENER_SESION()
        usuario = sesion.query(MODELO_USUARIO).filter_by(ID=self.USUARIO_ID).first()
        nombre_usuario = usuario.NOMBRE_USUARIO if usuario else "Tú"
        sesion.close()
        
        # Agregar mensaje localmente con estado "enviando"
        mensaje_temporal = {
            "id": -1,  # ID temporal
            "pedido_id": self.PEDIDO_ID,
            "usuario_id": self.USUARIO_ID,
            "usuario_nombre": nombre_usuario,
            "mensaje": mensaje_texto,
            "tipo": "texto",
            "fecha": datetime.now().isoformat(),
            "es_mio": True,
            "estado": EstadoMensaje.ENVIANDO
        }
        
        self.MENSAJES_LISTA.controls.append(
            self._CREAR_BURBUJA_MENSAJE(mensaje_temporal)
        )
        
        if self.DIALOG:
            self.DIALOG.update()
        
        # Enviar mensaje al servidor
        resultado = await self.GESTOR_CHAT.ENVIAR_MENSAJE(
            pedido_id=self.PEDIDO_ID,
            usuario_id=self.USUARIO_ID,
            mensaje=mensaje_texto,
        )
        
        if resultado.get("exito"):
            # Actualizar el mensaje temporal con el ID real
            if self.MENSAJES_LISTA.controls:
                ultima_burbuja = self.MENSAJES_LISTA.controls[-1]
                # Actualizar estado a "enviado"
                mensaje_temporal["id"] = resultado["mensaje_id"]
                mensaje_temporal["estado"] = EstadoMensaje.ENVIADO
                mensaje_temporal["hash"] = resultado["hash"]
                
                # Reemplazar burbuja
                self.MENSAJES_LISTA.controls[-1] = self._CREAR_BURBUJA_MENSAJE(mensaje_temporal)
                
                if self.DIALOG:
                    self.DIALOG.update()
        else:
            # Mostrar error
            if self.PAGINA.snack_bar:
                self.PAGINA.snack_bar.content = ft.Text(f"Error: {resultado.get('error', 'No se pudo enviar')}")
                self.PAGINA.snack_bar.bgcolor = COLORES.ERROR
                self.PAGINA.snack_bar.open = True
                self.PAGINA.update()
    
    def ABRIR(self):
        """Abre el diálogo de chat"""
        # Cargar mensajes
        self.CARGAR_MENSAJES()
        
        # Crear contenedor principal
        contenido = ft.Column([
            # Lista de mensajes
            ft.Container(
                content=self.MENSAJES_LISTA,
                expand=True,
                border=ft.border.all(1, COLORES.BORDE),
                border_radius=TAMANOS.RADIO_BORDE,
                bgcolor=COLORES.FONDO,
            ),
            
            # Typing indicator
            self.TYPING_INDICATOR,
            
            # Input de mensaje
            ft.Row([
                self.MENSAJE_INPUT,
                ft.IconButton(
                    icon=ICONOS.ENVIAR,
                    on_click=self._ENVIAR_MENSAJE_SYNC,
                    bgcolor=COLORES.PRIMARIO,
                    icon_color=COLORES.TEXTO_BLANCO,
                    tooltip="Enviar mensaje (Enter)",
                ),
            ], spacing=5),
        ], spacing=10, expand=True)
        
        # Crear diálogo
        self.DIALOG = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ICONOS.CHAT, color=COLORES.PRIMARIO),
                ft.Text(f"Chat - Pedido #{self.PEDIDO_ID}", weight=ft.FontWeight.BOLD),
            ]),
            content=ft.Container(
                content=contenido,
                width=650,
                height=550,
            ),
            actions=[
                ft.TextButton(
                    "Cerrar",
                    on_click=lambda e: self.CERRAR()
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Mostrar diálogo
        self.PAGINA.dialog = self.DIALOG
        self.DIALOG.open = True
        self.PAGINA.update()
        
        # Marcar mensajes como leídos
        asyncio.create_task(self._MARCAR_MENSAJES_LEIDOS())
    
    async def _MARCAR_MENSAJES_LEIDOS(self):
        """Marca todos los mensajes como leídos"""
        mensajes = self.GESTOR_CHAT.OBTENER_MENSAJES(
            self.PEDIDO_ID,
            self.USUARIO_ID
        )
        
        for msg in mensajes:
            if not msg["es_mio"] and msg.get("estado") != EstadoMensaje.LEIDO:
                await self.GESTOR_CHAT.MARCAR_LEIDO(msg["id"], self.USUARIO_ID)
    
    def CERRAR(self):
        """Cierra el diálogo"""
        if self.DIALOG:
            self.DIALOG.open = False
            self.PAGINA.update()
        
        if self.ON_CERRAR:
            self.ON_CERRAR()
