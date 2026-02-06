#!/usr/bin/env python3
"""
🧪 Test Visual del Chat Flotante tipo Messenger
"""
import flet as ft
import sys
sys.path.insert(0, '/mnt/flox/conychips')

from core.chat.ChatFlotante import ChatFlotante
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_USUARIO


def main(page: ft.Page):
    page.title = "Test Chat Flotante"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    # Obtener usuario de prueba
    sesion = OBTENER_SESION()
    
    # Buscar un cliente
    cliente = sesion.query(MODELO_USUARIO).filter(
        MODELO_USUARIO.ROLES.any()
    ).first()
    
    if not cliente:
        page.add(ft.Text("❌ No hay usuarios en la base de datos"))
        sesion.close()
        return
    
    rol = cliente.ROLES[0].NOMBRE if cliente.ROLES else "CLIENTE"
    
    print(f"✅ Usuario: {cliente.NOMBRE_USUARIO} (ID: {cliente.ID})")
    print(f"✅ Rol: {rol}")
    
    sesion.close()
    
    # Crear chat flotante
    chat_flotante = ChatFlotante(
        pagina=page,
        usuario_id=cliente.ID,
        usuario_rol=rol
    )
    
    # Contenido de prueba
    contenido = ft.Column([
        ft.Text(
            "Test del Chat Flotante tipo Messenger",
            size=24,
            weight=ft.FontWeight.BOLD
        ),
        ft.Text(
            f"Usuario: {cliente.NOMBRE_USUARIO}",
            size=16
        ),
        ft.Text(
            f"Rol: {rol}",
            size=16
        ),
        ft.Divider(),
        ft.Text(
            "Instrucciones:",
            size=18,
            weight=ft.FontWeight.BOLD
        ),
        ft.Text("1. Haz clic en el botón flotante azul en la esquina inferior derecha"),
        ft.Text("2. Se abrirá el panel de conversaciones"),
        ft.Text("3. Si hay pedidos con mensajes, aparecerán listados"),
        ft.Text("4. Haz clic en una conversación para abrir el chat"),
        ft.Text("5. El badge rojo muestra mensajes no leídos"),
        ft.Container(height=20),
        ft.Text(
            "El chat está integrado con:",
            size=16,
            weight=ft.FontWeight.BOLD
        ),
        ft.Text("✅ WebSockets para tiempo real"),
        ft.Text("✅ Estados de mensaje (enviando, enviado, entregado, leído)"),
        ft.Text("✅ Indicador de escritura"),
        ft.Text("✅ Notificaciones de mensajes no leídos"),
        ft.Text("✅ Hashing SHA256 para evitar duplicados"),
    ], expand=True, scroll=ft.ScrollMode.AUTO)
    
    # Layout con Stack
    layout = ft.Stack([
        ft.Container(content=contenido, padding=20, expand=True),
        chat_flotante
    ], expand=True)
    
    page.add(layout)


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
