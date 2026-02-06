"""Widget overlay para configurar el sistema (400x400)"""
import flet as ft
from core.configuracion.ServicioConfiguracion import ServicioConfiguracion
from core.ui.colores import PRIMARIO, SECUNDARIO, EXITO, PELIGRO
from datetime import datetime


class OverlayConfiguracion:
    """Popup overlay 400x400 para configurar el sistema"""
    
    def __init__(self, pagina: ft.Page, usuario_id: int = None, categoria: str = None):
        self.pagina = pagina
        self.usuario_id = usuario_id
        self.categoria = categoria  # Filtrar por categoría (vouchers, pedidos, etc)
        self.overlay_container = None
        self.valores_originales = {}  # Guardar valores originales
        self.campos_actuales = {}  # Referencias a los campos para comparar
        
    def mostrar(self):
        """Muestra el overlay de configuración"""
        
        # Obtener configuraciones (filtradas por categoría si se especifica)
        configs = ServicioConfiguracion.obtener_todas(categoria=self.categoria)
        
        # Guardar valores originales
        self.valores_originales = {c["clave"]: c["valor"] for c in configs}
        
        # Controles de configuración
        controles_config = []
        
        for config in configs:
            control = self._crear_control(config)
            if control:
                controles_config.append(control)
        
        # Contenedor principal del diálogo
        dialogo = ft.Container(
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SETTINGS_ROUNDED, size=24, color=ft.Colors.WHITE),
                        ft.Text(
                            f"Configuración - {self.categoria.upper()}" if self.categoria else "Configuración",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE_ROUNDED,
                            icon_color=ft.Colors.WHITE,
                            on_click=lambda _: self.cerrar(),
                        ),
                    ]),
                    padding=15,
                    bgcolor=PRIMARIO,
                    border_radius=ft.border_radius.only(top_left=15, top_right=15),
                ),
                
                # Contenido scrollable
                ft.Container(
                    content=ft.Column(
                        controles_config,
                        spacing=10,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    padding=15,
                    height=250,
                ),
                
                # Footer con botones
                ft.Container(
                    content=ft.Row([
                        ft.Button(
                            "Ver Historial",
                            icon=ft.Icons.HISTORY_ROUNDED,
                            on_click=lambda _: self.mostrar_historial(),
                            bgcolor=SECUNDARIO,
                            color=ft.Colors.WHITE,
                        ),
                        ft.Container(expand=True),
                        ft.Button(
                            "Cerrar",
                            icon=ft.Icons.CHECK_ROUNDED,
                            on_click=lambda _: self.cerrar(),
                            bgcolor=EXITO,
                            color=ft.Colors.WHITE,
                        ),
                    ]),
                    padding=15,
                    bgcolor=ft.Colors.BLACK12,
                    border_radius=ft.border_radius.only(bottom_left=15, bottom_right=15),
                ),
            ], spacing=0, tight=True),
            width=400,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(
                blur_radius=50,
                spread_radius=0,
                color=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
                offset=ft.Offset(0, 15),
            ),
        )
        
        # Overlay con fondo semi-transparente
        self.overlay_container = ft.Container(
            content=dialogo,
            alignment=ft.Alignment(0, 0),
            bgcolor="#80000000",
            expand=True,
        )
        
        self.pagina.overlay.append(self.overlay_container)
        self.pagina.update()
    
    def _crear_control(self, config: dict) -> ft.Container:
        """Crea control para editar una configuración"""
        
        clave = config["clave"]
        valor = config["valor"]
        tipo = config["tipo"]
        descripcion = config["descripcion"]
        
        # Nombre amigable
        nombre = clave.split(".")[-1].replace("_", " ").title()
        
        # Campo según tipo
        if tipo == "int":
            campo = ft.TextField(
                value=str(valor),
                width=100,
                height=40,
                text_size=14,
                keyboard_type=ft.KeyboardType.NUMBER,
                on_submit=lambda e, k=clave: self._guardar(k, e.control.value),
            )
            # Guardar referencia al campo
            self.campos_actuales[clave] = campo
        elif tipo == "bool":
            campo = ft.Switch(
                value=valor,
                on_change=lambda e, k=clave: self._guardar(k, e.control.value),
            )
            self.campos_actuales[clave] = campo
        else:
            campo = ft.TextField(
                value=str(valor),
                width=150,
                height=40,
                text_size=14,
                on_submit=lambda e, k=clave: self._guardar(k, e.control.value),
            )
            self.campos_actuales[clave] = campo
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(nombre, size=13, weight=ft.FontWeight.W_500),
                    ft.Container(expand=True),
                    campo,
                ]),
                ft.Text(
                    descripcion,
                    size=11,
                    color=ft.Colors.BLACK54,
                    italic=True,
                ),
            ], spacing=3),
            padding=10,
            bgcolor=ft.Colors.BLACK12,
            border_radius=8,
        )
    
    def _guardar(self, clave: str, valor: any):
        """Guarda cambio de configuración"""
        exito = ServicioConfiguracion.actualizar_valor(clave, valor, self.usuario_id)
        
        if exito:
            # Actualizar el valor original después de guardar
            self.valores_originales[clave] = valor
            ServicioConfiguracion.limpiar_cache()
            self._mostrar_snackbar(f"✅ '{clave}' actualizado", EXITO)
        else:
            self._mostrar_snackbar(f"❌ Error al actualizar", PELIGRO)
    
    def _hay_cambios_sin_guardar(self) -> bool:
        """Verifica si hay cambios sin guardar en los campos"""
        for clave, campo in self.campos_actuales.items():
            valor_original = self.valores_originales.get(clave)
            
            # Obtener valor actual del campo
            if isinstance(campo, ft.TextField):
                valor_actual = campo.value
            elif isinstance(campo, ft.Switch):
                valor_actual = campo.value
            else:
                continue
            
            # Convertir a string para comparar
            if str(valor_actual) != str(valor_original):
                return True
        
        return False
    
    def cerrar(self):
        """Cierra el overlay (con confirmación si hay cambios)"""
        # Verificar si hay cambios sin guardar
        if self._hay_cambios_sin_guardar():
            self._mostrar_dialogo_confirmacion()
        else:
            self._cerrar_definitivo()
    
    def _cerrar_definitivo(self):
        """Cierra el overlay sin confirmación"""
        if self.overlay_container in self.pagina.overlay:
            self.pagina.overlay.remove(self.overlay_container)
            self.pagina.update()
    
    def _mostrar_dialogo_confirmacion(self):
        """Muestra diálogo de confirmación de cambios sin guardar"""
        
        dialogo = ft.Container(
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.WARNING_ROUNDED, size=24, color=ft.Colors.WHITE),
                        ft.Text(
                            "Cambios sin guardar",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                    ]),
                    padding=15,
                    bgcolor=PELIGRO,
                    border_radius=ft.border_radius.only(top_left=12, top_right=12),
                ),
                
                # Contenido
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Hay cambios sin guardar.",
                            size=14,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(
                            "¿Deseas cerrar sin guardar?",
                            size=13,
                            color=ft.Colors.BLACK54,
                        ),
                    ], spacing=5),
                    padding=20,
                ),
                
                # Botones
                ft.Container(
                    content=ft.Row([
                        ft.Button(
                            "Cancelar",
                            icon=ft.Icons.CLOSE_ROUNDED,
                            on_click=lambda _: self._cerrar_dialogo_confirmacion(),
                            bgcolor=ft.Colors.BLACK12,
                        ),
                        ft.Container(expand=True),
                        ft.Button(
                            "Cerrar sin guardar",
                            icon=ft.Icons.CHECK_ROUNDED,
                            on_click=lambda _: self._confirmar_cierre(),
                            bgcolor=PELIGRO,
                            color=ft.Colors.WHITE,
                        ),
                    ]),
                    padding=15,
                    bgcolor=ft.Colors.BLACK12,
                    border_radius=ft.border_radius.only(bottom_left=12, bottom_right=12),
                ),
            ], spacing=0, tight=True),
            width=350,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                blur_radius=30,
                spread_radius=0,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                offset=ft.Offset(0, 10),
            ),
        )
        
        # Crear overlay de confirmación
        self.dialogo_confirmacion = ft.Container(
            content=dialogo,
            alignment=ft.Alignment(0, 0),
            bgcolor="#80000000",
            expand=True,
        )
        
        self.pagina.overlay.append(self.dialogo_confirmacion)
        self.pagina.update()
    
    def _cerrar_dialogo_confirmacion(self):
        """Cierra el diálogo de confirmación"""
        if self.dialogo_confirmacion in self.pagina.overlay:
            self.pagina.overlay.remove(self.dialogo_confirmacion)
            self.pagina.update()
    
    def _confirmar_cierre(self):
        """Confirma el cierre sin guardar"""
        # Cerrar diálogo de confirmación
        self._cerrar_dialogo_confirmacion()
        # Cerrar overlay de configuración
        self._cerrar_definitivo()
    
    def mostrar_historial(self):
        """Muestra el historial de cambios"""
        self.cerrar()
        historial = OverlayHistorialConfig(self.pagina)
        historial.mostrar()
    
    def _mostrar_snackbar(self, mensaje: str, color: str):
        """Muestra un snackbar"""
        snack = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=color,
        )
        snack.open = True
        self.pagina.overlay.append(snack)
        self.pagina.update()


