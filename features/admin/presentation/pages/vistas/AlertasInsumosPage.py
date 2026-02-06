"""
📋 Página de Alertas de Insumos - FLET
Gestión de alertas de stock bajo con interfaz visual
"""

import flet as ft
from core.base_datos.ConfiguracionBD import OBTENER_SESION, CERRAR_SESION
from core.base_datos.ConfiguracionBD import MODELO_ALERTA_INSUMO, MODELO_INSUMO
from core.Constantes import ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from features.admin.presentation.widgets.LayoutBase import LayoutBase
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@REQUIERE_ROL(ROLES.ADMIN, ROLES.SUPERADMIN)
class AlertasInsumosPage(LayoutBase):
    """Página para gestionar alertas de stock bajo"""
    
    def __init__(self, pagina: ft.Page, usuario):
        super().__init__(pagina, usuario)
        self._pagina = pagina
        self._usuario = usuario
        self._alertas = []
        self._tabla_alertas = None
        
        # Cargar datos al inicializar
        self._cargar_alertas()
        
        # Construir UI
        self.content = self._construir_interfaz()
    
    def _cargar_alertas(self):
        """Carga alertas pendientes de la base de datos"""
        try:
            with OBTENER_SESION() as session:
                alertas = session.query(MODELO_ALERTA_INSUMO).filter(
                    MODELO_ALERTA_INSUMO.RESUELTA == False
                ).order_by(MODELO_ALERTA_INSUMO.FECHA_CREACION.desc()).all()
                
                self._alertas = []
                for alerta in alertas:
                    insumo = alerta.INSUMO
                    self._alertas.append({
                        'ID': alerta.ID,
                        'INSUMO_ID': insumo.ID if insumo else None,
                        'INSUMO_NOMBRE': insumo.NOMBRE if insumo else 'N/A',
                        'TIPO': alerta.TIPO,
                        'MENSAJE': alerta.MENSAJE,
                        'LEIDA': alerta.LEIDA,
                        'FECHA_CREACION': alerta.FECHA_CREACION.strftime('%d/%m/%Y %H:%M'),
                        'objeto': alerta
                    })
                
                logger.info(f"Cargadas {len(self._alertas)} alertas pendientes")
        except Exception as e:
            logger.error(f"Error al cargar alertas: {e}")
            self._alertas = []
        finally:
            CERRAR_SESION()
    
    def _construir_interfaz(self) -> ft.Container:
        """Construye la interfaz principal"""
        
        # Header con título
        header = ft.Container(
            content=ft.Column([
                ft.Text("⚠️ Alertas de Insumos", 
                       size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_600),
                ft.Text("Gestiona las alertas de stock bajo automáticamente",
                       size=14, color=ft.Colors.GREY_700),
            ], spacing=5),
            padding=16,
            bgcolor=ft.Colors.RED_50,
            border_radius=10,
        )
        
        # Botones de acción
        botones = ft.Row([
            ft.ElevatedButton(
                "🔄 Actualizar",
                on_click=self._actualizar_alertas,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
            ),
            ft.ElevatedButton(
                "📊 Estadísticas",
                on_click=self._mostrar_estadisticas,
                bgcolor=ft.Colors.TEAL_600,
                color=ft.Colors.WHITE,
            ),
        ], spacing=8)
        
        # Tabla de alertas
        self._tabla_alertas = self._crear_tabla_alertas()
        
        # Contenedor principal
        return ft.Container(
            content=ft.Column([
                header,
                ft.Divider(height=1),
                botones,
                ft.Divider(height=1),
                ft.Text(
                    f"Total: {len(self._alertas)} alertas pendientes",
                    size=12, color=ft.Colors.GREY_600
                ),
                self._tabla_alertas,
            ], spacing=16, expand=True),
            padding=16,
        )
    
    def _crear_tabla_alertas(self) -> ft.DataTable:
        """Crea tabla con alertas"""
        
        filas = []
        for alerta in self._alertas:
            color_fondo = ft.Colors.GREY_100 if alerta['LEIDA'] else ft.Colors.ORANGE_50
            
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(alerta['INSUMO_NOMBRE'], 
                                   weight=ft.FontWeight.W_500)
                        ),
                        ft.DataCell(
                            ft.Text(alerta['TIPO'], 
                                   size=11, 
                                   color=ft.Colors.RED_700)
                        ),
                        ft.DataCell(
                            ft.Text(alerta['FECHA_CREACION'], 
                                   size=10, 
                                   color=ft.Colors.GREY_600)
                        ),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    ft.icons.CHECK_CIRCLE,
                                    tooltip="Marcar como leída",
                                    on_click=lambda e, alerta_id=alerta['ID']: 
                                        self._marcar_leida(alerta_id),
                                    icon_color=ft.Colors.BLUE_600 if not alerta['LEIDA'] else ft.Colors.GREY_400,
                                ),
                                ft.IconButton(
                                    ft.icons.DONE_ALL,
                                    tooltip="Resolver alerta",
                                    on_click=lambda e, alerta_id=alerta['ID']: 
                                        self._resolver_alerta(alerta_id),
                                    icon_color=ft.Colors.GREEN_600,
                                ),
                            ], spacing=0),
                        ),
                    ],
                    color=color_fondo,
                )
            )
        
        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Insumo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=filas if filas else [
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("✅ Sin alertas pendientes", 
                                       size=14, color=ft.Colors.GREEN_600)),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                ])
            ],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_200),
            column_spacing=30,
            heading_row_color=ft.Colors.BLUE_100,
            heading_row_height=50,
            data_row_max_height=60,
        )
        
        return ft.Column([tabla], expand=True, scroll=ft.ScrollMode.ADAPTIVE)
    
    def _actualizar_alertas(self, e):
        """Actualiza la lista de alertas"""
        self._cargar_alertas()
        self._tabla_alertas.content[0] = self._crear_tabla_alertas().content[0]
        
        # Mostrar snackbar
        self._pagina.snack_bar = ft.SnackBar(
            ft.Text("✅ Alertas actualizadas", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_600,
        )
        self._pagina.snack_bar.open = True
        self._pagina.update()
    
    def _marcar_leida(self, alerta_id: int):
        """Marca una alerta como leída"""
        try:
            with OBTENER_SESION() as session:
                alerta = session.query(MODELO_ALERTA_INSUMO).filter_by(ID=alerta_id).first()
                if alerta:
                    alerta.LEIDA = True
                    session.commit()
                    logger.info(f"Alerta {alerta_id} marcada como leída")
            
            # Recargar
            self._actualizar_alertas(None)
        except Exception as e:
            logger.error(f"Error al marcar alerta: {e}")
            self._mostrar_error(f"Error: {e}")
        finally:
            CERRAR_SESION()
    
    def _resolver_alerta(self, alerta_id: int):
        """Resuelve una alerta (cuando se compra el insumo)"""
        try:
            with OBTENER_SESION() as session:
                alerta = session.query(MODELO_ALERTA_INSUMO).filter_by(ID=alerta_id).first()
                if alerta:
                    alerta.RESUELTA = True
                    alerta.FECHA_RESOLUCION = datetime.utcnow()
                    session.commit()
                    logger.info(f"Alerta {alerta_id} resuelta")
            
            # Recargar
            self._actualizar_alertas(None)
            
            # Mostrar éxito
            self._pagina.snack_bar = ft.SnackBar(
                ft.Text("✅ Alerta resuelta", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.GREEN_600,
            )
            self._pagina.snack_bar.open = True
            self._pagina.update()
        except Exception as e:
            logger.error(f"Error al resolver alerta: {e}")
            self._mostrar_error(f"Error: {e}")
        finally:
            CERRAR_SESION()
    
    def _mostrar_estadisticas(self, e):
        """Muestra estadísticas de alertas"""
        try:
            with OBTENER_SESION() as session:
                total = session.query(MODELO_ALERTA_INSUMO).count()
                pendientes = session.query(MODELO_ALERTA_INSUMO).filter(
                    MODELO_ALERTA_INSUMO.RESUELTA == False
                ).count()
                no_leidas = session.query(MODELO_ALERTA_INSUMO).filter(
                    MODELO_ALERTA_INSUMO.RESUELTA == False,
                    MODELO_ALERTA_INSUMO.LEIDA == False
                ).count()
                resueltas = session.query(MODELO_ALERTA_INSUMO).filter(
                    MODELO_ALERTA_INSUMO.RESUELTA == True
                ).count()
                
                # Mostrar en diálogo
                dlg = ft.AlertDialog(
                    title=ft.Text("📊 Estadísticas de Alertas", weight=ft.FontWeight.BOLD),
                    content=ft.Column([
                        ft.ListTile(
                            title=ft.Text("Total de alertas"),
                            subtitle=ft.Text(f"{total}", size=18, weight=ft.FontWeight.BOLD),
                            leading=ft.Icon(ft.icons.INFO_OUTLINE, color=ft.Colors.BLUE_600),
                        ),
                        ft.Divider(),
                        ft.ListTile(
                            title=ft.Text("Pendientes"),
                            subtitle=ft.Text(f"{pendientes}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_600),
                            leading=ft.Icon(ft.icons.WARNING_ROUNDED, color=ft.Colors.ORANGE_600),
                        ),
                        ft.ListTile(
                            title=ft.Text("No leídas"),
                            subtitle=ft.Text(f"{no_leidas}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_600),
                            leading=ft.Icon(ft.icons.MAIL_OUTLINE, color=ft.Colors.RED_600),
                        ),
                        ft.ListTile(
                            title=ft.Text("Resueltas"),
                            subtitle=ft.Text(f"{resueltas}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_600),
                            leading=ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600),
                        ),
                    ], spacing=5),
                    actions=[
                        ft.TextButton("Cerrar", on_click=lambda e: self._cerrar_dialogo(dlg)),
                    ],
                )
                self._pagina.dialog = dlg
                dlg.open = True
                self._pagina.update()
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            self._mostrar_error(f"Error: {e}")
        finally:
            CERRAR_SESION()
    
    def _cerrar_dialogo(self, dlg):
        """Cierra un diálogo"""
        dlg.open = False
        self._pagina.update()
    
    def _mostrar_error(self, mensaje: str):
        """Muestra un error"""
        self._pagina.snack_bar = ft.SnackBar(
            ft.Text(f"❌ {mensaje}", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_600,
        )
        self._pagina.snack_bar.open = True
        self._pagina.update()
