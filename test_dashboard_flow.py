"""
Test del flujo completo del dashboard
"""
import sys
sys.path.insert(0, '/mnt/flox/conychips')

def test_pagina_admin_constructor():
    """Verifica que PaginaAdmin se construye correctamente"""
    import flet as ft
    from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
    from features.autenticacion.domain.entities.Usuario import Usuario
    
    page = ft.Page()
    usuario = Usuario(
        ID=1,
        EMAIL="admin@test.com",
        NOMBRE_USUARIO="admin",
        ROLES=["SUPERADMIN"]
    )
    
    try:
        print("→ Creando PaginaAdmin...")
        dashboard = PaginaAdmin(page, usuario)
        print(f"✓ PaginaAdmin creado: {type(dashboard)}")
        print(f"  - Es Column: {isinstance(dashboard, ft.Column)}")
        print(f"  - Tiene controls: {len(dashboard.controls) if hasattr(dashboard, 'controls') else 0}")
        
        # Verificar que tiene el método _CONSTRUIR_CONTENIDO
        assert hasattr(dashboard, '_CONSTRUIR_CONTENIDO'), "Falta método _CONSTRUIR_CONTENIDO"
        print(f"✓ Tiene _CONSTRUIR_CONTENIDO")
        
        # Verificar que tiene el método _on_sucursales_change
        assert hasattr(dashboard, '_on_sucursales_change'), "Falta método _on_sucursales_change"
        print(f"✓ Tiene _on_sucursales_change")
        
        # Verificar que LayoutBase creó el navbar
        assert hasattr(dashboard, '_navbar'), "Falta _navbar del LayoutBase"
        print(f"✓ Tiene _navbar: {type(dashboard._navbar)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creando PaginaAdmin:")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_pagina_admin_constructor()
    sys.exit(0 if result else 1)
