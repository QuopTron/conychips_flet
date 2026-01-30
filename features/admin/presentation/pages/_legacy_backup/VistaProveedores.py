import flet as ft
from features.admin.presentation.widgets.VistaBase import VistaBase
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_PROVEEDOR
from core.Constantes import COLORES, TAMANOS

class VistaProveedores(VistaBase):
    
    def __init__(self, pagina: ft.Page, usuario, on_volver_inicio):
        super().__init__(pagina=pagina, usuario=usuario, titulo="Gestión de Proveedores", on_volver_inicio=on_volver_inicio, mostrar_boton_volver=True)
        self._tabla = None
        self._cargar_vista()
    
    def _cargar_vista(self):
        boton_nuevo = ft.Button("➕ Nuevo Proveedor", icon=ft.icons.Icons.Icons.BUSINESS, on_click=self._abrir_popup_crear, bgcolor=COLORES.PRIMARIO, color=COLORES.TEXTO_BLANCO)
        
        self._tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Contacto", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Teléfono", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Email", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.Border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_MD,
            vertical_lines=ft.BorderSide(1, COLORES.BORDE),
            heading_row_color=COLORES.PRIMARIO_CLARO,
        )
        
        self.establecer_contenido([ft.Row([boton_nuevo]), ft.Container(content=self._tabla, bgcolor=COLORES.FONDO_BLANCO, border_radius=TAMANOS.RADIO_MD, padding=TAMANOS.PADDING_MD)])
        self._cargar_datos()
    
    def _cargar_datos(self):
        sesion = OBTENER_SESION()
        items = sesion.query(MODELO_PROVEEDOR).all()
        self._tabla.rows.clear()
        for item in items:
            self._tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(item.ID))),
                    ft.DataCell(ft.Text(item.NOMBRE)),
                    ft.DataCell(ft.Text(item.CONTACTO or "-")),
                    ft.DataCell(ft.Text(item.TELEFONO or "-")),
                    ft.DataCell(ft.Text(item.EMAIL or "-")),
                    ft.DataCell(ft.Row([
                        ft.IconButton(icon=ft.icons.Icons.Icons.EDIT, tooltip="Editar", icon_color=COLORES.INFO, on_click=lambda e, i=item: self._abrir_popup_editar(i)),
                        ft.IconButton(icon=ft.icons.Icons.Icons.DELETE, tooltip="Eliminar", icon_color=COLORES.PELIGRO, on_click=lambda e, i=item: self._confirmar_eliminar(i)),
                    ])),
                ])
            )
        sesion.close()
        self.actualizar_ui()
    
    def _abrir_popup_crear(self, e):
        campo_nombre = ft.TextField(label="Nombre de la Empresa", prefix_icon=ft.icons.Icons.Icons.BUSINESS)
        campo_contacto = ft.TextField(label="Persona de Contacto", prefix_icon=ft.icons.Icons.Icons.PERSON)
        campo_telefono = ft.TextField(label="Teléfono", prefix_icon=ft.icons.Icons.Icons.PHONE)
        campo_email = ft.TextField(label="Email", prefix_icon=ft.icons.Icons.Icons.EMAIL, keyboard_type=ft.KeyboardType.EMAIL)
        
        def guardar(e):
            if not campo_nombre.value:
                self.mostrar_snackbar("Nombre es obligatorio", es_error=True)
                return
            try:
                sesion = OBTENER_SESION()
                nuevo = MODELO_PROVEEDOR(
                    NOMBRE=campo_nombre.value,
                    CONTACTO=campo_contacto.value,
                    TELEFONO=campo_telefono.value,
                    EMAIL=campo_email.value
                )
                sesion.add(nuevo)
                sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Proveedor creado exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("➕ Nuevo Proveedor", color=COLORES.TEXTO),
            content=ft.Container(content=ft.Column([campo_nombre, campo_contacto, campo_telefono, campo_email], tight=True, spacing=TAMANOS.ESPACIADO_MD), width=400),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()), ft.Button("Guardar", icon=ft.icons.Icons.Icons.SAVE, on_click=guardar, bgcolor=COLORES.PRIMARIO, color=COLORES.TEXTO_BLANCO)]
        )
        self.mostrar_dialogo(dialogo)
    
    def _abrir_popup_editar(self, item):
        campo_nombre = ft.TextField(label="Nombre de la Empresa", value=item.NOMBRE, prefix_icon=ft.icons.Icons.Icons.BUSINESS)
        campo_contacto = ft.TextField(label="Persona de Contacto", value=item.CONTACTO or "", prefix_icon=ft.icons.Icons.Icons.PERSON)
        campo_telefono = ft.TextField(label="Teléfono", value=item.TELEFONO or "", prefix_icon=ft.icons.Icons.Icons.PHONE)
        campo_email = ft.TextField(label="Email", value=item.EMAIL or "", prefix_icon=ft.icons.Icons.Icons.EMAIL)
        
        def guardar(e):
            try:
                sesion = OBTENER_SESION()
                item_bd = sesion.query(MODELO_PROVEEDOR).filter_by(ID=item.ID).first()
                if item_bd:
                    item_bd.NOMBRE = campo_nombre.value
                    item_bd.CONTACTO = campo_contacto.value
                    item_bd.TELEFONO = campo_telefono.value
                    item_bd.EMAIL = campo_email.value
                    sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Proveedor actualizado exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text(f"✏️ Editar: {item.NOMBRE}", color=COLORES.TEXTO),
            content=ft.Container(content=ft.Column([campo_nombre, campo_contacto, campo_telefono, campo_email], tight=True, spacing=TAMANOS.ESPACIADO_MD), width=400),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()), ft.Button("Actualizar", icon=ft.icons.Icons.Icons.SAVE, on_click=guardar, bgcolor=COLORES.INFO, color=COLORES.TEXTO_BLANCO)]
        )
        self.mostrar_dialogo(dialogo)
    
    def _confirmar_eliminar(self, item):
        def eliminar(e):
            try:
                sesion = OBTENER_SESION()
                item_bd = sesion.query(MODELO_PROVEEDOR).filter_by(ID=item.ID).first()
                if item_bd:
                    sesion.delete(item_bd)
                    sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Proveedor eliminado exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("⚠️ Confirmar Eliminación", color=COLORES.PELIGRO),
            content=ft.Text(f"¿Eliminar proveedor '{item.NOMBRE}'?\n\nEsta acción no se puede deshacer."),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()), ft.Button("Eliminar", icon=ft.icons.Icons.Icons.DELETE_FOREVER, on_click=eliminar, bgcolor=COLORES.PELIGRO, color=COLORES.TEXTO_BLANCO)]
        )
        self.mostrar_dialogo(dialogo)
