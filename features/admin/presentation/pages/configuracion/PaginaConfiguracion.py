"""Página de configuración del sistema para administradores"""
import flet as ft
from core.configuracion.ServicioConfiguracion import ServicioConfiguracion
from core.ui.colores import COLORES
from core.ui.safe_actions import safe_update


class PaginaConfiguracion:
    """Página para modificar configuraciones del sistema"""
    
    def __init__(self, pagina: ft.Page):
        self.pagina = pagina
        self.configuraciones = []
        
    def construir(self) -> ft.View:
        """Construye la vista de configuración"""
        
        # Cargar configuraciones
        self.configuraciones = ServicioConfiguracion.obtener_todas()
        
        # Agrupar por categoría
        categorias = {}
        for config in self.configuraciones:
            cat = config["categoria"] or "general"
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append(config)
        
        # Crear controles por categoría
        contenido = []
        
        for categoria, configs in categorias.items():
            # Título de categoría
            contenido.append(
                ft.Container(
                    content=ft.Text(
                        categoria.upper(),
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=COLORES.PRIMARIO
                    ),
                    margin=ft.margin.only(top=20, bottom=10)
                )
            )
            
            # Controles para cada configuración
            for config in configs:
                contenido.append(self._crear_control_config(config))
        
        return ft.View(
            "/admin/configuracion",
            controls=[
                ft.AppBar(
                    title=ft.Text("⚙️ Configuración del Sistema"),
                    bgcolor=COLORES.PRIMARIO,
                    color=ft.Colors.WHITE,
                ),
                ft.Container(
                    content=ft.Column(
                        contenido,
                        scroll=ft.ScrollMode.AUTO,
                        spacing=10,
                    ),
                    padding=20,
                    expand=True,
                ),
            ],
        )
    
    def _crear_control_config(self, config: dict) -> ft.Container:
        """Crea un control para editar una configuración"""
        
        clave = config["clave"]
        valor = config["valor"]
        tipo = config["tipo"]
        descripcion = config["descripcion"]
        
        # Campo de entrada según el tipo
        if tipo == "int":
            campo = ft.TextField(
                value=str(valor),
                label="Valor",
                keyboard_type=ft.KeyboardType.NUMBER,
                width=150,
                on_submit=lambda e, k=clave: self._guardar_config(k, e.control.value),
            )
        elif tipo == "bool":
            campo = ft.Switch(
                value=valor,
                on_change=lambda e, k=clave: self._guardar_config(k, e.control.value),
            )
        else:  # str
            campo = ft.TextField(
                value=str(valor),
                label="Valor",
                width=300,
                on_submit=lambda e, k=clave: self._guardar_config(k, e.control.value),
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(
                        clave.split(".")[-1].replace("_", " ").title(),
                        size=14,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Container(expand=True),
                    campo,
                ]),
                ft.Text(
                    descripcion,
                    size=12,
                    color=ft.Colors.BLACK54,
                    italic=True,
                ),
            ], spacing=5),
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.BLACK12),
            border_radius=8,
        )
    
    def _guardar_config(self, clave: str, valor: any):
        """Guarda el cambio de configuración"""
        exito = ServicioConfiguracion.actualizar_valor(clave, valor)
        
        if exito:
            # Limpiar cache para que se reflejen los cambios
            ServicioConfiguracion.limpiar_cache()
            
            # Mostrar mensaje de éxito
            snack = ft.SnackBar(
                content=ft.Text(
                    f"✅ Configuración '{clave}' actualizada a: {valor}",
                    color=ft.Colors.WHITE,
                ),
                bgcolor=COLORES.EXITO,
            )
            snack.open = True
            self.pagina.overlay.append(snack)
        else:
            # Mostrar error
            snack = ft.SnackBar(
                content=ft.Text(
                    f"❌ Error al actualizar '{clave}'",
                    color=ft.Colors.WHITE,
                ),
                bgcolor=COLORES.PELIGRO,
            )
            snack.open = True
            self.pagina.overlay.append(snack)
        
        safe_update(self.pagina)
