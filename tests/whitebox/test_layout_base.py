"""
White Box Testing - LayoutBase
Pruebas de caja blanca que conocen la implementación interna
"""
import pytest
import flet as ft
from features.admin.presentation.widgets.LayoutBase import LayoutBase
from features.autenticacion.domain.entities.Usuario import Usuario


class TestLayoutBaseWhiteBox:
    """Pruebas de estructura interna de LayoutBase"""
    
    def test_herencia_correcta(self):
        """Verifica que LayoutBase hereda de ft.Column"""
        assert issubclass(LayoutBase, ft.Column)
    
    def test_atributos_privados_inicializados(self):
        """Verifica que todos los atributos privados se inicializan"""
        page = ft.Page()
        usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test")
        
        layout = LayoutBase(
            pagina=page,
            usuario=usuario,
            titulo_vista="Test"
        )
        
        # Atributos privados
        assert hasattr(layout, '_pagina')
        assert hasattr(layout, '_usuario')
        assert hasattr(layout, '_titulo_vista')
        assert hasattr(layout, '_navbar')
        assert hasattr(layout, '_bottom_nav')
        assert hasattr(layout, '_contenido_container')
        assert hasattr(layout, '_gesture_detector')
    
    def test_metodo_construir_existe(self):
        """Verifica que el método construir() existe y es callable"""
        assert hasattr(LayoutBase, 'construir')
        assert callable(getattr(LayoutBase, 'construir'))
    
    def test_callbacks_opcionales(self):
        """Verifica que los callbacks son opcionales"""
        page = ft.Page()
        usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test")
        
        # Sin callbacks
        layout = LayoutBase(pagina=page, usuario=usuario)
        assert layout._on_volver_dashboard is None
        assert layout._on_cerrar_sesion is None
    
    def test_spacing_y_expand_configurados(self):
        """Verifica configuración de spacing y expand"""
        page = ft.Page()
        usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test")
        
        layout = LayoutBase(pagina=page, usuario=usuario)
        assert layout.spacing == 0
        assert layout.expand is True


class TestLayoutBaseInternalMethods:
    """Pruebas de métodos internos"""
    
    def test_on_sucursales_change_default(self):
        """Verifica que _on_sucursales_change por defecto no hace nada"""
        page = ft.Page()
        usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test")
        
        layout = LayoutBase(pagina=page, usuario=usuario)
        
        # No debe lanzar error
        try:
            layout._on_sucursales_change([1, 2, 3])
            layout._on_sucursales_change(None)
        except Exception as e:
            pytest.fail(f"_on_sucursales_change lanzó error: {e}")
    
    def test_obtener_sucursales_seleccionadas(self):
        """Verifica que obtener_sucursales_seleccionadas funciona"""
        page = ft.Page()
        usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test")
        
        layout = LayoutBase(pagina=page, usuario=usuario)
        
        # Por defecto None (todas)
        result = layout.obtener_sucursales_seleccionadas()
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
