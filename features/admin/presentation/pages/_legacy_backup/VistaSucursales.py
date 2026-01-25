"""
Vista de gestión de sucursales - REFACTORIZADA con BLoC + Componentes Globales
"""
import flet as ft
from features.admin.presentation.widgets.VistaBase import VistaBase
from core.base_datos.ConfiguracionBD import MODELO_SUCURSAL
from core.Constantes import COLORES, TAMANOS, ICONOS
from features.admin.presentation.bloc.SucursalesBloc import (
    SUCURSALES_BLOC,
    CargarSucursales,
    GuardarSucursal,
    EliminarSucursal,
    SucursalesCargadas,
    SucursalError,
    SucursalGuardada
)
from features.admin.presentation.widgets.ComponentesGlobales import (
    Notificador,
    FormularioCRUD,
    TablaCRUD,
    BotonesNavegacion
)


class VistaSucursales(VistaBase):
    """Vista para gestionar sucursales con BLoC Pattern"""
    
    def __init__(self, pagina: ft.Page, usuario, on_volver_inicio):
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo="Gestión de Sucursales",
            on_volver_inicio=on_volver_inicio,
            mostrar_boton_volver=True
        )
        self._tabla = None
        
        # Registrar listener BLoC
        SUCURSALES_BLOC.AGREGAR_LISTENER(self._ON_ESTADO_CAMBIO)
        
        self._cargar_vista()
        
        # Cargar datos
        SUCURSALES_BLOC.AGREGAR_EVENTO(CargarSucursales())
    
    def _ON_ESTADO_CAMBIO(self, estado):
        """Maneja cambios de estado"""
        if isinstance(estado, SucursalesCargadas):
            self._actualizar_tabla(estado.sucursales)
        elif isinstance(estado, SucursalError):
            Notificador.ERROR(self, estado.mensaje)
        elif isinstance(estado, SucursalGuardada):
            self.cerrar_dialogo()
            Notificador.EXITO(self, estado.mensaje)
    
    
    def _cargar_vista(self):
        """Carga la interfaz con componentes globales"""
        # Header con botón nuevo
        header = ft.Row([
            BotonesNavegacion.BOTON_NUEVO(self._abrir_popup_crear, "Sucursal")
        ])
        
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
            header,
            ft.Container(
                content=self._tabla,
                bgcolor=COLORES.FONDO_BLANCO,
                border_radius=TAMANOS.RADIO_MD,
                padding=TAMANOS.PADDING_MD,
            )
        ])
    
    def _actualizar_tabla(self, sucursales):
        """Actualiza tabla con datos"""
        self._tabla.rows.clear()
        for item in sucursales:
            self._tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(item.ID))),
                        ft.DataCell(ft.Text(item.NOMBRE)),
                        ft.DataCell(ft.Text(item.DIRECCION or "-")),
                        ft.DataCell(ft.Text(item.TELEFONO or "-")),
                        ft.DataCell(ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Editar",
                                icon_color=COLORES.INFO,
                                on_click=lambda e, i=item: self._abrir_popup_editar(i)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Eliminar",
                                icon_color=COLORES.PELIGRO,
                                on_click=lambda e, i=item: self._confirmar_eliminar(i)
                            ),
                        ])),
                    ]
                )
            )
        self.actualizar_ui()
    
    
    def _abrir_popup_crear(self, e):
        """Formulario crear con componentes globales"""
        campo_nombre = FormularioCRUD.CREAR_CAMPO("Nombre", icono=ft.Icons.STORE)
        campo_direccion = FormularioCRUD.CREAR_CAMPO("Dirección", icono=ft.Icons.LOCATION_ON)
        campo_telefono = FormularioCRUD.CREAR_CAMPO("Teléfono", icono=ft.Icons.PHONE)
        
        def guardar(e):
            if not campo_nombre.value:
                Notificador.ADVERTENCIA(self, "El nombre es obligatorio")
                return
            
            SUCURSALES_BLOC.AGREGAR_EVENTO(
                GuardarSucursal(datos={
                    "NOMBRE": campo_nombre.value,
                    "DIRECCION": campo_direccion.value,
                    "TELEFONO": campo_telefono.value
                })
            )
        
        dialogo = FormularioCRUD.CONSTRUIR_DIALOGO(
            titulo="➕ Nueva Sucursal",
            campos=[campo_nombre, campo_direccion, campo_telefono],
            on_guardar=guardar,
            on_cancelar=lambda e: self.cerrar_dialogo(),
            es_edicion=False
        )
        self.mostrar_dialogo(dialogo)
    
    def _abrir_popup_editar(self, item):
        """Formulario editar con componentes globales"""
        campo_nombre = FormularioCRUD.CREAR_CAMPO("Nombre", item.NOMBRE, icono=ft.Icons.STORE)
        campo_direccion = FormularioCRUD.CREAR_CAMPO("Dirección", item.DIRECCION or "", icono=ft.Icons.LOCATION_ON)
        campo_telefono = FormularioCRUD.CREAR_CAMPO("Teléfono", item.TELEFONO or "", icono=ft.Icons.PHONE)
        
        def guardar(e):
            SUCURSALES_BLOC.AGREGAR_EVENTO(
                GuardarSucursal(datos={
                    "ID": item.ID,
                    "NOMBRE": campo_nombre.value,
                    "DIRECCION": campo_direccion.value,
                    "TELEFONO": campo_telefono.value
                })
            )
        
        dialogo = FormularioCRUD.CONSTRUIR_DIALOGO(
            titulo=f"✏️ Editar: {item.NOMBRE}",
            campos=[campo_nombre, campo_direccion, campo_telefono],
            on_guardar=guardar,
            on_cancelar=lambda e: self.cerrar_dialogo(),
            es_edicion=True
        )
        self.mostrar_dialogo(dialogo)
    
    def _confirmar_eliminar(self, item):
        """Eliminar vía BLoC"""
        def eliminar(e):
            SUCURSALES_BLOC.AGREGAR_EVENTO(EliminarSucursal(sucursal_id=item.ID))
        
        dialogo = ft.AlertDialog(
            title=ft.Text("⚠️ Confirmar Eliminación", color=COLORES.PELIGRO),
            content=ft.Text(f"¿Eliminar sucursal '{item.NOMBRE}'?\n\nEsta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()),
                ft.ElevatedButton(
                    "Eliminar",
                    icon=ft.Icons.DELETE_FOREVER,
                    on_click=eliminar,
                    bgcolor=COLORES.PELIGRO,
                    color=COLORES.TEXTO_BLANCO
                )
            ]
        )
        self.mostrar_dialogo(dialogo)
    
    def __del__(self):
        """Limpieza"""
        try:
            SUCURSALES_BLOC.REMOVER_LISTENER(self._ON_ESTADO_CAMBIO)
        except:
            pass

