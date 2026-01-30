
import flet as ft

from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES, ERRORES_AUTENTICACION
from features.autenticacion.domain.entities.Usuario import Usuario
from core.decoradores.DecoradorVistas import REQUIERE_ROL
from core.ui.safe_actions import safe_update

from ..bloc import (
    ADMIN_BLOC,
    AdminEstado,
    AdminInicial,
    AdminCargando,
    AdminCargado,
    AdminError,
    AdminRolActualizado,
    CargarDashboard,
    ActualizarRol,
)

from ..widgets import (
    CardEstadistica,
    GraficoRoles,
    GraficoSucursales,
    GraficoSemanal,
    GraficoInventario,
    LayoutBase,
)

from ...domain.usecases import ObtenerRolesDisponibles
from ...data.RepositorioAdminImpl import REPOSITORIO_ADMIN_IMPL

@REQUIERE_ROL(ROLES.SUPERADMIN, ROLES.ADMIN)
class PaginaAdmin(LayoutBase):
    """Dashboard Admin usando LayoutBase global"""

    def __init__(self, PAGINA: ft.Page, USUARIO: Usuario):
        print("🔵 PaginaAdmin.__init__ - INICIO")
        # Inicializar layout base
        super().__init__(
            pagina=PAGINA,
            usuario=USUARIO,
            titulo_vista="Dashboard Administrativo",
            mostrar_boton_volver=False,
            index_navegacion=0,  # Dashboard es el primer item
            on_volver_dashboard=None,  # No hay volver en dashboard
            on_cerrar_sesion=self._SALIR
        )
        print("🔵 PaginaAdmin - super().__init__ completado")
        
        self._card_usuarios: CardEstadistica = None
        self._card_pedidos: CardEstadistica = None
        self._card_ganancias: CardEstadistica = None
        self._card_productos: CardEstadistica = None
        
        self._grafico_roles: GraficoRoles = None
        self._grafico_sucursales: GraficoSucursales = None
        self._grafico_semanal: GraficoSemanal = None
        self._grafico_inventario: GraficoInventario = None
        
        # Construir contenido
        print("🔵 PaginaAdmin - Llamando _CONSTRUIR_CONTENIDO()")
        self._CONSTRUIR_CONTENIDO()
        print(f"🔵 PaginaAdmin - _CONSTRUIR_CONTENIDO() completado. self.controls tiene {len(self.controls)} items")
        
        ADMIN_BLOC.CONFIGURAR_PAGINA(PAGINA)
        ADMIN_BLOC.AGREGAR_LISTENER(self._ON_ESTADO_CAMBIO)
        
        # Cargar dashboard con sucursales seleccionadas
        sucursales = self.obtener_sucursales_seleccionadas()
        sucursal_id = sucursales[0] if sucursales and len(sucursales) == 1 else None
        print(f"🔵 PaginaAdmin - Cargando dashboard con sucursal_id={sucursal_id}")
        ADMIN_BLOC.AGREGAR_EVENTO(CargarDashboard(sucursal_id=sucursal_id))
        print("🔵 PaginaAdmin.__init__ - FIN")
    
    def _on_sucursales_change(self, sucursales_ids):
        """OVERRIDE: Callback cuando cambian las sucursales seleccionadas"""
        # Recargar dashboard con nuevas sucursales
        if sucursales_ids is None or len(sucursales_ids) == 0:
            # Todas las sucursales
            ADMIN_BLOC.AGREGAR_EVENTO(CargarDashboard(sucursal_id=None))
        elif len(sucursales_ids) == 1:
            # Una sola sucursal
            ADMIN_BLOC.AGREGAR_EVENTO(CargarDashboard(sucursal_id=sucursales_ids[0]))
        else:
            # Múltiples sucursales - cargar sin filtro (todas)
            ADMIN_BLOC.AGREGAR_EVENTO(CargarDashboard(sucursal_id=None))

    def _CONSTRUIR_CONTENIDO(self):
        """Construye el contenido específico del dashboard"""
        # LayoutBase ya crea el NavbarGlobal automáticamente
        
        self._card_usuarios = CardEstadistica(
            icono=ICONOS.USUARIOS,
            valor="...",
            etiqueta="Usuarios",
            color_icono=COLORES.PRIMARIO
        )
        
        self._card_pedidos = CardEstadistica(
            icono=ICONOS.PEDIDOS,
            valor="...",
            etiqueta="Pedidos Hoy",
            color_icono=COLORES.EXITO
        )
        
        self._card_ganancias = CardEstadistica(
            icono=ICONOS.CAJA,
            valor="...",
            etiqueta="Ganancias Hoy",
            color_icono=COLORES.ADVERTENCIA
        )
        
        self._card_productos = CardEstadistica(
            icono=ICONOS.PRODUCTOS,
            valor="...",
            etiqueta="Productos",
            color_icono=COLORES.INFO
        )
        
        stats_row = ft.ResponsiveRow(
            [
                ft.Container(self._card_usuarios, col={"xs": 12, "sm": 6, "md": 3}),
                ft.Container(self._card_pedidos, col={"xs": 12, "sm": 6, "md": 3}),
                ft.Container(self._card_ganancias, col={"xs": 12, "sm": 6, "md": 3}),
                ft.Container(self._card_productos, col={"xs": 12, "sm": 6, "md": 3}),
            ],
            spacing=10,
            run_spacing=10,
        )
        
        self._grafico_roles = GraficoRoles()
        self._grafico_sucursales = GraficoSucursales()
        self._grafico_semanal = GraficoSemanal()
        self._grafico_inventario = GraficoInventario()
        
        graficos_row = ft.ResponsiveRow(
            [
                ft.Container(
                    self._CREAR_CONTENEDOR_GRAFICO(
                        "Usuarios por Rol",
                        self._grafico_roles
                    ),
                    col={"xs": 12, "md": 6}
                ),
                ft.Container(
                    self._CREAR_CONTENEDOR_GRAFICO(
                        "Pedidos por Sucursal",
                        self._grafico_sucursales
                    ),
                    col={"xs": 12, "md": 6}
                ),
            ],
            spacing=10,
            run_spacing=10,
        )
        
        graficos_row2 = ft.ResponsiveRow(
            [
                ft.Container(
                    self._CREAR_CONTENEDOR_GRAFICO(
                        "Pedidos Última Semana",
                        self._grafico_semanal
                    ),
                    col={"xs": 12, "md": 6}
                ),
                ft.Container(
                    self._CREAR_CONTENEDOR_GRAFICO(
                        "Estado Inventario",
                        self._grafico_inventario
                    ),
                    col={"xs": 12, "md": 6}
                ),
            ],
            spacing=10,
            run_spacing=10,
        )
        
        contenido = ft.Container(
            content=ft.Column(
                [
                    stats_row,
                    ft.Divider(height=1, color=COLORES.BORDE),
                    graficos_row,
                    graficos_row2,
                ],
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=15,
            expand=True
        )

        # Llamar a construir() del layout base
        self.construir(contenido)
    
    def _CREAR_CONTENEDOR_GRAFICO(self, titulo: str, grafico: ft.Control) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        titulo,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=COLORES.TEXTO
                    ),
                    ft.Container(
                        content=grafico,
                        expand=True
                    ),
                ],
                spacing=10,
                expand=True
            ),
            padding=15,
            bgcolor=COLORES.FONDO_BLANCO,
            border_radius=TAMANOS.RADIO_MD,
            border=ft.Border.all(1, COLORES.BORDE),
            expand=True,
        )
    
    def _CONSTRUIR_BOTONES_GESTION(self) -> ft.Row:
        # Botones comunes para ADMIN y SUPERADMIN
        botones = [
            self._CREAR_BOTON_GESTION("Gestión de Usuarios", ICONOS.USUARIOS, self._VER_GESTION_USUARIOS, COLORES.PRIMARIO),
            self._CREAR_BOTON_GESTION("Gestionar Productos", ICONOS.PRODUCTOS, self._VER_PRODUCTOS, COLORES.EXITO),
            self._CREAR_BOTON_GESTION("Gestión Pedidos", ICONOS.PEDIDOS, self._VER_PEDIDOS_ADMIN, COLORES.EXITO),
            self._CREAR_BOTON_GESTION("Validar Vouchers", ICONOS.VOUCHER, self._VER_VALIDAR_VOUCHERS, COLORES.ADVERTENCIA),
            self._CREAR_BOTON_GESTION("Finanzas y Control", ICONOS.CAJA, self._VER_FINANZAS, COLORES.EXITO),
            self._CREAR_BOTON_GESTION("Extras", ft.icons.Icons.ADD_CIRCLE, self._VER_EXTRAS, COLORES.INFO_OSCURO),
            self._CREAR_BOTON_GESTION("Ofertas", ft.icons.Icons.LOCAL_OFFER, self._VER_OFERTAS, COLORES.ADVERTENCIA),
            self._CREAR_BOTON_GESTION("Horarios", ft.icons.Icons.SCHEDULE, self._VER_HORARIOS, COLORES.INFO),
            self._CREAR_BOTON_GESTION("Insumos", ICONOS.INSUMOS, self._VER_INSUMOS, COLORES.INFO),
            self._CREAR_BOTON_GESTION("Proveedores", ICONOS.PROVEEDORES, self._VER_PROVEEDORES, COLORES.PRIMARIO_OSCURO),
            self._CREAR_BOTON_GESTION("Caja", ICONOS.CAJA, self._VER_CAJA, COLORES.EXITO_OSCURO),
            self._CREAR_BOTON_GESTION("Reseñas", ICONOS.RESENAS, self._VER_RESENAS, COLORES.ADVERTENCIA_OSCURO),
        ]
        
        # Botones EXCLUSIVOS para SUPERADMIN
        rol_usuario = self._usuario.ROLES[0].NOMBRE if hasattr(self._usuario.ROLES[0], 'NOMBRE') else self._usuario.ROLES[0]
        if rol_usuario == "SUPERADMIN":
            botones.insert(0, self._CREAR_BOTON_GESTION("Gestionar Roles", ICONOS.ROLES, self._ABRIR_GESTION_ROLES, COLORES.SECUNDARIO))
            botones.insert(4, self._CREAR_BOTON_GESTION("Gestionar Sucursales", ft.icons.Icons.STORE, self._VER_SUCURSALES, COLORES.ADVERTENCIA))
            botones.append(self._CREAR_BOTON_GESTION("Auditoría", ICONOS.AUDITORIA, self._VER_AUDITORIA, COLORES.GRIS_OSCURO))
        
        return ft.ResponsiveRow(
            [ft.Container(btn, col={"xs": 12, "sm": 6, "md": 4, "lg": 3}) for btn in botones],
            spacing=10,
            run_spacing=10,
        )
    
    def _CREAR_BOTON_GESTION(self, texto: str, icono: str, handler, bgcolor: str) -> ft.Button:
        return ft.Button(
            content=ft.Text(texto, color=COLORES.TEXTO_BLANCO),
            icon=icono,
            on_click=handler,
            bgcolor=bgcolor,
        )
    
    def _ON_ESTADO_CAMBIO(self, estado: AdminEstado):
        if isinstance(estado, AdminCargando):
            self._MOSTRAR_CARGANDO()
        
        elif isinstance(estado, AdminCargado):
            self._ACTUALIZAR_UI_CON_DATOS(estado.dashboard)
        
        elif isinstance(estado, AdminRolActualizado):
            self._MOSTRAR_EXITO(estado.mensaje)
            if estado.dashboard:
                self._ACTUALIZAR_UI_CON_DATOS(estado.dashboard)
        
        elif isinstance(estado, AdminError):
            self._MOSTRAR_ERROR(estado.mensaje)
    
    def _MOSTRAR_CARGANDO(self):
        pass
    
    def _ACTUALIZAR_UI_CON_DATOS(self, dashboard):
        try:
            stats = dashboard.estadisticas_generales
            
            if self._card_usuarios and self._card_usuarios.content:
                self._card_usuarios.content.controls[1].value = str(stats.total_usuarios)
            
            if self._card_pedidos and self._card_pedidos.content:
                self._card_pedidos.content.controls[1].value = str(stats.total_pedidos_hoy)
            
            if self._card_ganancias and self._card_ganancias.content:
                self._card_ganancias.content.controls[1].value = f"{stats.ganancias_hoy:.2f} Bs"
            
            if self._card_productos and self._card_productos.content:
                self._card_productos.content.controls[1].value = str(stats.total_productos)
            
            if self._grafico_roles:
                self._grafico_roles.ACTUALIZAR_DATOS(dashboard.estadisticas_roles)
            
            if self._grafico_sucursales:
                self._grafico_sucursales.ACTUALIZAR_DATOS(dashboard.estadisticas_sucursales)
            
            if self._grafico_semanal:
                self._grafico_semanal.ACTUALIZAR_DATOS(dashboard.estadisticas_semanales)
            
            if self._grafico_inventario:
                self._grafico_inventario.ACTUALIZAR_DATOS(dashboard.estadisticas_inventario)
            
            if self._pagina and hasattr(self._pagina, 'update'):
                safe_update(self._pagina)
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def _ABRIR_GESTION_ROLES(self, e):
        try:
            if not self._usuario.TIENE_ROL(ROLES.SUPERADMIN):
                self._MOSTRAR_ERROR(ERRORES_AUTENTICACION.PERMISOS_INSUFICIENTES)
                return
            
            from features.admin.presentation.pages.gestion.RolesPage import RolesPage
            
            self._pagina.controls.clear()
            self._pagina.add(RolesPage(self._pagina, self._usuario))
            safe_update(self._pagina)
            
        except Exception as error:
            self._MOSTRAR_ERROR(f"Error: {str(error)}")

    def _ABRIR_CAMBIO_ROL(self, USUARIO):
        usecase_roles = ObtenerRolesDisponibles(REPOSITORIO_ADMIN_IMPL)
        roles = usecase_roles.EJECUTAR()
        
        if not roles:
            self._MOSTRAR_ERROR("No se pudieron cargar los roles")
            return
        
        opciones = [ft.dropdown.Option(r.NOMBRE) for r in roles]
        actual = USUARIO.ROLES[0].NOMBRE if USUARIO.ROLES else ""

        campo_rol = ft.Dropdown(
            label="Rol",
            options=opciones,
            value=actual,
        )

        def GUARDAR(e):
            if not campo_rol.value:
                self._MOSTRAR_ERROR("Selecciona un rol")
                return

            ADMIN_BLOC.AGREGAR_EVENTO(
                ActualizarRol(
                    usuario_id=USUARIO.ID,
                    nombre_rol=campo_rol.value
                )
            )
            self._CERRAR_DLG(None)

        dlg = ft.AlertDialog(
            title=ft.Text(f"Rol de {USUARIO.NOMBRE_USUARIO}", color=COLORES.TEXTO),
            content=ft.Container(
                content=ft.Column(
                    controls=[campo_rol],
                    spacing=TAMANOS.ESPACIADO_MD,
                    tight=True,
                ),
                width=TAMANOS.ANCHO_CARD,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DLG(e)),
                ft.Button(
                    "Guardar",
                    on_click=GUARDAR,
                    bgcolor=COLORES.PRIMARIO,
                    color=COLORES.TEXTO_BLANCO
                ),
            ],
        )

        self._pagina.dialog = dlg
        dlg.open = True
        safe_update(self._pagina)

    def _VER_GESTION_USUARIOS(self, e):
        """Abre la nueva página de gestión de usuarios refactorizada"""
        from features.gestion_usuarios.presentation.pages.PaginaGestionUsuarios import PaginaGestionUsuarios
        
        ADMIN_BLOC.REMOVER_LISTENER(self._ON_ESTADO_CAMBIO)
        self._pagina.controls.clear()
        self._pagina.controls.append(PaginaGestionUsuarios(self._pagina, self._usuario))
        safe_update(self._pagina)

    def _ABRIR_CAMBIO_ROL(self, USUARIO):
        usecase_roles = ObtenerRolesDisponibles(REPOSITORIO_ADMIN_IMPL)
        roles = usecase_roles.EJECUTAR()
        
        if not roles:
            self._MOSTRAR_ERROR("No se pudieron cargar los roles")
            return
        
        opciones = [ft.dropdown.Option(r.NOMBRE) for r in roles]
        actual = USUARIO.ROLES[0].NOMBRE if USUARIO.ROLES else ""

        campo_rol = ft.Dropdown(
            label="Rol",
            options=opciones,
            value=actual,
        )

        def GUARDAR(e):
            if not campo_rol.value:
                self._MOSTRAR_ERROR("Selecciona un rol")
                return

            ADMIN_BLOC.AGREGAR_EVENTO(
                ActualizarRol(
                    usuario_id=USUARIO.ID,
                    nombre_rol=campo_rol.value
                )
            )
            self._CERRAR_DLG(None)

        dlg = ft.AlertDialog(
            title=ft.Text(f"Rol de {USUARIO.NOMBRE_USUARIO}", color=COLORES.TEXTO),
            content=ft.Container(
                content=ft.Column(
                    controls=[campo_rol],
                    spacing=TAMANOS.ESPACIADO_MD,
                    tight=True,
                ),
                width=TAMANOS.ANCHO_CARD,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._CERRAR_DLG(e)),
                ft.Button(
                    "Guardar",
                    on_click=GUARDAR,
                    bgcolor=COLORES.PRIMARIO,
                    color=COLORES.TEXTO_BLANCO
                ),
            ],
        )

        self._pagina.dialog = dlg
        dlg.open = True
        safe_update(self._pagina)

    def _OBTENER_ROLES(self):
        usecase = ObtenerRolesDisponibles(REPOSITORIO_ADMIN_IMPL)
        return usecase.EJECUTAR()

    def _ACTUALIZAR_ROL_USUARIO(self, USUARIO_ID: int, NOMBRE_ROL: str):
        ADMIN_BLOC.AGREGAR_EVENTO(
            ActualizarRol(usuario_id=USUARIO_ID, nombre_rol=NOMBRE_ROL)
        )

    def _CERRAR_DLG(self, e):
        if hasattr(self._pagina, "dialog") and self._pagina.dialog:
            self._pagina.dialog.open = False
            safe_update(self._pagina)

    def _VER_PRODUCTOS(self, e):
        from features.admin.presentation.pages.gestion.ProductosPage import ProductosPage
        
        self._pagina.controls.clear()
        self._pagina.controls.append(ProductosPage(self._pagina, self._usuario))
        safe_update(self._pagina)

    def _VER_SUCURSALES(self, e):
        from features.admin.presentation.pages.gestion.SucursalesPage import SucursalesPage
        
        self._pagina.controls.clear()
        self._pagina.controls.append(SucursalesPage(self._pagina, self._usuario))
        safe_update(self._pagina)

    def _VER_USUARIOS_AVANZADO(self, e):
        from features.admin.presentation.pages.gestion.UsuariosPage import UsuariosPage
        
        self._pagina.controls.clear()
        self._pagina.controls.append(UsuariosPage(self._pagina, self._usuario))
        safe_update(self._pagina)

    def _VER_EXTRAS(self, e):
        from features.admin.presentation.pages.gestion.ExtrasPage import ExtrasPage
        
        self._pagina.controls.clear()
        self._pagina.controls.append(ExtrasPage(self._pagina, self._usuario))
        safe_update(self._pagina)

    def _VER_OFERTAS(self, e):
        from features.admin.presentation.pages.gestion.OfertasPage import OfertasPage
        
        self._pagina.controls.clear()
        self._pagina.controls.append(OfertasPage(self._pagina, self._usuario))
        safe_update(self._pagina)

    def _VER_HORARIOS(self, e):
        from features.admin.presentation.pages.gestion.HorariosPage import HorariosPage
        
        self._pagina.controls.clear()
        self._pagina.controls.append(HorariosPage(self._pagina, self._usuario))
        safe_update(self._pagina)

    def _VER_PEDIDOS_ADMIN(self, e):
        from features.admin.presentation.pages.vistas.PedidosPage import PedidosPage

        self._pagina.controls.clear()
        self._pagina.controls.append(PedidosPage(self._pagina, self._usuario))
        safe_update(self._pagina)

    def _VER_INSUMOS(self, e):
        from features.admin.presentation.pages.gestion.InsumosPage import InsumosPage
        
        self._pagina.controls.clear()
        self._pagina.controls.append(InsumosPage(self._pagina, self._usuario))
        safe_update(self._pagina)

    def _VER_PROVEEDORES(self, e):
        from features.admin.presentation.pages.gestion.ProveedoresPage import ProveedoresPage
        
        self._pagina.controls.clear()
        self._pagina.controls.append(ProveedoresPage(self._pagina, self._usuario))
        safe_update(self._pagina)

    def _VER_CAJA(self, e):
        from features.admin.presentation.pages.gestion.CajaPage import CajaPage
        
        self._pagina.controls.clear()
        self._pagina.controls.append(CajaPage(self._pagina, self._usuario))
        safe_update(self._pagina)

    def _VER_AUDITORIA(self, e):
        from features.admin.presentation.pages.vistas.AuditoriaPage import AuditoriaPage
        
        self._pagina.controls.clear()
        self._pagina.controls.append(AuditoriaPage(self._pagina, self._usuario))
        safe_update(self._pagina)

    def _VER_RESENAS(self, e):
        from features.admin.presentation.pages.vistas.ResenasPage import ResenasPage

        self._pagina.controls.clear()
        self._pagina.controls.append(ResenasPage(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    
    def _VER_FINANZAS(self, e):
        from features.admin.presentation.pages.vistas.FinanzasPage import FinanzasPage

        self._pagina.controls.clear()
        self._pagina.controls.append(FinanzasPage(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    
    def _VER_VALIDAR_VOUCHERS(self, e):
        from features.admin.presentation.pages.vistas.VouchersPage import VouchersPage

        self._pagina.controls.clear()
        vouchers_page = VouchersPage(self._pagina, self._usuario)
        self._pagina.controls.append(vouchers_page)
        safe_update(self._pagina)
        
        if hasattr(vouchers_page, '_cargar_datos_iniciales'):
            vouchers_page._cargar_datos_iniciales()

    def _SALIR(self, e):
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin

        ADMIN_BLOC.REMOVER_LISTENER(self._ON_ESTADO_CAMBIO)
        
        self._pagina.controls.clear()
        self._pagina.controls.append(PaginaLogin(self._pagina))
        safe_update(self._pagina)

    def _MOSTRAR_ERROR(self, MENSAJE: str):
        snackbar = ft.SnackBar(
            content=ft.Text(MENSAJE, color=COLORES.TEXTO_BLANCO),
            bgcolor=COLORES.PELIGRO,
        )
        _overlay = getattr(self._pagina, 'overlay', None)
        if _overlay is not None:
            _overlay.append(snackbar)
        else:
            try:
                self._pagina.controls.append(snackbar)
            except Exception:
                pass
        snackbar.open = True
        safe_update(self._pagina)
    
    def _MOSTRAR_EXITO(self, MENSAJE: str):
        snackbar = ft.SnackBar(
            content=ft.Text(MENSAJE, color=COLORES.TEXTO_BLANCO),
            bgcolor=COLORES.EXITO,
        )
        _overlay = getattr(self._pagina, 'overlay', None)
        if _overlay is not None:
            _overlay.append(snackbar)
        else:
            try:
                self._pagina.controls.append(snackbar)
            except Exception:
                pass
        snackbar.open = True
        safe_update(self._pagina)

