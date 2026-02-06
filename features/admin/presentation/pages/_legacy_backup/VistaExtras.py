import flet as ft
from features.admin.presentation.widgets.VistaBase import VistaBase
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_EXTRA
from core.Constantes import COLORES, TAMANOS

class VistaExtras(VistaBase):
    
    def __init__(self, pagina: ft.Page, usuario, on_volver_inicio):
        super().__init__(pagina=pagina, usuario=usuario, titulo="Gestión de Extras", on_volver_inicio=on_volver_inicio, mostrar_boton_volver=True)
        self._tabla = None
        self._cargar_vista()
    
    def _cargar_vista(self):
        boton_nuevo = ft.Button("➕ Nuevo Extra", icon=ft.icons.Icons.Icons.ADD_CIRCLE, on_click=self._abrir_popup_crear, bgcolor=COLORES.PRIMARIO, color=COLORES.TEXTO_BLANCO)
        
        self._tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Descripción", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Precio Adicional", weight=ft.FontWeight.BOLD)),
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
        items = sesion.query(MODELO_EXTRA).all()
        self._tabla.rows.clear()
        for item in items:
            self._tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(item.ID))),
                    ft.DataCell(ft.Text(item.NOMBRE)),
                    ft.DataCell(ft.Text(item.DESCRIPCION or "-")),
                    ft.DataCell(ft.Text(f"${item.PRECIO_ADICIONAL / 100:.2f}")),
                    ft.DataCell(ft.Row([
                        ft.IconButton(icon=ft.icons.Icons.Icons.EDIT, tooltip="Editar", icon_color=COLORES.INFO, on_click=lambda e, i=item: self._abrir_popup_editar(i)),
                        ft.IconButton(icon=ft.icons.Icons.Icons.DELETE, tooltip="Eliminar", icon_color=COLORES.PELIGRO, on_click=lambda e, i=item: self._confirmar_eliminar(i)),
                    ])),
                ])
            )
        sesion.close()
        self.actualizar_ui()
    
    def _abrir_popup_crear(self, e):
        campo_nombre = ft.TextField(label="Nombre", prefix_icon=ft.icons.Icons.Icons.ADD_CIRCLE)
        campo_descripcion = ft.TextField(label="Descripción", multiline=True)
        campo_precio = ft.TextField(label="Precio Adicional (centavos)", prefix_icon=ft.icons.Icons.Icons.ATTACH_MONEY, keyboard_type=ft.KeyboardType.NUMBER)
        
        def guardar(e):
            if not campo_nombre.value or not campo_precio.value:
                self.mostrar_snackbar("Nombre y precio son obligatorios", es_error=True)
                return
            try:
                sesion = OBTENER_SESION()
                nuevo = MODELO_EXTRA(NOMBRE=campo_nombre.value, DESCRIPCION=campo_descripcion.value, PRECIO_ADICIONAL=int(campo_precio.value))
                sesion.add(nuevo)
                sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Extra creado exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("➕ Nuevo Extra", color=COLORES.TEXTO),
            content=ft.Container(content=ft.Column([campo_nombre, campo_descripcion, campo_precio], tight=True, spacing=TAMANOS.ESPACIADO_MD), width=400),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()), ft.Button("Guardar", icon=ft.icons.Icons.Icons.SAVE, on_click=guardar, bgcolor=COLORES.PRIMARIO, color=COLORES.TEXTO_BLANCO)]
        )
        self.mostrar_dialogo(dialogo)
    
    def _abrir_popup_editar(self, item):
        campo_nombre = ft.TextField(label="Nombre", value=item.NOMBRE, prefix_icon=ft.icons.Icons.Icons.ADD_CIRCLE)
        campo_descripcion = ft.TextField(label="Descripción", value=item.DESCRIPCION or "", multiline=True)
        campo_precio = ft.TextField(label="Precio Adicional (centavos)", value=str(item.PRECIO_ADICIONAL), keyboard_type=ft.KeyboardType.NUMBER)
        
        def guardar(e):
            try:
                sesion = OBTENER_SESION()
                item_bd = sesion.query(MODELO_EXTRA).filter_by(ID=item.ID).first()
                if item_bd:
                    item_bd.NOMBRE = campo_nombre.value
                    item_bd.DESCRIPCION = campo_descripcion.value
                    item_bd.PRECIO_ADICIONAL = int(campo_precio.value)
                    sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Extra actualizado exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text(f"✏️ Editar: {item.NOMBRE}", color=COLORES.TEXTO),
            content=ft.Container(content=ft.Column([campo_nombre, campo_descripcion, campo_precio], tight=True, spacing=TAMANOS.ESPACIADO_MD), width=400),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()), ft.Button("Actualizar", icon=ft.icons.Icons.Icons.SAVE, on_click=guardar, bgcolor=COLORES.INFO, color=COLORES.TEXTO_BLANCO)]
        )
        self.mostrar_dialogo(dialogo)
    
    def _confirmar_eliminar(self, item):
        def eliminar(e):
            try:
                sesion = OBTENER_SESION()
                item_bd = sesion.query(MODELO_EXTRA).filter_by(ID=item.ID).first()
                if item_bd:
                    sesion.delete(item_bd)
                    sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Extra eliminado exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("⚠️ Confirmar Eliminación", color=COLORES.PELIGRO),
            content=ft.Text(f"¿Eliminar extra '{item.NOMBRE}'?\n\nEsta acción no se puede deshacer."),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()), ft.Button("Eliminar", icon=ft.icons.Icons.Icons.DELETE_FOREVER, on_click=eliminar, bgcolor=COLORES.PELIGRO, color=COLORES.TEXTO_BLANCO)]
        )
        self.mostrar_dialogo(dialogo)
