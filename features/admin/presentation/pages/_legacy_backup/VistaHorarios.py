"""
Vista de gestión de horarios de sucursales con CRUD completo en popups
"""
import flet as ft
from features.admin.presentation.widgets.VistaBase import VistaBase
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_HORARIO, MODELO_SUCURSAL
from core.Constantes import COLORES, TAMANOS


class VistaHorarios(VistaBase):
    
    def __init__(self, pagina: ft.Page, usuario, on_volver_inicio):
        super().__init__(pagina=pagina, usuario=usuario, titulo="Gestión de Horarios", on_volver_inicio=on_volver_inicio, mostrar_boton_volver=True)
        self._tabla = None
        self._cargar_vista()
    
    def _cargar_vista(self):
        boton_nuevo = ft.ElevatedButton("➕ Nuevo Horario", icon=ft.Icons.SCHEDULE, on_click=self._abrir_popup_crear, bgcolor=COLORES.PRIMARIO, color=COLORES.TEXTO_BLANCO)
        
        self._tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Sucursal", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Día", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Hora Apertura", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Hora Cierre", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_MD,
            vertical_lines=ft.BorderSide(1, COLORES.BORDE),
            heading_row_color=COLORES.PRIMARIO_CLARO,
        )
        
        self.establecer_contenido([ft.Row([boton_nuevo]), ft.Container(content=ft.Column([self._tabla], scroll=ft.ScrollMode.AUTO), bgcolor=COLORES.FONDO_BLANCO, border_radius=TAMANOS.RADIO_MD, padding=TAMANOS.PADDING_MD)])
        self._cargar_datos()
    
    def _cargar_datos(self):
        sesion = OBTENER_SESION()
        items = sesion.query(MODELO_HORARIO).all()
        self._tabla.rows.clear()
        for item in items:
            sucursal_nombre = item.SUCURSAL.NOMBRE if item.SUCURSAL else "Sin sucursal"
            
            self._tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(item.ID))),
                    ft.DataCell(ft.Text(sucursal_nombre)),
                    ft.DataCell(ft.Text(item.DIA_SEMANA)),
                    ft.DataCell(ft.Text(item.HORA_APERTURA or "-")),
                    ft.DataCell(ft.Text(item.HORA_CIERRE or "-")),
                    ft.DataCell(ft.Row([
                        ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar", icon_color=COLORES.INFO, on_click=lambda e, i=item: self._abrir_popup_editar(i)),
                        ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar", icon_color=COLORES.PELIGRO, on_click=lambda e, i=item: self._confirmar_eliminar(i)),
                    ])),
                ])
            )
        sesion.close()
        self.actualizar_ui()
    
    def _abrir_popup_crear(self, e):
        sesion = OBTENER_SESION()
        sucursales = sesion.query(MODELO_SUCURSAL).all()
        sesion.close()
        
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        campo_sucursal = ft.Dropdown(label="Sucursal", options=[ft.dropdown.Option(str(s.ID), s.NOMBRE) for s in sucursales])
        campo_dia = ft.Dropdown(label="Día de la Semana", options=[ft.dropdown.Option(d) for d in dias])
        campo_apertura = ft.TextField(label="Hora Apertura (HH:MM)", prefix_icon=ft.Icons.ACCESS_TIME, hint_text="08:00")
        campo_cierre = ft.TextField(label="Hora Cierre (HH:MM)", prefix_icon=ft.Icons.ACCESS_TIME_FILLED, hint_text="22:00")
        
        def guardar(e):
            if not campo_sucursal.value or not campo_dia.value:
                self.mostrar_snackbar("Sucursal y día son obligatorios", es_error=True)
                return
            try:
                sesion = OBTENER_SESION()
                nuevo = MODELO_HORARIO(
                    SUCURSAL_ID=int(campo_sucursal.value),
                    DIA_SEMANA=campo_dia.value,
                    HORA_APERTURA=campo_apertura.value,
                    HORA_CIERRE=campo_cierre.value
                )
                sesion.add(nuevo)
                sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Horario creado exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("➕ Nuevo Horario", color=COLORES.TEXTO),
            content=ft.Container(content=ft.Column([campo_sucursal, campo_dia, campo_apertura, campo_cierre], tight=True, spacing=TAMANOS.ESPACIADO_MD), width=400),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()), ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=guardar, bgcolor=COLORES.PRIMARIO, color=COLORES.TEXTO_BLANCO)]
        )
        self.mostrar_dialogo(dialogo)
    
    def _abrir_popup_editar(self, item):
        sesion = OBTENER_SESION()
        sucursales = sesion.query(MODELO_SUCURSAL).all()
        sesion.close()
        
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        campo_sucursal = ft.Dropdown(label="Sucursal", value=str(item.SUCURSAL_ID) if item.SUCURSAL_ID else None, options=[ft.dropdown.Option(str(s.ID), s.NOMBRE) for s in sucursales])
        campo_dia = ft.Dropdown(label="Día de la Semana", value=item.DIA_SEMANA, options=[ft.dropdown.Option(d) for d in dias])
        campo_apertura = ft.TextField(label="Hora Apertura (HH:MM)", value=item.HORA_APERTURA or "")
        campo_cierre = ft.TextField(label="Hora Cierre (HH:MM)", value=item.HORA_CIERRE or "")
        
        def guardar(e):
            try:
                sesion = OBTENER_SESION()
                item_bd = sesion.query(MODELO_HORARIO).filter_by(ID=item.ID).first()
                if item_bd:
                    item_bd.SUCURSAL_ID = int(campo_sucursal.value) if campo_sucursal.value else None
                    item_bd.DIA_SEMANA = campo_dia.value
                    item_bd.HORA_APERTURA = campo_apertura.value
                    item_bd.HORA_CIERRE = campo_cierre.value
                    sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Horario actualizado exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text(f"✏️ Editar: {item.DIA_SEMANA}", color=COLORES.TEXTO),
            content=ft.Container(content=ft.Column([campo_sucursal, campo_dia, campo_apertura, campo_cierre], tight=True, spacing=TAMANOS.ESPACIADO_MD), width=400),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()), ft.ElevatedButton("Actualizar", icon=ft.Icons.SAVE, on_click=guardar, bgcolor=COLORES.INFO, color=COLORES.TEXTO_BLANCO)]
        )
        self.mostrar_dialogo(dialogo)
    
    def _confirmar_eliminar(self, item):
        def eliminar(e):
            try:
                sesion = OBTENER_SESION()
                item_bd = sesion.query(MODELO_HORARIO).filter_by(ID=item.ID).first()
                if item_bd:
                    sesion.delete(item_bd)
                    sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Horario eliminado exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("⚠️ Confirmar Eliminación", color=COLORES.PELIGRO),
            content=ft.Text(f"¿Eliminar horario de {item.DIA_SEMANA}?\n\nEsta acción no se puede deshacer."),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()), ft.ElevatedButton("Eliminar", icon=ft.Icons.DELETE_FOREVER, on_click=eliminar, bgcolor=COLORES.PELIGRO, color=COLORES.TEXTO_BLANCO)]
        )
        self.mostrar_dialogo(dialogo)
