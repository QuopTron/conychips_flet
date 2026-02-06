import flet as ft
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import and_, or_, desc
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_AUDITORIA, MODELO_USUARIO
from core.Constantes import COLORES, TAMANOS, ICONOS
from features.admin.presentation.widgets.LayoutBase import LayoutBase
from features.admin.presentation.widgets.ComponentesGlobales import Notificador
from core.ui.safe_actions import safe_update


class AuditoriaPageModerna(LayoutBase):
    """
    Página moderna de auditoría del sistema con filtros avanzados.
    Muestra todos los logs de acciones realizadas en el sistema.
    """
    
    # Tipos de acciones auditadas
    TIPOS_ACCION = {
        "TODOS": ("🔍 Todas las Acciones", ft.Colors.BLUE_700),
        "LOGIN": ("🔐 Inicios de Sesión", ft.Colors.GREEN_700),
        "LOGOUT": ("🚪 Cierres de Sesión", ft.Colors.GREY_700),
        "CREAR": ("➕ Creaciones", ft.Colors.BLUE_700),
        "EDITAR": ("✏️ Modificaciones", ft.Colors.ORANGE_700),
        "ELIMINAR": ("🗑️ Eliminaciones", ft.Colors.RED_700),
        "VER": ("👁️ Consultas", ft.Colors.TEAL_700),
        "ERROR": ("⚠️ Errores", ft.Colors.DEEP_ORANGE_700),
    }
    
    # Entidades del sistema
    ENTIDADES = [
        "TODOS",
        "USUARIOS",
        "PRODUCTOS",
        "PEDIDOS",
        "SUCURSALES",
        "ROLES",
        "PROVEEDORES",
        "INSUMOS",
        "CAJAS",
        "OFERTAS",
    ]
    
    def __init__(self, PAGINA: ft.Page, USUARIO):
        # Estado de filtros
        self._filtro_accion = "TODOS"
        self._filtro_entidad = "TODOS"
        self._filtro_usuario = None
        self._filtro_texto = ""
        self._fecha_inicio = datetime.now() - timedelta(days=7)
        self._fecha_fin = datetime.now()
        
        # Componentes
        self._tabla = None
        self._lista_registros = None
        self._dropdown_usuarios = None
        self._contador_registros = None
        
        # Inicializar LayoutBase
        super().__init__(
            pagina=PAGINA,
            usuario=USUARIO,
            titulo_vista="📋 Auditoría del Sistema",
            mostrar_boton_volver=True,
            index_navegacion=0,
            on_volver_dashboard=self._ir_dashboard,
            on_cerrar_sesion=self._cerrar_sesion
        )
        
        # Construir interfaz
        contenido = self._construir_interfaz()
        self.construir(contenido)
        
        # Cargar datos iniciales
        self._cargar_usuarios()
        self._cargar_registros()
    
    def _construir_interfaz(self):
        """Construye la interfaz completa"""
        # Header con estadísticas
        header = self._construir_header()
        
        # Panel de filtros
        filtros = self._construir_filtros()
        
        # Tabla de registros
        self._lista_registros = ft.Column(
            spacing=8,
            scroll=ft.ScrollMode.ADAPTIVE
        )
        
        # Contador de registros
        self._contador_registros = ft.Text(
            "Cargando...",
            size=14,
            color=COLORES.TEXTO_SECUNDARIO,
            weight=ft.FontWeight.BOLD
        )
        
        contenedor_tabla = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.Icons.LIST_ALT, size=20, color=COLORES.PRIMARIO),
                        ft.Text("Registros de Auditoría", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        self._contador_registros
                    ]),
                    padding=12,
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=ft.border_radius.only(top_left=8, top_right=8)
                ),
                ft.Container(
                    content=self._lista_registros,
                    padding=12,
                    expand=True
                )
            ], spacing=0, expand=True),
            border=ft.border.all(1, COLORES.BORDE),
            border_radius=8,
            expand=True
        )
        
        return ft.Column([
            header,
            filtros,
            contenedor_tabla
        ], spacing=12, expand=True)
    
    def _construir_header(self):
        """Construye el header con estadísticas rápidas"""
        # Textos para estadísticas (se actualizan después)
        self._stat_hoy = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=COLORES.PRIMARIO)
        self._stat_semana = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)
        self._stat_usuarios = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_700)
        self._stat_errores = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700)
        
        return ft.Container(
            content=ft.ResponsiveRow([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.Icons.TODAY, size=32, color=ft.Colors.BLUE_400),
                        ft.Text("Hoy", size=12, color=COLORES.TEXTO_SECUNDARIO),
                        self._stat_hoy
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=8,
                    padding=16,
                    border=ft.border.all(1, ft.Colors.BLUE_200),
                    col={"xs": 6, "sm": 3}
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.Icons.DATE_RANGE, size=32, color=ft.Colors.GREEN_400),
                        ft.Text("Esta Semana", size=12, color=COLORES.TEXTO_SECUNDARIO),
                        self._stat_semana
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=8,
                    padding=16,
                    border=ft.border.all(1, ft.Colors.GREEN_200),
                    col={"xs": 6, "sm": 3}
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.Icons.PERSON, size=32, color=ft.Colors.PURPLE_400),
                        ft.Text("Usuarios Activos", size=12, color=COLORES.TEXTO_SECUNDARIO),
                        self._stat_usuarios
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=8,
                    padding=16,
                    border=ft.border.all(1, ft.Colors.PURPLE_200),
                    col={"xs": 6, "sm": 3}
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.Icons.ERROR_OUTLINE, size=32, color=ft.Colors.RED_400),
                        ft.Text("Errores", size=12, color=COLORES.TEXTO_SECUNDARIO),
                        self._stat_errores
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=8,
                    padding=16,
                    border=ft.border.all(1, ft.Colors.RED_200),
                    col={"xs": 6, "sm": 3}
                )
            ], spacing=12, run_spacing=12),
            padding=0
        )
    
    def _construir_filtros(self):
        """Construye el panel de filtros avanzados"""
        # Dropdown de tipo de acción
        dropdown_accion = ft.Dropdown(
            label="Tipo de Acción",
            options=[
                ft.dropdown.Option(key, text=label) 
                for key, (label, _) in self.TIPOS_ACCION.items()
            ],
            value=self._filtro_accion,
            border_color=COLORES.PRIMARIO,
            focused_border_color=COLORES.PRIMARIO
        )
        dropdown_accion.on_select = self._cambiar_filtro_accion
        
        # Dropdown de entidad
        dropdown_entidad = ft.Dropdown(
            label="Entidad/Módulo",
            options=[ft.dropdown.Option(e) for e in self.ENTIDADES],
            value=self._filtro_entidad,
            border_color=COLORES.PRIMARIO,
            focused_border_color=COLORES.PRIMARIO
        )
        dropdown_entidad.on_select = self._cambiar_filtro_entidad
        
        # Dropdown de usuario
        self._dropdown_usuarios = ft.Dropdown(
            label="Usuario",
            options=[ft.dropdown.Option("TODOS", "Todos los usuarios")],
            value="TODOS",
            border_color=COLORES.PRIMARIO,
            focused_border_color=COLORES.PRIMARIO
        )
        self._dropdown_usuarios.on_select = self._cambiar_filtro_usuario
        
        # Campo de búsqueda
        campo_busqueda = ft.TextField(
            label="Buscar en detalles",
            hint_text="Escriba para buscar...",
            prefix_icon=ft.icons.Icons.SEARCH,
            on_change=self._cambiar_busqueda,
            border_color=COLORES.PRIMARIO,
            focused_border_color=COLORES.PRIMARIO
        )
        
        # Botones de rango de fechas
        botones_rango = ft.Row([
            ft.ElevatedButton(
                "Hoy",
                icon=ft.icons.Icons.TODAY,
                on_click=lambda e: self._aplicar_rango(0),
                bgcolor=ft.Colors.BLUE_100,
                color=COLORES.PRIMARIO
            ),
            ft.ElevatedButton(
                "Última Semana",
                icon=ft.icons.Icons.DATE_RANGE,
                on_click=lambda e: self._aplicar_rango(7),
                bgcolor=ft.Colors.GREEN_100,
                color=ft.Colors.GREEN_700
            ),
            ft.ElevatedButton(
                "Último Mes",
                icon=ft.icons.Icons.CALENDAR_TODAY,
                on_click=lambda e: self._aplicar_rango(30),
                bgcolor=ft.Colors.ORANGE_100,
                color=ft.Colors.ORANGE_700
            ),
            ft.Container(expand=True),
            ft.ElevatedButton(
                "Limpiar Filtros",
                icon=ft.icons.Icons.CLEAR_ALL,
                on_click=self._limpiar_filtros,
                bgcolor=ft.Colors.GREY_300,
                color=COLORES.TEXTO
            ),
            ft.ElevatedButton(
                "Exportar",
                icon=ft.icons.Icons.DOWNLOAD,
                on_click=self._exportar,
                bgcolor=COLORES.EXITO,
                color=ft.Colors.WHITE
            )
        ], spacing=8, wrap=True)
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "🔍 Filtros Avanzados",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=COLORES.PRIMARIO
                ),
                ft.ResponsiveRow([
                    ft.Container(dropdown_accion, col={"xs": 12, "sm": 6, "md": 3}),
                    ft.Container(dropdown_entidad, col={"xs": 12, "sm": 6, "md": 3}),
                    ft.Container(self._dropdown_usuarios, col={"xs": 12, "sm": 6, "md": 3}),
                    ft.Container(campo_busqueda, col={"xs": 12, "sm": 6, "md": 3}),
                ], spacing=12, run_spacing=12),
                botones_rango
            ], spacing=12),
            padding=16,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.BLUE_200)
        )
    
    def _crear_card_registro(self, registro: MODELO_AUDITORIA):
        """Crea una tarjeta visual para cada registro de auditoría"""
        # Obtener datos
        usuario_nombre = registro.USUARIO.NOMBRE_COMPLETO if registro.USUARIO else "Sistema"
        usuario_rol = registro.USUARIO.ROL if registro.USUARIO else "SISTEMA"
        accion = registro.ACCION or "Sin especificar"
        entidad = registro.ENTIDAD or "Sistema"
        detalle = registro.DETALLE or "Sin detalles adicionales"
        fecha = registro.FECHA.strftime("%d/%m/%Y %H:%M:%S") if registro.FECHA else "Fecha desconocida"
        
        # Determinar color según la acción
        color_accion = ft.Colors.GREY_700
        icono_accion = ft.icons.Icons.INFO_OUTLINE
        
        if "LOGIN" in accion.upper():
            color_accion = ft.Colors.GREEN_700
            icono_accion = ft.icons.Icons.LOGIN
        elif "LOGOUT" in accion.upper():
            color_accion = ft.Colors.GREY_700
            icono_accion = ft.icons.Icons.LOGOUT
        elif "CREAR" in accion.upper():
            color_accion = ft.Colors.BLUE_700
            icono_accion = ft.icons.Icons.ADD_CIRCLE_OUTLINE
        elif "EDITAR" in accion.upper() or "MODIFICAR" in accion.upper():
            color_accion = ft.Colors.ORANGE_700
            icono_accion = ft.icons.Icons.EDIT
        elif "ELIMINAR" in accion.upper():
            color_accion = ft.Colors.RED_700
            icono_accion = ft.icons.Icons.DELETE_OUTLINE
        elif "VER" in accion.upper():
            color_accion = ft.Colors.TEAL_700
            icono_accion = ft.icons.Icons.VISIBILITY
        elif "ERROR" in accion.upper():
            color_accion = ft.Colors.DEEP_ORANGE_700
            icono_accion = ft.icons.Icons.ERROR_OUTLINE
        
        # Badge de entidad con color
        color_entidad = ft.Colors.PURPLE_700
        if entidad:
            if "PRODUCTO" in entidad:
                color_entidad = ft.Colors.BLUE_700
            elif "PEDIDO" in entidad:
                color_entidad = ft.Colors.ORANGE_700
            elif "USUARIO" in entidad:
                color_entidad = ft.Colors.PURPLE_700
            elif "SUCURSAL" in entidad:
                color_entidad = ft.Colors.TEAL_700
            elif "CAJA" in entidad:
                color_entidad = ft.Colors.GREEN_700
        
        badge_entidad = ft.Container(
            content=ft.Text(
                entidad.upper() if entidad else "SISTEMA",
                size=11,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE
            ),
            bgcolor=color_entidad,
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=4
        )
        
        # Badge de rol del usuario
        badge_rol = ft.Container(
            content=ft.Text(
                usuario_rol,
                size=10,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE
            ),
            bgcolor=ft.Colors.INDIGO_400,
            padding=ft.padding.symmetric(horizontal=6, vertical=2),
            border_radius=3
        )
        
        # Función para ver detalles completos
        def ver_detalles(e):
            dialogo = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(icono_accion, color=color_accion),
                    ft.Text("Detalles del Registro", weight=ft.FontWeight.BOLD),
                ]),
                content=ft.Container(
                    content=ft.Column([
                        ft.Divider(),
                        ft.Row([
                            ft.Text("👤 Usuario:", weight=ft.FontWeight.BOLD, size=13),
                            ft.Text(usuario_nombre, size=13),
                        ]),
                        ft.Row([
                            ft.Text("🎭 Rol:", weight=ft.FontWeight.BOLD, size=13),
                            badge_rol,
                        ]),
                        ft.Divider(),
                        ft.Row([
                            ft.Text("⏰ Fecha/Hora:", weight=ft.FontWeight.BOLD, size=13),
                            ft.Text(fecha, size=13),
                        ]),
                        ft.Row([
                            ft.Text("⚡ Acción:", weight=ft.FontWeight.BOLD, size=13),
                            ft.Container(
                                content=ft.Text(accion, size=12, color=ft.Colors.WHITE),
                                bgcolor=color_accion,
                                padding=8,
                                border_radius=4
                            ),
                        ]),
                        ft.Row([
                            ft.Text("📁 Entidad:", weight=ft.FontWeight.BOLD, size=13),
                            badge_entidad,
                            ft.Text(f"ID: {registro.ENTIDAD_ID}" if registro.ENTIDAD_ID else "Sin ID", size=12, italic=True),
                        ]),
                        ft.Divider(),
                        ft.Text("📝 Detalles:", weight=ft.FontWeight.BOLD, size=13),
                        ft.Container(
                            content=ft.Text(
                                detalle,
                                size=12,
                                selectable=True
                            ),
                            bgcolor=ft.Colors.GREY_100,
                            padding=12,
                            border_radius=6,
                            border=ft.border.all(1, ft.Colors.GREY_300)
                        ),
                    ], spacing=8, scroll=ft.ScrollMode.AUTO),
                    width=600,
                    height=400
                ),
                actions=[
                    ft.TextButton("Cerrar", on_click=lambda e: self._cerrar_dialogo_detalle(dialogo))
                ],
            )
            self._pagina.overlay.append(dialogo)
            dialogo.open = True
            self._pagina.update()
        
        return ft.Container(
            content=ft.Row([
                # Icono y timestamp
                ft.Container(
                    content=ft.Column([
                        ft.Icon(icono_accion, size=32, color=color_accion),
                        ft.Text(
                            fecha.split()[1],  # Solo la hora
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=COLORES.TEXTO_SECUNDARIO
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    width=80
                ),
                
                # Separador vertical
                ft.Container(
                    width=2,
                    bgcolor=color_accion,
                    border_radius=1
                ),
                
                # Contenido principal
                ft.Container(
                    content=ft.Column([
                        # Usuario, rol y fecha
                        ft.Row([
                            ft.Icon(ft.icons.Icons.PERSON, size=16, color=COLORES.PRIMARIO),
                            ft.Text(
                                usuario_nombre,
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=COLORES.PRIMARIO
                            ),
                            badge_rol,
                            ft.Container(expand=True),
                            ft.Text(
                                fecha.split()[0],  # Solo la fecha
                                size=12,
                                color=COLORES.TEXTO_SECUNDARIO
                            )
                        ], spacing=8),
                        
                        # Acción y entidad
                        ft.Row([
                            ft.Container(
                                content=ft.Text(
                                    accion,
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE
                                ),
                                bgcolor=color_accion,
                                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                border_radius=6
                            ),
                            ft.Icon(ft.icons.Icons.ARROW_FORWARD, size=16, color=COLORES.TEXTO_SECUNDARIO),
                            badge_entidad,
                            ft.Text(
                                f"ID: {registro.ENTIDAD_ID}" if registro.ENTIDAD_ID else "",
                                size=11,
                                color=COLORES.TEXTO_SECUNDARIO,
                                italic=True
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.icons.Icons.INFO_OUTLINE,
                                icon_size=20,
                                tooltip="Ver detalles completos",
                                on_click=ver_detalles,
                                icon_color=COLORES.PRIMARIO
                            )
                        ], spacing=8),
                        
                        # Detalles (truncados)
                        ft.Container(
                            content=ft.Text(
                                detalle,
                                size=12,
                                color=COLORES.TEXTO_SECUNDARIO,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            padding=ft.padding.only(top=4, left=8),
                            border=ft.border.only(left=ft.BorderSide(2, ft.Colors.GREY_300))
                        )
                    ], spacing=8),
                    expand=True,
                    padding=ft.padding.only(left=12)
                )
            ], spacing=0),
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            padding=12,
            border=ft.border.all(1, COLORES.BORDE),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=3,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 2)
            )
        )
    
    def _cerrar_dialogo_detalle(self, dialogo):
        """Cierra el diálogo de detalles"""
        dialogo.open = False
        self._pagina.overlay.remove(dialogo)
        self._pagina.update()
    
    def _cargar_usuarios(self):
        """Carga la lista de usuarios para el filtro"""
        try:
            sesion = OBTENER_SESION()
            usuarios = sesion.query(MODELO_USUARIO).filter(
                MODELO_USUARIO.ACTIVO == True
            ).order_by(MODELO_USUARIO.NOMBRE_COMPLETO).all()
            
            self._dropdown_usuarios.options = [
                ft.dropdown.Option("TODOS", "Todos los usuarios")
            ]
            
            for usuario in usuarios:
                self._dropdown_usuarios.options.append(
                    ft.dropdown.Option(
                        str(usuario.ID),
                        f"{usuario.NOMBRE_COMPLETO} - {usuario.ROL}"
                    )
                )
            
            safe_update(self._pagina)
            
        except Exception as e:
            print(f"Error al cargar usuarios: {e}")
    
    def _actualizar_estadisticas(self):
        """Actualiza las estadísticas del header"""
        try:
            sesion = OBTENER_SESION()
            
            # Registros de hoy
            hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            count_hoy = sesion.query(MODELO_AUDITORIA).filter(
                MODELO_AUDITORIA.FECHA >= hoy
            ).count()
            self._stat_hoy.value = str(count_hoy)
            
            # Registros de esta semana
            semana = datetime.now() - timedelta(days=7)
            count_semana = sesion.query(MODELO_AUDITORIA).filter(
                MODELO_AUDITORIA.FECHA >= semana
            ).count()
            self._stat_semana.value = str(count_semana)
            
            # Usuarios únicos activos (que han hecho algo en la última semana)
            usuarios_activos = sesion.query(MODELO_AUDITORIA.USUARIO_ID).filter(
                MODELO_AUDITORIA.FECHA >= semana
            ).distinct().count()
            self._stat_usuarios.value = str(usuarios_activos)
            
            # Errores en la última semana
            count_errores = sesion.query(MODELO_AUDITORIA).filter(
                and_(
                    MODELO_AUDITORIA.FECHA >= semana,
                    MODELO_AUDITORIA.ACCION.ilike('%ERROR%')
                )
            ).count()
            self._stat_errores.value = str(count_errores)
            
            safe_update(self._pagina)
            
        except Exception as e:
            print(f"Error al actualizar estadísticas: {e}")
    
    def _cargar_registros(self):
        """Carga los registros de auditoría según los filtros activos"""
        try:
            sesion = OBTENER_SESION()
            
            # Query base
            query = sesion.query(MODELO_AUDITORIA).filter(
                and_(
                    MODELO_AUDITORIA.FECHA >= self._fecha_inicio,
                    MODELO_AUDITORIA.FECHA <= self._fecha_fin
                )
            )
            
            # Aplicar filtros
            if self._filtro_accion != "TODOS":
                query = query.filter(MODELO_AUDITORIA.ACCION.ilike(f"%{self._filtro_accion}%"))
            
            if self._filtro_entidad != "TODOS":
                query = query.filter(MODELO_AUDITORIA.ENTIDAD == self._filtro_entidad)
            
            if self._filtro_usuario and self._filtro_usuario != "TODOS":
                query = query.filter(MODELO_AUDITORIA.USUARIO_ID == int(self._filtro_usuario))
            
            if self._filtro_texto:
                query = query.filter(
                    or_(
                        MODELO_AUDITORIA.ACCION.ilike(f"%{self._filtro_texto}%"),
                        MODELO_AUDITORIA.DETALLE.ilike(f"%{self._filtro_texto}%")
                    )
                )
            
            # Ordenar y limitar
            registros = query.order_by(desc(MODELO_AUDITORIA.FECHA)).limit(100).all()
            
            # Actualizar interfaz
            self._actualizar_lista(registros)
            
            # Actualizar estadísticas
            self._actualizar_estadisticas()
            
        except Exception as e:
            Notificador.ERROR(self._pagina, f"Error al cargar registros: {str(e)}")
    
    def _actualizar_lista(self, registros: List[MODELO_AUDITORIA]):
        """Actualiza la lista de registros en la interfaz"""
        self._lista_registros.controls.clear()
        
        if not registros:
            self._lista_registros.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.Icons.SEARCH_OFF, size=64, color=COLORES.TEXTO_SECUNDARIO),
                        ft.Text(
                            "No se encontraron registros",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=COLORES.TEXTO_SECUNDARIO
                        ),
                        ft.Text(
                            "Intenta ajustar los filtros o el rango de fechas",
                            size=14,
                            color=COLORES.TEXTO_SECUNDARIO
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                    padding=40,
                    alignment=ft.alignment.center
                )
            )
        else:
            for registro in registros:
                self._lista_registros.controls.append(self._crear_card_registro(registro))
        
        # Actualizar contador
        self._contador_registros.value = f"{len(registros)} registro(s) encontrado(s)"
        
        safe_update(self._pagina)
    
    # Métodos de filtros
    def _cambiar_filtro_accion(self, e):
        self._filtro_accion = e.control.value
        self._cargar_registros()
    
    def _cambiar_filtro_entidad(self, e):
        self._filtro_entidad = e.control.value
        self._cargar_registros()
    
    def _cambiar_filtro_usuario(self, e):
        self._filtro_usuario = e.control.value
        self._cargar_registros()
    
    def _cambiar_busqueda(self, e):
        self._filtro_texto = e.control.value
        self._cargar_registros()
    
    def _aplicar_rango(self, dias: int):
        if dias == 0:
            # Hoy
            self._fecha_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            self._fecha_inicio = datetime.now() - timedelta(days=dias)
        
        self._fecha_fin = datetime.now()
        self._cargar_registros()
    
    def _limpiar_filtros(self, e):
        """Limpia todos los filtros y recarga"""
        self._filtro_accion = "TODOS"
        self._filtro_entidad = "TODOS"
        self._filtro_usuario = "TODOS"
        self._filtro_texto = ""
        self._fecha_inicio = datetime.now() - timedelta(days=7)
        self._fecha_fin = datetime.now()
        
        # Actualizar controles (solo si existen)
        if self._dropdown_usuarios:
            self._dropdown_usuarios.value = "TODOS"
        
        self._cargar_registros()
    
    def _exportar(self, e):
        """Exporta los registros actuales (placeholder)"""
        Notificador.INFO(self._pagina, "Función de exportación en desarrollo...")
    
    def _ir_dashboard(self, e=None):
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._pagina.controls.clear()
        self._pagina.add(PaginaAdmin(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _cerrar_sesion(self, e=None):
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._pagina.controls.clear()
        self._pagina.add(PaginaLogin(self._pagina))
        safe_update(self._pagina)
