import flet as ft
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_USUARIO, MODELO_ROL, MODELO_PEDIDO, MODELO_CAJA, MODELO_SUCURSAL
from datetime import datetime


class PaginaAdmin(ft.Column):
    def __init__(self, PAGINA: ft.Page, USUARIO_ID: int):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO_ID = USUARIO_ID
        self._LISTA_CONTROLES = ft.Column()
        self._CONSTRUIR()

    def _CONSTRUIR(self):
        HEADER = ft.Text("Dashboard Admin", size=24, weight=ft.FontWeight.BOLD)

        # Stats
        self._STATS_USUARIOS = ft.Text("Usuarios: Cargando...")
        self._STATS_PEDIDOS = ft.Text("Pedidos hoy: Cargando...")
        self._STATS_GANANCIAS = ft.Text("Ganancias hoy: Cargando...")

        # Gráficos simples (texto por ahora)
        self._GRAFICO_ROLES = ft.Column()
        self._GRAFICO_SUCURSALES = ft.Column()

        # Acciones
        self._BOTON_VER_USUARIOS = ft.Button("Gestionar Usuarios", on_click=self._VER_USUARIOS)
        self._BOTON_VER_PRODUCTOS = ft.Button("Gestionar Productos", on_click=self._VER_PRODUCTOS)
        self._BOTON_VER_SUCURSALES = ft.Button("Gestionar Sucursales", on_click=self._VER_SUCURSALES)

        self._LISTA_CONTROLES = ft.Column(spacing=10)

        self.controls = [
            ft.Container(content=ft.Column([
                HEADER,
                ft.Row([self._STATS_USUARIOS, self._STATS_PEDIDOS, self._STATS_GANANCIAS], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                ft.Text("Estadísticas por Rol", size=18, weight=ft.FontWeight.BOLD),
                self._GRAFICO_ROLES,
                ft.Text("Estadísticas por Sucursal", size=18, weight=ft.FontWeight.BOLD),
                self._GRAFICO_SUCURSALES,
                ft.Row([self._BOTON_VER_USUARIOS, self._BOTON_VER_PRODUCTOS, self._BOTON_VER_SUCURSALES]),
                self._LISTA_CONTROLES
            ]), padding=20, expand=True)
        ]
        self.expand = True
        self._CARGAR_STATS()

    def _CARGAR_STATS(self):
        import asyncio
        asyncio.create_task(self._OBTENER_STATS())

    async def _OBTENER_STATS(self):
        sesion = OBTENER_SESION()
        hoy = datetime.utcnow().date()

        # Usuarios por rol
        roles = sesion.query(MODELO_ROL).all()
        stats_roles = {}
        for r in roles:
            count = len(r.USUARIOS)
            stats_roles[r.NOMBRE] = count

        # Pedidos hoy
        pedidos_hoy = sesion.query(MODELO_PEDIDO).filter(MODELO_PEDIDO.FECHA_CREACION >= hoy).count()

        # Ganancias hoy
        cajas_hoy = sesion.query(MODELO_CAJA).filter(MODELO_CAJA.FECHA_APERTURA >= hoy).all()
        ganancias = sum(c.GANANCIAS or 0 for c in cajas_hoy)

        self._STATS_USUARIOS.value = f"Usuarios totales: {sesion.query(MODELO_USUARIO).count()}"
        self._STATS_PEDIDOS.value = f"Pedidos hoy: {pedidos_hoy}"
        self._STATS_GANANCIAS.value = f"Ganancias hoy: {ganancias} Bs"

        # Gráfico roles
        self._GRAFICO_ROLES.controls.clear()
        for rol, count in stats_roles.items():
            self._GRAFICO_ROLES.controls.append(ft.Text(f"{rol}: {count} usuarios"))

        # Gráfico sucursales
        sucursales = sesion.query(MODELO_SUCURSAL).all()
        self._GRAFICO_SUCURSALES.controls.clear()
        for s in sucursales:
            pedidos_suc = sesion.query(MODELO_PEDIDO).filter_by(SUCURSAL_ID=s.ID).count()
            self._GRAFICO_SUCURSALES.controls.append(ft.Text(f"{s.NOMBRE}: {pedidos_suc} pedidos"))

        if getattr(self, 'page', None):
            self.update()

    def _VER_USUARIOS(self, e):
        # Mostrar diálogo con usuarios y estado en línea
        from core.websocket.ManejadorConexion import ManejadorConexion
        manejador = ManejadorConexion()

        sesion = OBTENER_SESION()
        usuarios = sesion.query(MODELO_USUARIO).all()

        filas = []
        for u in usuarios:
            online = True if manejador.OBTENER_CONEXION(u.ID) else False
            color = ft.Colors.GREEN_600 if online else ft.Colors.RED_600
            filas.append(ft.Row([ft.Text(u.NOMBRE_USUARIO), ft.Text(u.EMAIL, size=12, color=ft.Colors.GREY_600), ft.Icon(ft.Icons.FIBER_MANUAL_RECORD, color=color)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

        dlg = ft.AlertDialog(
            title=ft.Text("Usuarios en el sistema"),
            content=ft.Column(filas, spacing=8),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: self._CERRAR_DLG(e))]
        )
        self._PAGINA.dialog = dlg
        dlg.open = True
        self._PAGINA.update()

    def _CERRAR_DLG(self, e):
        if hasattr(self._PAGINA, 'dialog') and self._PAGINA.dialog:
            self._PAGINA.dialog.open = False
            self._PAGINA.update()

    def _VER_PRODUCTOS(self, e):
        # Abrir vista de gestión de productos
        pass

    def _VER_SUCURSALES(self, e):
        # Abrir vista de gestión de sucursales
        pass