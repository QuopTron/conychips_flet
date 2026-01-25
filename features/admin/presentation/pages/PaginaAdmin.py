"""
Página Admin Refactorizada
Presentation Layer - Clean Architecture + BLoC Pattern
Separación de responsabilidades y código limpio
"""

import flet as ft

from core.Constantes import COLORES, TAMANOS, ICONOS, ROLES, ERRORES_AUTENTICACION
from features.autenticacion.domain.entities.Usuario import Usuario
from core.decoradores.DecoradorVistas import REQUIERE_ROL

# BLoC Pattern
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

# Widgets reutilizables
from ..widgets import (
    CardEstadistica,
    GraficoRoles,
    GraficoSucursales,
    GraficoSemanal,
    GraficoInventario,
)

# Casos de uso
from ...domain.usecases import ObtenerRolesDisponibles
from ...data.RepositorioAdminImpl import REPOSITORIO_ADMIN_IMPL


@REQUIERE_ROL(ROLES.SUPERADMIN, ROLES.ADMIN)
class PaginaAdmin(ft.Column):
    """
    Página principal del dashboard de administración
    Refactorizada con BLoC Pattern y Clean Architecture
    
    Responsabilidades:
    - Renderizar UI basada en el estado del BLoC
    - Disparar eventos al BLoC
    - Delegar navegación a otras vistas
    """

    def __init__(self, PAGINA: ft.Page, USUARIO: Usuario):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        
        # Widgets reutilizables - se actualizarán cuando cambie el estado
        self._card_usuarios: CardEstadistica = None
        self._card_pedidos: CardEstadistica = None
        self._card_ganancias: CardEstadistica = None
        self._card_productos: CardEstadistica = None
        
        self._grafico_roles: GraficoRoles = None
        self._grafico_sucursales: GraficoSucursales = None
        self._grafico_semanal: GraficoSemanal = None
        self._grafico_inventario: GraficoInventario = None
        
        # Construir UI
        self._CONSTRUIR()
        
        # Suscribirse al BLoC
        ADMIN_BLOC.AGREGAR_LISTENER(self._ON_ESTADO_CAMBIO)
        
        # Cargar datos iniciales
        ADMIN_BLOC.AGREGAR_EVENTO(CargarDashboard())

    def _CONSTRUIR(self):
        """Construye la interfaz de usuario"""
        # Header con navegación
        header = self._CONSTRUIR_HEADER()
        
        # Cards de estadísticas generales
        self._card_usuarios = CardEstadistica(
            icono=ICONOS.USUARIOS,
            valor="0",
            etiqueta="Usuarios",
            color_icono=COLORES.PRIMARIO
        )
        
        self._card_pedidos = CardEstadistica(
            icono=ICONOS.PEDIDOS,
            valor="0",
            etiqueta="Pedidos Hoy",
            color_icono=COLORES.EXITO
        )
        
        self._card_ganancias = CardEstadistica(
            icono=ICONOS.CAJA,
            valor="0 Bs",
            etiqueta="Ganancias Hoy",
            color_icono=COLORES.ADVERTENCIA
        )
        
        self._card_productos = CardEstadistica(
            icono=ICONOS.PRODUCTOS,
            valor="0",
            etiqueta="Productos",
            color_icono=COLORES.INFO
        )
        
        stats_row = ft.Row(
            [
                self._card_usuarios,
                self._card_pedidos,
                self._card_ganancias,
                self._card_productos,
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            wrap=True,
        )
        
        # Gráficos
        self._grafico_roles = GraficoRoles()
        self._grafico_sucursales = GraficoSucursales()
        self._grafico_semanal = GraficoSemanal()
        self._grafico_inventario = GraficoInventario()
        
        graficos_row = ft.Row(
            [
                self._CREAR_CONTENEDOR_GRAFICO(
                    "Usuarios por Rol",
                    self._grafico_roles
                ),
                self._CREAR_CONTENEDOR_GRAFICO(
                    "Pedidos por Sucursal",
                    self._grafico_sucursales
                ),
            ],
            spacing=TAMANOS.ESPACIADO_MD,
        )
        
        graficos_row2 = ft.Row(
            [
                self._CREAR_CONTENEDOR_GRAFICO(
                    "Pedidos Última Semana",
                    self._grafico_semanal
                ),
                self._CREAR_CONTENEDOR_GRAFICO(
                    "Estado Inventario",
                    self._grafico_inventario
                ),
            ],
            spacing=TAMANOS.ESPACIADO_MD,
        )
        
        # Botones de gestión
        botones_gestion = self._CONSTRUIR_BOTONES_GESTION()
        
        # Contenido completo
        contenido = ft.Column(
            [
                header,
                ft.Divider(height=1, color=COLORES.BORDE),
                stats_row,
                ft.Divider(height=1, color=COLORES.BORDE),
                graficos_row,
                graficos_row2,
                ft.Divider(height=1, color=COLORES.BORDE),
                ft.Text(
                    "Gestión del Sistema",
                    size=TAMANOS.TEXTO_XL,
                    weight=ft.FontWeight.BOLD,
                    color=COLORES.TEXTO
                ),
                botones_gestion,
            ],
            spacing=TAMANOS.ESPACIADO_LG,
            scroll=ft.ScrollMode.AUTO,
        )

        self.controls = [
            ft.Container(
                content=contenido,
                padding=TAMANOS.PADDING_XL,
                expand=True,
                bgcolor=COLORES.FONDO,
            )
        ]
        self.expand = True
    
    def _CONSTRUIR_HEADER(self) -> ft.Row:
        """Construye el header con título y botones de navegación"""
        return ft.Row(
            controls=[
                ft.Icon(
                    ICONOS.ADMIN,
                    size=TAMANOS.ICONO_LG,
                    color=COLORES.PRIMARIO
                ),
                ft.Text(
                    "Dashboard Admin",
                    size=TAMANOS.TEXTO_3XL,
                    weight=ft.FontWeight.BOLD,
                    color=COLORES.TEXTO
                ),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Menú",
                    icon=ICONOS.DASHBOARD,
                    on_click=self._IR_MENU,
                    bgcolor=COLORES.PRIMARIO,
                    color=COLORES.TEXTO_BLANCO
                ),
                ft.ElevatedButton(
                    "Salir",
                    icon=ICONOS.CERRAR_SESION,
                    on_click=self._SALIR,
                    bgcolor=COLORES.PELIGRO,
                    color=COLORES.TEXTO_BLANCO
                ),
            ],
            spacing=TAMANOS.ESPACIADO_MD,
        )
    
    def _CREAR_CONTENEDOR_GRAFICO(self, titulo: str, grafico: ft.Control) -> ft.Container:
        """Crea un contenedor estilizado para un gráfico"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        titulo,
                        size=TAMANOS.TEXTO_XL,
                        weight=ft.FontWeight.BOLD,
                        color=COLORES.TEXTO
                    ),
                    grafico,
                ],
                spacing=TAMANOS.ESPACIADO_MD,
            ),
            padding=TAMANOS.PADDING_LG,
            bgcolor=COLORES.FONDO_BLANCO,
            border_radius=TAMANOS.RADIO_MD,
            border=ft.border.all(1, COLORES.BORDE),
            expand=True,
        )
    
    def _CONSTRUIR_BOTONES_GESTION(self) -> ft.Row:
        """Construye la fila de botones de gestión (DRY)"""
        botones = [
            self._CREAR_BOTON_GESTION("Gestionar Roles", ICONOS.ROLES, self._ABRIR_GESTION_ROLES, COLORES.SECUNDARIO),
            self._CREAR_BOTON_GESTION("Gestionar Usuarios", ICONOS.USUARIOS, self._VER_USUARIOS, COLORES.PRIMARIO),
            self._CREAR_BOTON_GESTION("Usuarios Avanzado", ICONOS.USUARIOS, self._VER_USUARIOS_AVANZADO, COLORES.PRIMARIO_CLARO),
            self._CREAR_BOTON_GESTION("Gestionar Productos", ICONOS.PRODUCTOS, self._VER_PRODUCTOS, COLORES.EXITO),
            self._CREAR_BOTON_GESTION("Gestionar Sucursales", ft.Icons.STORE, self._VER_SUCURSALES, COLORES.ADVERTENCIA),
            self._CREAR_BOTON_GESTION("Extras", ft.Icons.ADD_CIRCLE, self._VER_EXTRAS, COLORES.INFO_OSCURO),
            self._CREAR_BOTON_GESTION("Ofertas", ft.Icons.LOCAL_OFFER, self._VER_OFERTAS, COLORES.ADVERTENCIA),
            self._CREAR_BOTON_GESTION("Horarios", ft.Icons.SCHEDULE, self._VER_HORARIOS, COLORES.INFO),
            self._CREAR_BOTON_GESTION("Gestión Pedidos", ICONOS.PEDIDOS, self._VER_PEDIDOS_ADMIN, COLORES.EXITO),
            self._CREAR_BOTON_GESTION("Insumos", ICONOS.INSUMOS, self._VER_INSUMOS, COLORES.INFO),
            self._CREAR_BOTON_GESTION("Proveedores", ICONOS.PROVEEDORES, self._VER_PROVEEDORES, COLORES.PRIMARIO_OSCURO),
            self._CREAR_BOTON_GESTION("Caja", ICONOS.CAJA, self._VER_CAJA, COLORES.EXITO_OSCURO),
            self._CREAR_BOTON_GESTION("Auditoría", ICONOS.AUDITORIA, self._VER_AUDITORIA, COLORES.GRIS_OSCURO),
            self._CREAR_BOTON_GESTION("Reseñas", ICONOS.RESENAS, self._VER_RESENAS, COLORES.ADVERTENCIA_OSCURO),
            self._CREAR_BOTON_GESTION("Finanzas y Control", ICONOS.CAJA, self._VER_FINANZAS, COLORES.EXITO),
            self._CREAR_BOTON_GESTION("Validar Vouchers", ICONOS.VOUCHER, self._VER_VALIDAR_VOUCHERS, COLORES.ADVERTENCIA),
        ]
        
        return ft.Row(
            botones,
            wrap=True,
            spacing=TAMANOS.ESPACIADO_MD,
        )
    
    def _CREAR_BOTON_GESTION(self, texto: str, icono: str, handler, bgcolor: str) -> ft.ElevatedButton:
        """Factory method para crear botones de gestión (DRY)"""
        return ft.ElevatedButton(
            texto,
            icon=icono,
            on_click=handler,
            bgcolor=bgcolor,
            color=COLORES.TEXTO_BLANCO,
        )
    
    # =========================================================================
    # Gestión de Estado con BLoC Pattern
    # =========================================================================
    
    def _ON_ESTADO_CAMBIO(self, estado: AdminEstado):
        """
        Callback cuando el BLoC cambia de estado
        Actualiza la UI reactivamente
        """
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
        """Muestra indicador de carga"""
        # Aquí podrías agregar un spinner si lo deseas
        pass
    
    def _ACTUALIZAR_UI_CON_DATOS(self, dashboard):
        """Actualiza la UI con los datos del dashboard"""
        # Actualizar cards de estadísticas generales
        stats = dashboard.estadisticas_generales
        self._card_usuarios.ACTUALIZAR_VALOR(str(stats.total_usuarios))
        self._card_pedidos.ACTUALIZAR_VALOR(str(stats.total_pedidos_hoy))
        self._card_ganancias.ACTUALIZAR_VALOR(f"{stats.ganancias_hoy} Bs")
        self._card_productos.ACTUALIZAR_VALOR(str(stats.total_productos))
        
        # Actualizar gráficos
        self._grafico_roles.ACTUALIZAR_DATOS(dashboard.estadisticas_roles)
        self._grafico_sucursales.ACTUALIZAR_DATOS(dashboard.estadisticas_sucursales)
        self._grafico_semanal.ACTUALIZAR_DATOS(dashboard.estadisticas_semanales)
        self._grafico_inventario.ACTUALIZAR_DATOS(dashboard.estadisticas_inventario)
        
        # Forzar actualización
        if hasattr(self, 'update'):
            self.update()
    
    # =========================================================================
    # Gestión de Roles
    # =========================================================================
        try:
            if not self._USUARIO.TIENE_ROL(ROLES.SUPERADMIN):
                self._MOSTRAR_ERROR(ERRORES_AUTENTICACION.PERMISOS_INSUFICIENTES)
                return
            
            from features.admin.presentation.pages.PaginaGestionRoles import PaginaGestionRoles
            
            def volver_dashboard():
                self._PAGINA.controls.clear()
                self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
                self._PAGINA.update()
            
            pagina_roles = PaginaGestionRoles(self._PAGINA, self._USUARIO, volver_dashboard)
            self._PAGINA.controls.clear()
            self._PAGINA.add(pagina_roles)
            self._PAGINA.update()
            
        except Exception as error:
            print(f"Error abriendo gestión de roles: {error}")
            self._MOSTRAR_ERROR(f"Error: {str(error)}")    
    # =========================================================================
    # Gestión de Roles
    # =========================================================================
    
    def _ABRIR_GESTION_ROLES(self, e):
        """Navega a la vista de gestión de roles"""
        try:
            if not self._USUARIO.TIENE_ROL(ROLES.SUPERADMIN):
                self._MOSTRAR_ERROR(ERRORES_AUTENTICACION.PERMISOS_INSUFICIENTES)
                return
            
            from features.admin.presentation.pages.PaginaGestionRoles import PaginaGestionRoles
            
            def volver_dashboard():
                self._PAGINA.controls.clear()
                self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
                self._PAGINA.update()
            
            pagina_roles = PaginaGestionRoles(self._PAGINA, self._USUARIO, volver_dashboard)
            self._PAGINA.controls.clear()
            self._PAGINA.add(pagina_roles)
            self._PAGINA.update()
            
        except Exception as error:
            print(f"Error abriendo gestión de roles: {error}")
            self._MOSTRAR_ERROR(f"Error: {str(error)}")

    def _ABRIR_CAMBIO_ROL(self, USUARIO):
        """Abre diálogo para cambiar rol de usuario (usando BLoC)"""
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

            # Disparar evento al BLoC
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
                ft.ElevatedButton(
                    "Guardar",
                    on_click=GUARDAR,
                    bgcolor=COLORES.PRIMARIO,
                    color=COLORES.TEXTO_BLANCO
                ),
            ],
        )

        self._PAGINA.dialog = dlg
        dlg.open = True
        self._PAGINA.update()
    
    # =========================================================================
    # Navegación a Otras Vistas (Delegación)
    # =========================================================================    
    # =========================================================================
    # Navegación a Otras Vistas (Delegación)
    # =========================================================================


    def _VER_USUARIOS(self, e):
        """Abre vista de gestión de usuarios"""
        from features.admin.presentation.pages.VistaUsuarios import VistaUsuarios
        
        def volver_dashboard():
            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
            self._PAGINA.update()
        
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(
            VistaUsuarios(self._PAGINA, self._USUARIO, volver_dashboard)
        )
        self._PAGINA.update()

    def _ABRIR_CAMBIO_ROL(self, USUARIO):
        """Abre diálogo para cambiar rol de usuario (usando BLoC)"""
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

            # Disparar evento al BLoC
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
                ft.ElevatedButton(
                    "Guardar",
                    on_click=GUARDAR,
                    bgcolor=COLORES.PRIMARIO,
                    color=COLORES.TEXTO_BLANCO
                ),
            ],
        )

        self._PAGINA.dialog = dlg
        dlg.open = True
        self._PAGINA.update()


    def _OBTENER_ROLES(self):
        """Obsoleto - ahora se usa el caso de uso"""
        usecase = ObtenerRolesDisponibles(REPOSITORIO_ADMIN_IMPL)
        return usecase.EJECUTAR()


    def _ACTUALIZAR_ROL_USUARIO(self, USUARIO_ID: int, NOMBRE_ROL: str):
        """Obsoleto - ahora se usa el BLoC"""
        ADMIN_BLOC.AGREGAR_EVENTO(
            ActualizarRol(usuario_id=USUARIO_ID, nombre_rol=NOMBRE_ROL)
        )


    def _CERRAR_DLG(self, e):
        """Cierra el diálogo modal"""
        if hasattr(self._PAGINA, "dialog") and self._PAGINA.dialog:
            self._PAGINA.dialog.open = False
            self._PAGINA.update()
    
    # =========================================================================
    # Métodos de Navegación (Delegación - mantienen compatibilidad)
    # =========================================================================
    # =========================================================================
    # Métodos de Navegación (Delegación - mantienen compatibilidad)
    # =========================================================================


    def _VER_PRODUCTOS(self, e):
        """Abre vista de gestión de productos"""
        from features.admin.presentation.pages.VistaProductos import VistaProductos
        
        def volver_dashboard():
            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
            self._PAGINA.update()
        
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(VistaProductos(self._PAGINA, self._USUARIO, volver_dashboard))
        self._PAGINA.update()


    def _VER_SUCURSALES(self, e):
        """Abre vista de gestión de sucursales"""
        from features.admin.presentation.pages.VistaSucursales import VistaSucursales
        
        def volver_dashboard():
            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
            self._PAGINA.update()
        
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(VistaSucursales(self._PAGINA, self._USUARIO, volver_dashboard))
        self._PAGINA.update()


    def _VER_USUARIOS_AVANZADO(self, e):
        """Abre vista avanzada de gestión de usuarios"""
        from features.admin.presentation.pages.VistaUsuarios import VistaUsuarios
        
        def volver_dashboard():
            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
            self._PAGINA.update()
        
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(VistaUsuarios(self._PAGINA, self._USUARIO, volver_dashboard))
        self._PAGINA.update()


    def _VER_EXTRAS(self, e):
        """Abre vista de gestión de extras"""
        from features.admin.presentation.pages.VistaExtras import VistaExtras
        
        def volver_dashboard():
            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
            self._PAGINA.update()
        
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(VistaExtras(self._PAGINA, self._USUARIO, volver_dashboard))
        self._PAGINA.update()


    def _VER_OFERTAS(self, e):
        """Abre vista de gestión de ofertas"""
        from features.admin.presentation.pages.VistaOfertas import VistaOfertas
        
        def volver_dashboard():
            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
            self._PAGINA.update()
        
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(VistaOfertas(self._PAGINA, self._USUARIO, volver_dashboard))
        self._PAGINA.update()


    def _VER_HORARIOS(self, e):
        """Abre vista de gestión de horarios"""
        from features.admin.presentation.pages.VistaHorarios import VistaHorarios
        
        def volver_dashboard():
            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
            self._PAGINA.update()
        
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(VistaHorarios(self._PAGINA, self._USUARIO, volver_dashboard))
        self._PAGINA.update()


    def _VER_PEDIDOS_ADMIN(self, e):
        from features.admin.presentation.pages.PaginaPedidos import PaginaPedidos

        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaPedidos(self._PAGINA, self._USUARIO))
        self._PAGINA.update()


    def _VER_INSUMOS(self, e):
        """Abre vista de gestión de insumos"""
        from features.admin.presentation.pages.VistaInsumos import VistaInsumos
        
        def volver_dashboard():
            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
            self._PAGINA.update()
        
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(VistaInsumos(self._PAGINA, self._USUARIO, volver_dashboard))
        self._PAGINA.update()


    def _VER_PROVEEDORES(self, e):
        """Abre vista de gestión de proveedores"""
        from features.admin.presentation.pages.VistaProveedores import VistaProveedores
        
        def volver_dashboard():
            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
            self._PAGINA.update()
        
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(VistaProveedores(self._PAGINA, self._USUARIO, volver_dashboard))
        self._PAGINA.update()


    def _VER_CAJA(self, e):
        """Abre vista de gestión de caja"""
        from features.admin.presentation.pages.VistaCaja import VistaCaja
        
        def volver_dashboard():
            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
            self._PAGINA.update()
        
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(VistaCaja(self._PAGINA, self._USUARIO, volver_dashboard))
        self._PAGINA.update()


    def _VER_AUDITORIA(self, e):
        """Abre vista de auditoría"""
        from features.admin.presentation.pages.VistaAuditoria import VistaAuditoria
        
        def volver_dashboard():
            self._PAGINA.controls.clear()
            self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
            self._PAGINA.update()
        
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(VistaAuditoria(self._PAGINA, self._USUARIO, volver_dashboard))
        self._PAGINA.update()


    def _VER_RESENAS(self, e):
        """Abre vista de reseñas"""
        from features.admin.presentation.pages.PaginaResenas import PaginaResenas

        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaResenas(self._PAGINA, self._USUARIO))
        self._PAGINA.update()
    
    
    def _VER_FINANZAS(self, e):
        """Abre vista de finanzas"""
        from features.admin.presentation.pages.PaginaFinanzas import PaginaFinanzas

        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaFinanzas(self._PAGINA, self._USUARIO).CONSTRUIR())
        self._PAGINA.update()
    
    
    def _VER_VALIDAR_VOUCHERS(self, e):
        """Abre vista de validación de vouchers"""
        from features.admin.presentation.pages.PaginaValidarVouchers import PaginaValidarVouchers

        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaValidarVouchers(self._PAGINA, self._USUARIO).CONSTRUIR())
        self._PAGINA.update()


    def _IR_MENU(self, e):
        """Recarga el dashboard"""
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
        self._PAGINA.update()


    def _SALIR(self, e):
        """Cierra sesión y vuelve al login"""
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin

        # Limpiar listener del BLoC
        ADMIN_BLOC.REMOVER_LISTENER(self._ON_ESTADO_CAMBIO)
        
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaLogin(self._PAGINA))
        self._PAGINA.update()
    
    # =========================================================================
    # Utilidades
    # =========================================================================

    def _MOSTRAR_ERROR(self, MENSAJE: str):
        """Muestra mensaje de error"""
        snackbar = ft.SnackBar(
            content=ft.Text(MENSAJE, color=COLORES.TEXTO_BLANCO),
            bgcolor=COLORES.PELIGRO,
        )
        self._PAGINA.overlay.append(snackbar)
        snackbar.open = True
        self._PAGINA.update()
    
    def _MOSTRAR_EXITO(self, MENSAJE: str):
        """Muestra mensaje de éxito"""
        snackbar = ft.SnackBar(
            content=ft.Text(MENSAJE, color=COLORES.TEXTO_BLANCO),
            bgcolor=COLORES.EXITO,
        )
        self._PAGINA.overlay.append(snackbar)
        snackbar.open = True
        self._PAGINA.update()

