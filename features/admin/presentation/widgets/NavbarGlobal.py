"""
Navbar Global Mejorado
Aparece en todas las vistas con filtro de sucursales múltiples
"""
import flet as ft
from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES
from typing import Callable, Optional, List
from core.ui.safe_actions import safe_update
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_SUCURSAL, MODELO_AUDITORIA
from core.cache.GestorRedis import REDIS_GLOBAL
from datetime import datetime


class NavbarGlobal(ft.Container):
    """Barra de navegación global con selector de sucursales mejorado"""
    
    def __init__(
        self,
        pagina: ft.Page,
        usuario,
        titulo_vista: str = "Dashboard Administrativo",
        mostrar_boton_volver: bool = False,
        on_volver: Optional[Callable] = None,
        on_cambio_sucursales: Optional[Callable] = None,
        on_cerrar_sesion: Optional[Callable] = None
    ):
        super().__init__()
        self._pagina = pagina
        self._usuario = usuario
        self._titulo_vista = titulo_vista
        self._mostrar_boton_volver = mostrar_boton_volver
        self._on_volver = on_volver
        self._on_cambio_sucursales = on_cambio_sucursales
        self._on_cerrar_sesion = on_cerrar_sesion
        
        # Estado de sucursales seleccionadas
        self._sucursales_seleccionadas: List[int] = []
        self._todas_seleccionadas = True
        
        # Componentes
        self._panel_sucursales = None
        self._btn_sucursales = None
        self._checkboxes = {}
        self._texto_titulo = None  # Referencia al texto del título
        
        self._construir()
    
    def _construir(self):
        """Construye el navbar"""
        
        # Botón de sucursales con ícono y contador
        self._btn_sucursales = ft.Button(
            content=ft.Row([
                ft.Icon(ft.icons.Icons.STORE, size=20, color=ft.Colors.WHITE),
                ft.Text(
                    self._obtener_texto_sucursales(),
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.WHITE
                ),
                ft.Icon(ft.icons.Icons.ARROW_DROP_DOWN, size=20, color=ft.Colors.WHITE),
            ], spacing=5, tight=True),
            on_click=self._toggle_panel,
            bgcolor=COLORES.PRIMARIO,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10)
            ),
            height=45
        )
        
        # Panel desplegable de sucursales - Mejorado para mejor visibilidad
        self._panel_sucursales = ft.Container(
            content=self._crear_contenido_panel(),
            visible=False,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(3, COLORES.PRIMARIO),
            border_radius=16,
            padding=20,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=20,
                color=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
                offset=ft.Offset(0, 8)
            ),
            width=380,
            margin=ft.margin.only(top=5)
        )
        
        # Información del usuario
        rol_usuario = self._usuario.ROLES[0].NOMBRE if hasattr(self._usuario.ROLES[0], 'NOMBRE') else self._usuario.ROLES[0]
        info_usuario = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.Icons.ACCOUNT_CIRCLE, size=24, color=COLORES.INFO),
                ft.Column([
                    ft.Text(
                        getattr(self._usuario, 'NOMBRE_COMPLETO', None) or 
                        getattr(self._usuario, 'NOMBRE_USUARIO', 'Usuario'),
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        color=COLORES.TEXTO
                    ),
                    ft.Text(
                        rol_usuario.replace("_", " ").title(),
                        size=11,
                        color=COLORES.TEXTO_SECUNDARIO
                    ),
                ], spacing=2, tight=True)
            ], spacing=8, tight=True),
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            border_radius=8,
            bgcolor=ft.Colors.BLUE_50
        )
        
        # Botón de cerrar sesión
        btn_logout = ft.IconButton(
            icon=ft.icons.Icons.LOGOUT,
            tooltip="Cerrar Sesión",
            on_click=self._cerrar_sesion,
            icon_color=ft.Colors.WHITE,
            bgcolor=COLORES.PELIGRO,
            icon_size=20,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10)
            )
        )
        
        # Layout del navbar con panel overlay
        self._texto_titulo = ft.Text(
            self._titulo_vista,
            size=20,
            weight=ft.FontWeight.BOLD,
            color=COLORES.TEXTO
        )
        
        # Crear fila con título y botón volver (si aplica)
        titulo_row = []
        if self._mostrar_boton_volver and self._on_volver:
            titulo_row.append(
                ft.IconButton(
                    icon=ft.icons.Icons.ARROW_BACK,
                    tooltip="Volver",
                    on_click=lambda e: self._on_volver(),
                    icon_color=COLORES.PRIMARIO,
                    icon_size=22
                )
            )
        titulo_row.append(self._texto_titulo)
        
        navbar_content = ft.Row([
                ft.Row(titulo_row, spacing=5),
                ft.Container(expand=True),
                self._btn_sucursales,
                info_usuario,
                btn_logout
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.content = navbar_content
        self.bgcolor = ft.Colors.WHITE
        self.padding = ft.padding.symmetric(horizontal=20, vertical=12)
        self.border = ft.border.only(bottom=ft.BorderSide(2, COLORES.BORDE))
        self.shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=4,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 2)
        )
    
    def _crear_contenido_panel(self) -> ft.Column:
        """Crea el contenido del panel de sucursales"""
        sesion = OBTENER_SESION()
        sucursales = sesion.query(MODELO_SUCURSAL).filter_by(ACTIVA=True).all()
        sesion.close()
        
        # Checkbox "Todas"
        checkbox_todas = ft.Checkbox(
            label="📍 Todas las Sucursales",
            value=True,
            on_change=self._on_todas_change,
            fill_color=COLORES.PRIMARIO,
            label_style=ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                size=14
            )
        )
        
        # Checkboxes individuales con mejor diseño
        checkboxes_list = [
            checkbox_todas, 
            ft.Divider(height=15, color=COLORES.BORDE)
        ]
        
        for sucursal in sucursales:
            checkbox = ft.Checkbox(
                label=f"🏪 {sucursal.NOMBRE}",
                value=False,
                data=sucursal.ID,
                on_change=self._on_sucursal_change,
                fill_color=COLORES.INFO,
                check_color=ft.Colors.WHITE,
                label_style=ft.TextStyle(
                    size=14,
                    color=COLORES.TEXTO
                ),
                active_color=COLORES.PRIMARIO
            )
            self._checkboxes[sucursal.ID] = checkbox
            
            # Wrapper con hover effect
            checkbox_container = ft.Container(
                content=checkbox,
                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                border_radius=8,
                ink=True
            )
            checkboxes_list.append(checkbox_container)
        
        # Botones de acción más grandes y visibles
        botones = ft.Row([
            ft.OutlinedButton(
                "Cancelar",
                icon=ft.icons.Icons.CLOSE,
                on_click=lambda e: self._toggle_panel(None),
                style=ft.ButtonStyle(
                    color=COLORES.TEXTO_SECUNDARIO,
                    side=ft.BorderSide(2, COLORES.BORDE)
                ),
                height=45
            ),
            ft.Button(
                "Aplicar Filtros",
                icon=ft.icons.Icons.CHECK_CIRCLE,
                on_click=self._aplicar_filtros,
                bgcolor=COLORES.EXITO,
                color=ft.Colors.WHITE,
                height=45,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10)
                )
            )
        ], alignment=ft.MainAxisAlignment.END, spacing=15)
        
        self._checkbox_todas = checkbox_todas
        
        return ft.Column([
            ft.Container(
                content=ft.Text(
                    "🏪 Seleccionar Sucursales",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=COLORES.PRIMARIO
                ),
                padding=ft.padding.only(bottom=10)
            ),
            ft.Divider(height=20, color=COLORES.PRIMARIO),
            ft.Container(
                content=ft.Column(
                    controls=checkboxes_list,
                    spacing=5,
                    scroll=ft.ScrollMode.ADAPTIVE
                ),
                height=280,
                border=ft.border.all(1, COLORES.BORDE),
                border_radius=8,
                padding=10,
                bgcolor=ft.Colors.GREY_50
            ),
            ft.Divider(height=15),
            botones
        ], spacing=5, tight=True)
    
    def _obtener_texto_sucursales(self) -> str:
        """Obtiene el texto a mostrar en el botón"""
        if self._todas_seleccionadas or len(self._sucursales_seleccionadas) == 0:
            return "Todas las Sucursales"
        elif len(self._sucursales_seleccionadas) == 1:
            sesion = OBTENER_SESION()
            suc = sesion.query(MODELO_SUCURSAL).filter_by(ID=self._sucursales_seleccionadas[0]).first()
            sesion.close()
            return suc.NOMBRE if suc else "1 Sucursal"
        else:
            return f"{len(self._sucursales_seleccionadas)} Sucursales"
    
    def _toggle_panel(self, e):
        """Muestra/oculta el panel usando page.overlay"""
        self._panel_sucursales.visible = not self._panel_sucursales.visible
        print(f"📍 Toggle panel: visible={self._panel_sucursales.visible}")
        
        # Usar page.overlay para que aparezca por encima de todo
        if self._panel_sucursales.visible:
            # Calcular posición del botón
            panel_overlay = ft.Container(
                content=self._panel_sucursales,
                right=20,
                top=70,
                width=380
            )
            
            # Añadir al overlay de la página
            if not any(isinstance(c, ft.Container) and c.content == self._panel_sucursales for c in self._pagina.overlay):
                self._pagina.overlay.append(panel_overlay)
        else:
            # Remover del overlay
            items_to_remove = [c for c in self._pagina.overlay if isinstance(c, ft.Container) and c.content == self._panel_sucursales]
            for item in items_to_remove:
                self._pagina.overlay.remove(item)
        
        try:
            self._pagina.update()
        except Exception as ex:
            print(f"⚠️ Error actualizando página: {ex}")
    
    def _on_todas_change(self, e):
        """Maneja el cambio del checkbox 'Todas'"""
        todas = e.control.value
        
        # Deshabilitar/habilitar checkboxes individuales
        for checkbox in self._checkboxes.values():
            checkbox.value = False
            checkbox.disabled = todas
        
        safe_update(self._pagina)
    
    def _on_sucursal_change(self, e):
        """Maneja el cambio de checkboxes individuales"""
        # Si se selecciona alguna, desmarcar "Todas"
        self._checkbox_todas.value = False
        safe_update(self._pagina)
    
    def _aplicar_filtros(self, e):
        """Aplica los filtros seleccionados"""
        if self._checkbox_todas.value:
            self._todas_seleccionadas = True
            self._sucursales_seleccionadas = []
        else:
            self._todas_seleccionadas = False
            self._sucursales_seleccionadas = [
                suc_id for suc_id, checkbox in self._checkboxes.items()
                if checkbox.value
            ]
        
        # Actualizar texto del botón
        self._btn_sucursales.content.controls[1].value = self._obtener_texto_sucursales()
        
        # Cerrar panel
        self._panel_sucursales.visible = False
        
        # Actualizar atributo del usuario
        if self._todas_seleccionadas:
            setattr(self._usuario, 'SUCURSALES_SELECCIONADAS', None)
        else:
            setattr(self._usuario, 'SUCURSALES_SELECCIONADAS', self._sucursales_seleccionadas)
        
        # Registrar en auditoría
        self._registrar_cambio_sucursales()
        
        # Callback externo
        if self._on_cambio_sucursales:
            self._on_cambio_sucursales(self._sucursales_seleccionadas if not self._todas_seleccionadas else None)
        
        safe_update(self._pagina)
    
    def _registrar_cambio_sucursales(self):
        """Registra el cambio de sucursales en auditoría"""
        try:
            sesion = OBTENER_SESION()
            
            if self._todas_seleccionadas:
                detalles = "Filtro: Todas las sucursales"
            else:
                sucursales_nombres = []
                for suc_id in self._sucursales_seleccionadas:
                    suc = sesion.query(MODELO_SUCURSAL).filter_by(ID=suc_id).first()
                    if suc:
                        sucursales_nombres.append(suc.NOMBRE)
                detalles = f"Filtro: {', '.join(sucursales_nombres)}"
            
            auditoria = MODELO_AUDITORIA(
                USUARIO_ID=self._usuario.ID,
                ACCION="CAMBIO_FILTRO_SUCURSALES",
                ENTIDAD="NAVBAR",
                DETALLE=detalles,
                FECHA=datetime.now()
            )
            sesion.add(auditoria)
            sesion.commit()
            sesion.close()
        except Exception as e:
            print(f"Error registrando auditoría: {e}")
    
    def _cerrar_sesion(self, e):
        """Cierra la sesión del usuario"""
        if self._on_cerrar_sesion:
            self._on_cerrar_sesion()
    
    def obtener_sucursales_seleccionadas(self) -> Optional[List[int]]:
        """Retorna las sucursales seleccionadas (None = todas)"""
        if self._todas_seleccionadas:
            return None
        return self._sucursales_seleccionadas
    
    def actualizar_titulo(self, nuevo_titulo: str):
        """Actualiza el título mostrado en el navbar"""
        self._titulo_vista = nuevo_titulo
        if self._texto_titulo:
            self._texto_titulo.value = nuevo_titulo
            if self._pagina:
                try:
                    self._pagina.update()
                except:
                    pass
    
    def recargar_sucursales(self):
        """Recarga las sucursales del panel después de cambios en BD"""
        try:
            # Guardar estado actual
            todas_seleccionadas = self._todas_seleccionadas
            sucursales_ids = list(self._sucursales_seleccionadas)
            
            # Limpiar checkboxes actuales
            self._checkboxes.clear()
            
            # Recrear panel con datos actualizados
            nuevo_contenido = self._crear_contenido_panel()
            
            # Restaurar selecciones si es posible
            if todas_seleccionadas:
                if self._checkbox_todas:
                    self._checkbox_todas.value = True
            else:
                for suc_id in sucursales_ids:
                    if suc_id in self._checkboxes:
                        self._checkboxes[suc_id].value = True
            
            # Actualizar el contenido del panel
            if hasattr(self, '_panel_sucursales') and self._panel_sucursales:
                self._panel_sucursales.content = nuevo_contenido
                
                # Actualizar texto del botón
                if self._btn_sucursales:
                    self._btn_sucursales.text = self._obtener_texto_sucursales()
                
                if self._pagina:
                    self._pagina.update()
        except Exception as e:
            print(f"⚠️ Error recargando sucursales en navbar: {e}")
    
    def _es_superadmin(self) -> bool:
        """Verificar si el usuario es superadmin"""
        try:
            rol = self._usuario.ROLES[0].NOMBRE if hasattr(self._usuario.ROLES[0], 'NOMBRE') else self._usuario.ROLES[0]
            return rol == "SUPERADMIN"
        except:
            return False
    
    def _ir_dashboard(self, e):
        """Navegar al dashboard"""
        try:
            from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
            self._pagina.controls.clear()
            self._pagina.add(PaginaAdmin(self._pagina, self._usuario))
            self._pagina.update()
        except Exception as ex:
            print(f"Error navegando a dashboard: {ex}")
    
    def _ir_usuarios(self, e):
        """Navegar a gestión de usuarios"""
        try:
            from features.gestion_usuarios.presentation.pages.PaginaGestionUsuarios import PaginaGestionUsuarios
            self._pagina.controls.clear()
            self._pagina.add(PaginaGestionUsuarios(self._pagina, self._usuario))
            self._pagina.update()
        except Exception as ex:
            print(f"Error navegando a usuarios: {ex}")
    
    def _ir_productos(self, e):
        """Navegar a gestión de productos"""
        try:
            from features.admin.presentation.pages.gestion.ProductosPage import ProductosPage
            self._pagina.controls.clear()
            self._pagina.add(ProductosPage(self._pagina, self._usuario))
            self._pagina.update()
        except Exception as ex:
            print(f"Error navegando a productos: {ex}")
    
    def _ir_pedidos(self, e):
        """Navegar a gestión de pedidos"""
        try:
            from features.admin.presentation.pages.vistas.PedidosPage import PedidosPage
            self._pagina.controls.clear()
            self._pagina.add(PedidosPage(self._pagina, self._usuario))
            self._pagina.update()
        except Exception as ex:
            print(f"Error navegando a pedidos: {ex}")
    
    def _ir_finanzas(self, e):
        """Navegar a finanzas y reportes"""
        try:
            from features.admin.presentation.pages.vistas.FinanzasPage import FinanzasPage
            self._pagina.controls.clear()
            self._pagina.add(FinanzasPage(self._pagina, self._usuario))
            self._pagina.update()
        except Exception as ex:
            print(f"Error navegando a finanzas: {ex}")
    
    def _ir_vouchers(self, e):
        """Navegar a validación de vouchers"""
        try:
            from features.admin.presentation.pages.vistas.VouchersPage import VouchersPage
            self._pagina.controls.clear()
            self._pagina.add(VouchersPage(self._pagina, self._usuario))
            self._pagina.update()
        except Exception as ex:
            print(f"Error navegando a vouchers: {ex}")
    
    def _ir_sucursales(self, e):
        """Navegar a gestión de sucursales"""
        try:
            from features.admin.presentation.pages.vistas.SucursalesPage import SucursalesPage
            self._pagina.controls.clear()
            self._pagina.add(SucursalesPage(self._pagina, self._usuario))
            self._pagina.update()
        except Exception as ex:
            print(f"Error navegando a sucursales: {ex}")
    
    def _ir_roles(self, e):
        """Navegar a gestión de roles"""
        try:
            from features.admin.presentation.pages.gestion.RolesPage import RolesPage
            self._pagina.controls.clear()
            self._pagina.add(RolesPage(self._pagina, self._usuario))
            self._pagina.update()
        except Exception as ex:
            print(f"Error navegando a roles: {ex}")
