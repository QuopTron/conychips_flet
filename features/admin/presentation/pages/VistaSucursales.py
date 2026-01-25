"""
Vista de gestión de sucursales con CRUD completo en popups
"""
import flet as ft
from features.admin.presentation.widgets.VistaBase import VistaBase
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_SUCURSAL
from core.Constantes import COLORES, TAMANOS, ICONOS


class VistaSucursales(VistaBase):
    """Vista para gestionar sucursales con CRUDs en popups"""
    
    def __init__(self, pagina: ft.Page, usuario, on_volver_inicio):
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo="Gestión de Sucursales",
            on_volver_inicio=on_volver_inicio,
            mostrar_boton_volver=True
        )
        self._tabla = None
        self._cargar_vista()
    
    def _cargar_vista(self):
        """Carga la interfaz"""
        boton_nuevo = ft.ElevatedButton(
            "➕ Nueva Sucursal",
            icon=ft.Icons.STORE,
            on_click=self._abrir_popup_crear,
            bgcolor=COLORES.PRIMARIO,
            color=COLORES.TEXTO_BLANCO,
        )
        
        self._tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Dirección", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Teléfono", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_MD,
            vertical_lines=ft.BorderSide(1, COLORES.BORDE),
            heading_row_color=COLORES.PRIMARIO_CLARO,
        )
        
        self.establecer_contenido([
            ft.Row([boton_nuevo]),
            ft.Container(
                content=self._tabla,
                bgcolor=COLORES.FONDO_BLANCO,
                border_radius=TAMANOS.RADIO_MD,
                padding=TAMANOS.PADDING_MD,
            )
        ])
        
        self._cargar_datos()
    
    def _cargar_datos(self):
        """Carga sucursales desde BD"""
        sesion = OBTENER_SESION()
        items = sesion.query(MODELO_SUCURSAL).all()
        
        self._tabla.rows.clear()
        for item in items:
            self._tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(item.ID))),
                        ft.DataCell(ft.Text(item.NOMBRE)),
                        ft.DataCell(ft.Text(item.DIRECCION or "-")),
                        ft.DataCell(ft.Text(item.TELEFONO or "-")),
                        ft.DataCell(ft.Row([
                            ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar", icon_color=COLORES.INFO, on_click=lambda e, i=item: self._abrir_popup_editar(i)),
                            ft.IconButton(icon=ft.Icons.DELETE, tooltip="Eliminar", icon_color=COLORES.PELIGRO, on_click=lambda e, i=item: self._confirmar_eliminar(i)),
                        ])),
                    ]
                )
            )
        
        sesion.close()
        self.actualizar_ui()
    
    def _abrir_popup_crear(self, e):
        campo_nombre = ft.TextField(label="Nombre", prefix_icon=ft.Icons.STORE)
        campo_direccion = ft.TextField(label="Dirección", prefix_icon=ft.Icons.LOCATION_ON)
        campo_telefono = ft.TextField(label="Teléfono", prefix_icon=ft.Icons.PHONE)
        
        def guardar(e):
            if not campo_nombre.value:
                self.mostrar_snackbar("El nombre es obligatorio", es_error=True)
                return
            
            try:
                sesion = OBTENER_SESION()
                nuevo = MODELO_SUCURSAL(NOMBRE=campo_nombre.value, DIRECCION=campo_direccion.value, TELEFONO=campo_telefono.value)
                sesion.add(nuevo)
                sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Sucursal creada exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("➕ Nueva Sucursal", color=COLORES.TEXTO),
            content=ft.Container(content=ft.Column([campo_nombre, campo_direccion, campo_telefono], tight=True, spacing=TAMANOS.ESPACIADO_MD), width=400),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()),
                ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=guardar, bgcolor=COLORES.PRIMARIO, color=COLORES.TEXTO_BLANCO)
            ]
        )
        self.mostrar_dialogo(dialogo)
    
    def _abrir_popup_editar(self, item):
        campo_nombre = ft.TextField(label="Nombre", value=item.NOMBRE, prefix_icon=ft.Icons.STORE)
        campo_direccion = ft.TextField(label="Dirección", value=item.DIRECCION or "", prefix_icon=ft.Icons.LOCATION_ON)
        campo_telefono = ft.TextField(label="Teléfono", value=item.TELEFONO or "", prefix_icon=ft.Icons.PHONE)
        
        def guardar(e):
            try:
                sesion = OBTENER_SESION()
                item_bd = sesion.query(MODELO_SUCURSAL).filter_by(ID=item.ID).first()
                if item_bd:
                    item_bd.NOMBRE = campo_nombre.value
                    item_bd.DIRECCION = campo_direccion.value
                    item_bd.TELEFONO = campo_telefono.value
                    sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Sucursal actualizada exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text(f"✏️ Editar: {item.NOMBRE}", color=COLORES.TEXTO),
            content=ft.Container(content=ft.Column([campo_nombre, campo_direccion, campo_telefono], tight=True, spacing=TAMANOS.ESPACIADO_MD), width=400),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()),
                ft.ElevatedButton("Actualizar", icon=ft.Icons.SAVE, on_click=guardar, bgcolor=COLORES.INFO, color=COLORES.TEXTO_BLANCO)
            ]
        )
        self.mostrar_dialogo(dialogo)
    
    def _confirmar_eliminar(self, item):
        def eliminar(e):
            try:
                sesion = OBTENER_SESION()
                item_bd = sesion.query(MODELO_SUCURSAL).filter_by(ID=item.ID).first()
                if item_bd:
                    sesion.delete(item_bd)
                    sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Sucursal eliminada exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("⚠️ Confirmar Eliminación", color=COLORES.PELIGRO),
            content=ft.Text(f"¿Eliminar sucursal '{item.NOMBRE}'?\n\nEsta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()),
                ft.ElevatedButton("Eliminar", icon=ft.Icons.DELETE_FOREVER, on_click=eliminar, bgcolor=COLORES.PELIGRO, color=COLORES.TEXTO_BLANCO)
            ]
        )
        self.mostrar_dialogo(dialogo)
