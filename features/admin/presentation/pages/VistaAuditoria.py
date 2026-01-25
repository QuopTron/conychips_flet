"""
Vista de auditoría y logs del sistema (solo lectura)
"""
import flet as ft
from features.admin.presentation.widgets.VistaBase import VistaBase
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_LOG_AUDITORIA
from core.Constantes import COLORES, TAMANOS


class VistaAuditoria(VistaBase):
    
    def __init__(self, pagina: ft.Page, usuario, on_volver_inicio):
        super().__init__(pagina=pagina, usuario=usuario, titulo="Auditoría del Sistema", on_volver_inicio=on_volver_inicio, mostrar_boton_volver=True)
        self._tabla = None
        self._filtro_tipo = None
        self._cargar_vista()
    
    def _cargar_vista(self):
        self._filtro_tipo = ft.Dropdown(
            label="Filtrar por Tipo",
            options=[
                ft.dropdown.Option("TODOS", "Todos"),
                ft.dropdown.Option("LOGIN", "Login"),
                ft.dropdown.Option("LOGOUT", "Logout"),
                ft.dropdown.Option("CREATE", "Crear"),
                ft.dropdown.Option("UPDATE", "Actualizar"),
                ft.dropdown.Option("DELETE", "Eliminar"),
                ft.dropdown.Option("ERROR", "Errores"),
            ],
            value="TODOS",
            on_change=lambda e: self._cargar_datos()
        )
        
        boton_refrescar = ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Refrescar", on_click=lambda e: self._cargar_datos())
        
        self._tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acción", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tabla", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("IP", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_MD,
            vertical_lines=ft.BorderSide(1, COLORES.BORDE),
            heading_row_color=COLORES.PRIMARIO_CLARO,
        )
        
        self.establecer_contenido([
            ft.Row([self._filtro_tipo, boton_refrescar]),
            ft.Container(
                content=ft.Column([self._tabla], scroll=ft.ScrollMode.AUTO, height=500),
                bgcolor=COLORES.FONDO_BLANCO,
                border_radius=TAMANOS.RADIO_MD,
                padding=TAMANOS.PADDING_MD
            )
        ])
        self._cargar_datos()
    
    def _cargar_datos(self):
        sesion = OBTENER_SESION()
        query = sesion.query(MODELO_LOG_AUDITORIA).order_by(MODELO_LOG_AUDITORIA.FECHA.desc())
        
        if self._filtro_tipo.value != "TODOS":
            query = query.filter(MODELO_LOG_AUDITORIA.TIPO == self._filtro_tipo.value)
        
        items = query.limit(100).all()
        self._tabla.rows.clear()
        
        for item in items:
            usuario_nombre = item.USUARIO.NOMBRE_USUARIO if item.USUARIO else "Sistema"
            
            color_tipo = COLORES.INFO
            if item.TIPO == "ERROR":
                color_tipo = COLORES.PELIGRO
            elif item.TIPO == "DELETE":
                color_tipo = COLORES.ADVERTENCIA
            elif item.TIPO in ["LOGIN", "CREATE"]:
                color_tipo = COLORES.EXITO
            
            self._tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(item.ID))),
                    ft.DataCell(ft.Text(item.TIPO, color=color_tipo, weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(usuario_nombre)),
                    ft.DataCell(ft.Text(item.ACCION or "-")),
                    ft.DataCell(ft.Text(item.TABLA_AFECTADA or "-")),
                    ft.DataCell(ft.Text(item.IP_ORIGEN or "-")),
                    ft.DataCell(ft.Text(item.FECHA.strftime("%d/%m/%Y %H:%M:%S") if item.FECHA else "-")),
                ])
            )
        sesion.close()
        self.actualizar_ui()
