"""
Vista de gestión de productos con CRUD completo en popups
"""
import flet as ft
from features.admin.presentation.widgets.VistaBase import VistaBase
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_PRODUCTO, MODELO_SUCURSAL
from core.Constantes import COLORES, TAMANOS, ICONOS


class VistaProductos(VistaBase):
    """Vista para gestionar productos con CRUDs en popups"""
    
    def __init__(self, pagina: ft.Page, usuario, on_volver_inicio):
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo="Gestión de Productos",
            on_volver_inicio=on_volver_inicio,
            mostrar_boton_volver=True
        )
        self._tabla_productos = None
        self._cargar_vista()
    
    def _cargar_vista(self):
        """Carga la interfaz de gestión de productos"""
        boton_nuevo = ft.ElevatedButton(
            "➕ Nuevo Producto",
            icon=ICONOS.PRODUCTOS,
            on_click=self._abrir_popup_crear,
            bgcolor=COLORES.PRIMARIO,
            color=COLORES.TEXTO_BLANCO,
        )
        
        self._tabla_productos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Descripción", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Precio", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Stock", weight=ft.FontWeight.BOLD)),
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
                content=ft.Column([self._tabla_productos], scroll=ft.ScrollMode.AUTO),
                bgcolor=COLORES.FONDO_BLANCO,
                border_radius=TAMANOS.RADIO_MD,
                padding=TAMANOS.PADDING_MD,
            )
        ])
        
        self._cargar_productos()
    
    def _cargar_productos(self):
        """Carga productos desde la base de datos"""
        sesion = OBTENER_SESION()
        productos = sesion.query(MODELO_PRODUCTO).all()
        
        self._tabla_productos.rows.clear()
        for producto in productos:
            self._tabla_productos.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(producto.ID))),
                        ft.DataCell(ft.Text(producto.NOMBRE)),
                        ft.DataCell(ft.Text(producto.DESCRIPCION or "-")),
                        ft.DataCell(ft.Text(f"${producto.PRECIO / 100:.2f}")),
                        ft.DataCell(ft.Text(str(producto.STOCK or 0))),
                        ft.DataCell(ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Editar",
                                icon_color=COLORES.INFO,
                                on_click=lambda e, p=producto: self._abrir_popup_editar(p)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Eliminar",
                                icon_color=COLORES.PELIGRO,
                                on_click=lambda e, p=producto: self._confirmar_eliminar(p)
                            ),
                        ])),
                    ]
                )
            )
        
        sesion.close()
        self.actualizar_ui()
    
    def _abrir_popup_crear(self, e):
        """Abre popup para crear nuevo producto"""
        campo_nombre = ft.TextField(label="Nombre", prefix_icon=ft.Icons.FASTFOOD)
        campo_descripcion = ft.TextField(label="Descripción", multiline=True, min_lines=2, max_lines=4)
        campo_precio = ft.TextField(label="Precio (en centavos)", prefix_icon=ft.Icons.ATTACH_MONEY, keyboard_type=ft.KeyboardType.NUMBER)
        campo_stock = ft.TextField(label="Stock inicial", prefix_icon=ft.Icons.INVENTORY, keyboard_type=ft.KeyboardType.NUMBER, value="0")
        campo_imagen = ft.TextField(label="URL Imagen", prefix_icon=ft.Icons.IMAGE, hint_text="assets/productos/imagen.jpg")
        
        def guardar(e):
            if not campo_nombre.value or not campo_precio.value:
                self.mostrar_snackbar("Nombre y precio son obligatorios", es_error=True)
                return
            
            try:
                sesion = OBTENER_SESION()
                
                nuevo_producto = MODELO_PRODUCTO(
                    NOMBRE=campo_nombre.value,
                    DESCRIPCION=campo_descripcion.value,
                    PRECIO=int(campo_precio.value),
                    STOCK=int(campo_stock.value) if campo_stock.value else 0,
                    IMAGEN=campo_imagen.value
                )
                
                sesion.add(nuevo_producto)
                sesion.commit()
                sesion.close()
                
                self.cerrar_dialogo()
                self.mostrar_snackbar("Producto creado exitosamente")
                self._cargar_productos()
                
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("➕ Nuevo Producto", color=COLORES.TEXTO),
            content=ft.Container(
                content=ft.Column([
                    campo_nombre, campo_descripcion, campo_precio, campo_stock, campo_imagen
                ], tight=True, spacing=TAMANOS.ESPACIADO_MD),
                width=500
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()),
                ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=guardar, bgcolor=COLORES.PRIMARIO, color=COLORES.TEXTO_BLANCO)
            ]
        )
        
        self.mostrar_dialogo(dialogo)
    
    def _abrir_popup_editar(self, producto):
        """Abre popup para editar producto existente"""
        campo_nombre = ft.TextField(label="Nombre", value=producto.NOMBRE, prefix_icon=ft.Icons.FASTFOOD)
        campo_descripcion = ft.TextField(label="Descripción", value=producto.DESCRIPCION or "", multiline=True, min_lines=2, max_lines=4)
        campo_precio = ft.TextField(label="Precio (en centavos)", value=str(producto.PRECIO), prefix_icon=ft.Icons.ATTACH_MONEY, keyboard_type=ft.KeyboardType.NUMBER)
        campo_stock = ft.TextField(label="Stock", value=str(producto.STOCK or 0), prefix_icon=ft.Icons.INVENTORY, keyboard_type=ft.KeyboardType.NUMBER)
        campo_imagen = ft.TextField(label="URL Imagen", value=producto.IMAGEN or "", prefix_icon=ft.Icons.IMAGE)
        
        def guardar(e):
            try:
                sesion = OBTENER_SESION()
                producto_bd = sesion.query(MODELO_PRODUCTO).filter_by(ID=producto.ID).first()
                
                if producto_bd:
                    producto_bd.NOMBRE = campo_nombre.value
                    producto_bd.DESCRIPCION = campo_descripcion.value
                    producto_bd.PRECIO = int(campo_precio.value)
                    producto_bd.STOCK = int(campo_stock.value) if campo_stock.value else 0
                    producto_bd.IMAGEN = campo_imagen.value
                    
                    sesion.commit()
                
                sesion.close()
                
                self.cerrar_dialogo()
                self.mostrar_snackbar("Producto actualizado exitosamente")
                self._cargar_productos()
                
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text(f"✏️ Editar: {producto.NOMBRE}", color=COLORES.TEXTO),
            content=ft.Container(
                content=ft.Column([
                    campo_nombre, campo_descripcion, campo_precio, campo_stock, campo_imagen
                ], tight=True, spacing=TAMANOS.ESPACIADO_MD),
                width=500
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()),
                ft.ElevatedButton("Actualizar", icon=ft.Icons.SAVE, on_click=guardar, bgcolor=COLORES.INFO, color=COLORES.TEXTO_BLANCO)
            ]
        )
        
        self.mostrar_dialogo(dialogo)
    
    def _confirmar_eliminar(self, producto):
        """Confirma eliminación de producto"""
        def eliminar(e):
            try:
                sesion = OBTENER_SESION()
                producto_bd = sesion.query(MODELO_PRODUCTO).filter_by(ID=producto.ID).first()
                
                if producto_bd:
                    sesion.delete(producto_bd)
                    sesion.commit()
                
                sesion.close()
                
                self.cerrar_dialogo()
                self.mostrar_snackbar("Producto eliminado exitosamente")
                self._cargar_productos()
                
            except Exception as ex:
                self.mostrar_snackbar(f"Error: {str(ex)}", es_error=True)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("⚠️ Confirmar Eliminación", color=COLORES.PELIGRO),
            content=ft.Text(f"¿Eliminar el producto '{producto.NOMBRE}'?\n\nEsta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()),
                ft.ElevatedButton("Eliminar", icon=ft.Icons.DELETE_FOREVER, on_click=eliminar, bgcolor=COLORES.PELIGRO, color=COLORES.TEXTO_BLANCO)
            ]
        )
        
        self.mostrar_dialogo(dialogo)
