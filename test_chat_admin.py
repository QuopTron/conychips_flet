#!/usr/bin/env python3
"""
🧪 Test Chat Flotante en Vista Admin
"""
import flet as ft
import sys
sys.path.insert(0, '/mnt/flox/conychips')

from features.autenticacion.domain.entities.Usuario import Usuario
from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_USUARIO


def main(page: ft.Page):
    page.title = "Test Chat Admin"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window.width = 1200
    page.window.height = 800
    
    # Obtener admin de prueba
    sesion = OBTENER_SESION()
    
    # Buscar un admin o superadmin
    admin = sesion.query(MODELO_USUARIO).filter(
        MODELO_USUARIO.ROLES.any()
    ).first()
    
    if not admin:
        page.add(ft.Text("❌ No hay usuarios en la base de datos"))
        sesion.close()
        return
    
    # Convertir a entidad Usuario
    usuario_entity = Usuario(
        ID=admin.ID,
        NOMBRE_USUARIO=admin.NOMBRE_USUARIO,
        ROLES=[admin.ROLES[0]]
    )
    
    rol = admin.ROLES[0].NOMBRE if admin.ROLES else "ADMIN"
    
    print(f"✅ Usuario: {admin.NOMBRE_USUARIO} (ID: {admin.ID})")
    print(f"✅ Rol: {rol}")
    
    sesion.close()
    
    try:
        # Crear página admin
        print("🔵 Creando PaginaAdmin...")
        pagina_admin = PaginaAdmin(page, usuario_entity)
        
        print("🔵 Agregando PaginaAdmin a la página...")
        page.add(pagina_admin)
        
        print("✅ PaginaAdmin agregada exitosamente")
        print("✅ Deberías ver el botón flotante de chat en la esquina inferior derecha")
        
    except Exception as e:
        print(f"❌ Error creando PaginaAdmin: {e}")
        import traceback
        traceback.print_exc()
        page.add(ft.Text(f"Error: {e}"))


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
