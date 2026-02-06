import flet as ft
from features.admin.presentation.widgets.VistaBase import VistaBase
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_INSUMO, MODELO_PROVEEDOR
from core.Constantes import COLORES, TAMANOS, ICONOS

class VistaInsumos(VistaBase):
    
    def __init__(self, pagina: ft.Page, usuario, on_volver_inicio):
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo="Gestión de Insumos",
            on_volver_inicio=on_volver_inicio,
            mostrar_boton_volver=True
        )
        self._tabla = None
        self._cargar_vista()
    
    def _cargar_vista(self):
        boton_nuevo = ft.Button(
            "➕ Nuevo Insumo",
            icon=ICONOS.INSUMOS,
            on_click=self._abrir_popup_crear,
            bgcolor=COLORES.PRIMARIO,
            color=COLORES.TEXTO_BLANCO,
        )
        
        self._tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Cantidad", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Unidad", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Stock Mínimo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.Border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_MD,
            vertical_lines=ft.BorderSide(1, COLORES.BORDE),
            heading_row_color=COLORES.PRIMARIO_CLARO,
        )
        
        self.establecer_contenido([
            ft.Row([boton_nuevo]),
            ft.Container(
                content=ft.Column([self._tabla], scroll=ft.ScrollMode.AUTO),
                bgcolor=COLORES.FONDO_BLANCO,
                border_radius=TAMANOS.RADIO_MD,
                padding=TAMANOS.PADDING_MD,
            )
        ])
        
        self._cargar_datos()
    
    def _cargar_datos(self):
        sesion = OBTENER_SESION()
        items = sesion.query(MODELO_INSUMO).all()
        
        self._tabla.rows.clear()
        for item in items:
            alerta = item.CANTIDAD < item.STOCK_MINIMO if item.STOCK_MINIMO else False
            
            self._tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(item.ID))),
                        ft.DataCell(ft.Text(item.NOMBRE)),
                        ft.DataCell(ft.Text(str(item.CANTIDAD), color=COLORES.PELIGRO if alerta else COLORES.TEXTO)),
                        ft.DataCell(ft.Text(item.UNIDAD_MEDIDA or "-")),
                        ft.DataCell(ft.Text(str(item.STOCK_MINIMO) if item.STOCK_MINIMO else "-")),
                        ft.DataCell(ft.Row([
                            ft.IconButton(icon=ft.icons.Icons.Icons.EDIT, tooltip="Editar", icon_color=COLORES.INFO, on_click=lambda e, i=item: self._abrir_popup_editar(i)),
                            ft.IconButton(icon=ft.icons.Icons.Icons.DELETE, tooltip="Eliminar", icon_color=COLORES.PELIGRO, on_click=lambda e, i=item: self._confirmar_eliminar(i)),
                        ])),
                    ]
                )
            )
        
        sesion.close()
        self.actualizar_ui()
    
    def _abrir_popup_crear(self, e):
        campo_nombre = ft.TextField(label="Nombre", prefix_icon=ft.icons.Icons.Icons.INVENTORY_2)
        campo_cantidad = ft.TextField(label="Cantidad", prefix_icon=ft.icons.Icons.Icons.NUMBERS, keyboard_type=ft.KeyboardType.NUMBER, value="0")
        campo_unidad = ft.Dropdown(
            label="Unidad de Medida",
            options=[
                ft.dropdown.Option("kg"),
                ft.dropdown.Option("litros"),
                ft.dropdown.Option("unidades"),
                ft.dropdown.Option("gramos"),
                ft.dropdown.Option("mililitros"),
            ],
            value="unidades"
        )
        campo_minimo = ft.TextField(label="Stock Mínimo", keyboard_type=ft.KeyboardType.NUMBER, value="10")
        
        def guardar(e):
            if not campo_nombre.value:
                self.mostrar_snackbar("El nombre es obligatorio", es_error=True)
                return
            
            try:
                sesion = OBTENER_SESION()
                nuevo = MODELO_INSUMO(
                    NOMBRE=campo_nombre.value,
                    CANTIDAD=int(campo_cantidad.value) if campo_cantidad.value else 0,
                    UNIDAD_MEDIDA=campo_unidad.value,
                    STOCK_MINIMO=int(campo_minimo.value) if campo_minimo.value else None
                )
                sesion.add(nuevo)
                sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Insumo creado exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("➕ Nuevo Insumo", color=COLORES.TEXTO),
            content=ft.Container(content=ft.Column([campo_nombre, campo_cantidad, campo_unidad, campo_minimo], tight=True, spacing=TAMANOS.ESPACIADO_MD), width=400),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()),
                ft.Button("Guardar", icon=ft.icons.Icons.Icons.SAVE, on_click=guardar, bgcolor=COLORES.PRIMARIO, color=COLORES.TEXTO_BLANCO)
            ]
        )
        self.mostrar_dialogo(dialogo)
    
    def _abrir_popup_editar(self, item):
        campo_nombre = ft.TextField(label="Nombre", value=item.NOMBRE, prefix_icon=ft.icons.Icons.Icons.INVENTORY_2)
        campo_cantidad = ft.TextField(label="Cantidad", value=str(item.CANTIDAD), keyboard_type=ft.KeyboardType.NUMBER)
        campo_unidad = ft.Dropdown(
            label="Unidad de Medida",
            options=[ft.dropdown.Option("kg"), ft.dropdown.Option("litros"), ft.dropdown.Option("unidades"), ft.dropdown.Option("gramos"), ft.dropdown.Option("mililitros")],
            value=item.UNIDAD_MEDIDA or "unidades"
        )
        campo_minimo = ft.TextField(label="Stock Mínimo", value=str(item.STOCK_MINIMO) if item.STOCK_MINIMO else "", keyboard_type=ft.KeyboardType.NUMBER)
        
        def guardar(e):
            try:
                sesion = OBTENER_SESION()
                item_bd = sesion.query(MODELO_INSUMO).filter_by(ID=item.ID).first()
                if item_bd:
                    item_bd.NOMBRE = campo_nombre.value
                    item_bd.CANTIDAD = int(campo_cantidad.value) if campo_cantidad.value else 0
                    item_bd.UNIDAD_MEDIDA = campo_unidad.value
                    item_bd.STOCK_MINIMO = int(campo_minimo.value) if campo_minimo.value else None
                    sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Insumo actualizado exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text(f"✏️ Editar: {item.NOMBRE}", color=COLORES.TEXTO),
            content=ft.Container(content=ft.Column([campo_nombre, campo_cantidad, campo_unidad, campo_minimo], tight=True, spacing=TAMANOS.ESPACIADO_MD), width=400),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()),
                ft.Button("Actualizar", icon=ft.icons.Icons.Icons.SAVE, on_click=guardar, bgcolor=COLORES.INFO, color=COLORES.TEXTO_BLANCO)
            ]
        )
        self.mostrar_dialogo(dialogo)
    
    def _confirmar_eliminar(self, item):
        def eliminar(e):
            try:
                sesion = OBTENER_SESION()
                item_bd = sesion.query(MODELO_INSUMO).filter_by(ID=item.ID).first()
                if item_bd:
                    sesion.delete(item_bd)
                    sesion.commit()
                sesion.close()
                self.cerrar_dialogo()
                self.mostrar_snackbar("Insumo eliminado exitosamente")
                self._cargar_datos()
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("⚠️ Confirmar Eliminación", color=COLORES.PELIGRO),
            content=ft.Text(f"¿Eliminar insumo '{item.NOMBRE}'?\n\nEsta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()),
                ft.Button("Eliminar", icon=ft.icons.Icons.Icons.DELETE_FOREVER, on_click=eliminar, bgcolor=COLORES.PELIGRO, color=COLORES.TEXTO_BLANCO)
            ]
        )
        self.mostrar_dialogo(dialogo)