class OverlayHistorialConfig:
    """Popup overlay para ver historial de cambios de configuración"""
    
    def __init__(self, pagina: ft.Page):
        self.pagina = pagina
        self.overlay_container = None
        
    def mostrar(self):
        """Muestra el historial de cambios"""
        
        # Obtener historial
        historial = ServicioConfiguracion.obtener_historial(limite=50)
        
        # Crear filas de la tabla
        filas = []
        for log in historial:
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(log["clave"].split(".")[-1], size=11)),
                        ft.DataCell(ft.Text(str(log["valor_anterior"] or "-"), size=11)),
                        ft.DataCell(ft.Text(str(log["valor_nuevo"]), size=11, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(log["usuario_nombre"], size=11)),
                        ft.DataCell(ft.Text(
                            log["fecha"].strftime("%d/%m %H:%M") if log["fecha"] else "-",
                            size=11
                        )),
                    ]
                )
            )
        
        # Tabla de historial
        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Config", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Anterior", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nuevo", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Usuario", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fecha", size=12, weight=ft.FontWeight.BOLD)),
            ],
            rows=filas,
            border=ft.Border.all(1, ft.Colors.BLACK12),
            border_radius=8,
            vertical_lines=ft.border.BorderSide(1, ft.Colors.BLACK12),
            heading_row_color=ft.Colors.BLACK12,
        )
        
        # Contenedor principal
        dialogo = ft.Container(
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.HISTORY_ROUNDED, size=24, color=ft.Colors.WHITE),
                        ft.Text(
                            "Historial de Cambios",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE_ROUNDED,
                            icon_color=ft.Colors.WHITE,
                            on_click=lambda _: self.cerrar(),
                        ),
                    ]),
                    padding=15,
                    bgcolor=SECUNDARIO,
                    border_radius=ft.border_radius.only(top_left=15, top_right=15),
                ),
                
                # Tabla scrollable
                ft.Container(
                    content=ft.Column([tabla], scroll=ft.ScrollMode.AUTO),
                    padding=15,
                    height=450,
                ),
                
                # Footer
                ft.Container(
                    content=ft.Row([
                        ft.Text(
                            f"Total: {len(historial)} cambios",
                            size=12,
                            color=ft.Colors.BLACK54,
                        ),
                        ft.Container(expand=True),
                        ft.Button(
                            "Cerrar",
                            icon=ft.Icons.CLOSE_ROUNDED,
                            on_click=lambda _: self.cerrar(),
                            bgcolor=PRIMARIO,
                            color=ft.Colors.WHITE,
                        ),
                    ]),
                    padding=15,
                    bgcolor=ft.Colors.BLACK12,
                    border_radius=ft.border_radius.only(bottom_left=15, bottom_right=15),
                ),
            ], spacing=0, tight=True),
            width=700,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(
                blur_radius=50,
                spread_radius=0,
                color=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
                offset=ft.Offset(0, 15),
            ),
        )
        
        # Overlay
        self.overlay_container = ft.Container(
            content=dialogo,
            alignment=ft.Alignment(0, 0),
            bgcolor="#80000000",
            expand=True,
        )
        
        self.pagina.overlay.append(self.overlay_container)
        self.pagina.update()
    
    def cerrar(self):
        """Cierra el overlay"""
        if self.overlay_container in self.pagina.overlay:
            self.pagina.overlay.remove(self.overlay_container)
            self.pagina.update()
