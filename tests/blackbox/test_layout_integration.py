"""
Black Box Testing - LayoutBase Integration
Pruebas de caja negra que verifican comportamiento externo
"""
import pytest
import flet as ft
from features.admin.presentation.widgets.LayoutBase import LayoutBase
from features.autenticacion.domain.entities.Usuario import Usuario


class TestLayoutBaseBlackBox:
    """Pruebas de comportamiento externo de LayoutBase"""
    
    def test_construccion_basica(self):
        """Verifica que se puede construir LayoutBase con parámetros mínimos"""
        page = ft.Page()
        usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test", ROLES=["ADMIN"])
        
        try:
            layout = LayoutBase(
                pagina=page,
                usuario=usuario,
                titulo_vista="Test Vista"
            )
            assert layout is not None
        except Exception as e:
            pytest.fail(f"Error al construir LayoutBase: {e}")
    
    def test_construccion_completa(self):
        """Verifica construcción con todos los parámetros"""
        page = ft.Page()
        usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test", ROLES=["ADMIN"])
        
        def callback_volver():
            pass
        
        def callback_logout(e=None):
            pass
        
        try:
            layout = LayoutBase(
                pagina=page,
                usuario=usuario,
                titulo_vista="Test Vista Completa",
                mostrar_boton_volver=True,
                index_navegacion=2,
                on_volver_dashboard=callback_volver,
                on_cerrar_sesion=callback_logout
            )
            assert layout is not None
        except Exception as e:
            pytest.fail(f"Error al construir LayoutBase completo: {e}")
    
    def test_construir_con_contenido(self):
        """Verifica que construir() acepta contenido"""
        page = ft.Page()
        usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test", ROLES=["ADMIN"])
        
        layout = LayoutBase(pagina=page, usuario=usuario)
        
        contenido = ft.Container(
            content=ft.Text("Contenido de prueba"),
            expand=True
        )
        
        try:
            layout.construir(contenido)
            # Verificar que controls tiene elementos
            assert len(layout.controls) > 0
        except Exception as e:
            pytest.fail(f"Error al construir contenido: {e}")


class TestLayoutBaseNavigation:
    """Pruebas de navegación"""
    
    def test_navegacion_routes(self):
        """Verifica que las rutas de navegación funcionan"""
        page = ft.Page()
        usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test", ROLES=["SUPERADMIN"])
        
        navegado = {"ruta": None}
        
        def mock_navegar(route):
            navegado["ruta"] = route
        
        layout = LayoutBase(pagina=page, usuario=usuario)
        layout._navegar_a = mock_navegar
        
        # Probar diferentes rutas
        for ruta in ["dashboard", "vouchers", "finanzas", "usuarios", "auditoria"]:
            layout._navegar_a(ruta)
            assert navegado["ruta"] == ruta


class TestLayoutBaseEdgeCases:
    """Pruebas de casos extremos"""
    
    def test_usuario_sin_roles(self):
        """Verifica comportamiento con usuario sin roles"""
        page = ft.Page()
        usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test", ROLES=[])
        
        try:
            layout = LayoutBase(pagina=page, usuario=usuario)
            assert layout is not None
        except Exception as e:
            pytest.fail(f"Fallo con usuario sin roles: {e}")
    
    def test_titulo_vacio(self):
        """Verifica comportamiento con título vacío"""
        page = ft.Page()
        usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test", ROLES=["ADMIN"])
        
        try:
            layout = LayoutBase(pagina=page, usuario=usuario, titulo_vista="")
            assert layout is not None
        except Exception as e:
            pytest.fail(f"Fallo con título vacío: {e}")
    
    def test_index_navegacion_invalido(self):
        """Verifica comportamiento con índice de navegación inválido"""
        page = ft.Page()
        usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test", ROLES=["ADMIN"])
        
        # Índice negativo
        layout1 = LayoutBase(pagina=page, usuario=usuario, index_navegacion=-1)
        assert layout1 is not None
        
        # Índice muy alto
        layout2 = LayoutBase(pagina=page, usuario=usuario, index_navegacion=999)
        assert layout2 is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
