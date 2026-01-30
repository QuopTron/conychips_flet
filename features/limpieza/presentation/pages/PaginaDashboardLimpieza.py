import flet as ft
from datetime import datetime

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_REPORTE_LIMPIEZA,
    MODELO_REPORTE_LIMPIEZA_FOTO,
    MODELO_SUCURSAL,
)
from core.constantes import COLORES, TAMANOS, ICONOS
from core.decoradores.DecoradorVistas import REQUIERE_ROL

@REQUIERE_ROL("LIMPIEZA", "ADMIN", "SUPERADMIN")
class PaginaDashboardLimpieza:
    
    def __init__(self, PAGINA: ft.Page, USUARIO_ID: int):
        self.PAGINA = PAGINA
        self.USUARIO_ID = USUARIO_ID
        
        self.MIS_REPORTES = ft.ListView(spacing=10, expand=True)
        
        self._CARGAR_REPORTES()
    
    
    def _CARGAR_REPORTES(self):
        sesion = OBTENER_SESION()
        
        reportes = (
            sesion.query(MODELO_REPORTE_LIMPIEZA)
            .filter_by(USUARIO_ID=self.USUARIO_ID)
            .order_by(MODELO_REPORTE_LIMPIEZA.FECHA.desc())
            .all()
        )
        
        self.MIS_REPORTES.controls.clear()
        
        if not reportes:
            self.MIS_REPORTES.controls.append(
                ft.Text("No tienes reportes registrados", color=COLORES.TEXTO_SECUNDARIO)
            )
        else:
            for reporte in reportes:
                self.MIS_REPORTES.controls.append(
                    self._CREAR_TARJETA_REPORTE(reporte)
                )
        
        sesion.close()
        
        if self.PAGINA:
            self.PAGINA.update()
    
    
    def _CREAR_TARJETA_REPORTE(self, REPORTE):
        sesion = OBTENER_SESION()
        
        sucursal = sesion.query(MODELO_SUCURSAL).filter_by(ID=REPORTE.SUCURSAL_ID).first()
        
        fotos = (
            sesion.query(MODELO_REPORTE_LIMPIEZA_FOTO)
            .filter_by(REPORTE_ID=REPORTE.ID)
            .all()
        )
        
        sesion.close()
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ICONOS.LIMPIEZA, color=COLORES.PRIMARIO),
                    ft.Text(f"Reporte #{REPORTE.ID}", weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.Chip(
                        label=ft.Text(f"{len(fotos)} fotos", size=12),
                        bgcolor=COLORES.INFO,
                    ),
                ]),
                ft.Text(
                    f"Sucursal: {sucursal.NOMBRE if sucursal else 'N/A'}",
                    color=COLORES.TEXTO_SECUNDARIO
                ),
                ft.Text(f"Área: {REPORTE.AREA}"),
                ft.Text(
                    f"Observaciones: {REPORTE.OBSERVACIONES or 'Ninguna'}",
                    color=COLORES.TEXTO_SECUNDARIO,
                    size=12
                ),
                ft.Text(
                    REPORTE.FECHA.strftime("%d/%m/%Y %H:%M"),
                    color=COLORES.TEXTO_SECUNDARIO,
                    size=12
                ),
                ft.Button(
                    "Ver Fotos",
                    icon=ICONOS.IMAGEN,
                    on_click=lambda e, r=REPORTE: self._VER_FOTOS(r),
                    visible=len(fotos) > 0
                ),
            ], spacing=10),
            padding=15,
            border=ft.Border.all(1, COLORES.BORDE),
            border_radius=TAMANOS.RADIO_BORDE,
            bgcolor=COLORES.FONDO_TARJETA,
        )
    
    
    def _CREAR_REPORTE(self):
        sesion = OBTENER_SESION()
        
        sucursales = sesion.query(MODELO_SUCURSAL).all()
        
        sesion.close()
        
        SUCURSAL = ft.Dropdown(
            label="Sucursal",
            options=[
                ft.dropdown.Option(key=str(s.ID), text=s.NOMBRE)
                for s in sucursales
            ],
        )
        
        AREA = ft.Dropdown(
            label="Área",
            options=[
                ft.dropdown.Option("cocina"),
                ft.dropdown.Option("comedor"),
                ft.dropdown.Option("baños"),
                ft.dropdown.Option("entrada"),
                ft.dropdown.Option("almacen"),
            ],
        )
        
        OBSERVACIONES = ft.TextField(
            label="Observaciones",
            multiline=True,
            min_lines=3,
            max_lines=5,
        )
        
        def GUARDAR_REPORTE(e):
            sesion = OBTENER_SESION()
            
            reporte = MODELO_REPORTE_LIMPIEZA(
                SUCURSAL_ID=int(SUCURSAL.value),
                USUARIO_ID=self.USUARIO_ID,
                AREA=AREA.value,
                OBSERVACIONES=OBSERVACIONES.value,
            )
            
            sesion.add(reporte)
            sesion.commit()
            sesion.refresh(reporte)
            
            REPORTE_ID = reporte.ID
            
            sesion.close()
            
            self._CERRAR_DIALOG()
            self._SUBIR_FOTOS(REPORTE_ID)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Crear Reporte de Limpieza"),
            content=ft.Column([SUCURSAL, AREA, OBSERVACIONES], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOG()),
                ft.Button("Continuar", on_click=GUARDAR_REPORTE),
            ]
        )
        
        self.PAGINA.dialog = dialog
        dialog.open = True
        self.PAGINA.update()
    
    
    def _SUBIR_FOTOS(self, REPORTE_ID: int):
        FOTOS = []
        FOTOS_LISTA = ft.ListView(spacing=5, height=200)
        
        IMAGEN_URL = ft.TextField(
            label="URL de Imagen",
            hint_text="https://ejemplo.com/foto.jpg",
            prefix_icon=ICONOS.IMAGEN,
        )
        
        DESCRIPCION = ft.TextField(
            label="Descripción de la Foto",
            hint_text="Ej: Cocina limpia",
        )
        
        def AGREGAR_FOTO(e):
            if not IMAGEN_URL.value:
                return
            
            FOTOS.append({
                "url": IMAGEN_URL.value,
                "descripcion": DESCRIPCION.value or "",
            })
            
            FOTOS_LISTA.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ICONOS.IMAGEN, color=COLORES.EXITO),
                    title=ft.Text(IMAGEN_URL.value[:50] + "..."),
                    subtitle=ft.Text(DESCRIPCION.value or "Sin descripción"),
                )
            )
            
            IMAGEN_URL.value = ""
            DESCRIPCION.value = ""
            
            if self.PAGINA.dialog:
                self.PAGINA.dialog.update()
        
        def FINALIZAR(e):
            sesion = OBTENER_SESION()
            
            for foto in FOTOS:
                foto_obj = MODELO_REPORTE_LIMPIEZA_FOTO(
                    REPORTE_ID=REPORTE_ID,
                    IMAGEN_URL=foto["url"],
                    DESCRIPCION=foto["descripcion"],
                )
                sesion.add(foto_obj)
            
            sesion.commit()
            sesion.close()
            
            self._CERRAR_DIALOG()
            self._CARGAR_REPORTES()
            
            self.PAGINA.snack_bar = ft.SnackBar(
                content=ft.Text("Reporte creado con fotos"),
                bgcolor=COLORES.EXITO
            )
            self.PAGINA.snack_bar.open = True
            self.PAGINA.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Subir Fotos del Reporte"),
            content=ft.Column([
                IMAGEN_URL,
                DESCRIPCION,
                ft.Button(
                    "Agregar Foto",
                    icon=ICONOS.AGREGAR,
                    on_click=AGREGAR_FOTO
                ),
                ft.Divider(),
                ft.Text(f"Fotos agregadas: {len(FOTOS)}", weight=ft.FontWeight.BOLD),
                FOTOS_LISTA,
            ], tight=True, scroll=ft.ScrollMode.AUTO, height=500),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DIALOG()),
                ft.Button(
                    "Finalizar",
                    on_click=FINALIZAR,
                    disabled=len(FOTOS) == 0
                ),
            ]
        )
        
        self.PAGINA.dialog = dialog
        dialog.open = True
        self.PAGINA.update()
    
    
    def _VER_FOTOS(self, REPORTE):
        sesion = OBTENER_SESION()
        
        fotos = (
            sesion.query(MODELO_REPORTE_LIMPIEZA_FOTO)
            .filter_by(REPORTE_ID=REPORTE.ID)
            .all()
        )
        
        sesion.close()
        
        FOTOS_VISTA = ft.ListView(spacing=10)
        
        for foto in fotos:
            FOTOS_VISTA.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(foto.IMAGEN_URL, selectable=True, size=12),
                        ft.Text(foto.DESCRIPCION or "Sin descripción", color=COLORES.TEXTO_SECUNDARIO),
                        ft.Text(
                            foto.FECHA_SUBIDA.strftime("%d/%m/%Y %H:%M"),
                            size=10,
                            color=COLORES.TEXTO_SECUNDARIO
                        ),
                    ]),
                    padding=10,
                    border=ft.Border.all(1, COLORES.BORDE),
                    border_radius=TAMANOS.RADIO_BORDE,
                )
            )
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"Fotos - Reporte #{REPORTE.ID}"),
            content=ft.Container(
                content=FOTOS_VISTA,
                width=500,
                height=400,
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self._CERRAR_DIALOG()),
            ]
        )
        
        self.PAGINA.dialog = dialog
        dialog.open = True
        self.PAGINA.update()
    
    
    def _CERRAR_DIALOG(self):
        if self.PAGINA.dialog:
            self.PAGINA.dialog.open = False
            self.PAGINA.update()
    
    
    def CONSTRUIR(self) -> ft.Control:
        return ft.Column([
            ft.Row([
                ft.Text("Dashboard Limpieza", size=TAMANOS.TITULO, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.Button(
                    "Crear Reporte",
                    icon=ICONOS.AGREGAR,
                    bgcolor=COLORES.EXITO,
                    on_click=lambda e: self._CREAR_REPORTE(),
                ),
            ]),
            
            ft.Divider(),
            
            ft.Text("Mis Reportes", size=18, weight=ft.FontWeight.BOLD),
            
            ft.Container(
                content=self.MIS_REPORTES,
                expand=True,
                padding=10,
            ),
        ], expand=True)
