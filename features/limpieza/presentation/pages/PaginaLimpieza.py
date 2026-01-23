import flet as ft
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_ASISTENCIA, MODELO_REPORTE_LIMPIEZA, MODELO_SUCURSAL
from datetime import datetime, timedelta


class PaginaLimpieza(ft.Column):
    def __init__(self, PAGINA: ft.Page, USUARIO_ID: int):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO_ID = USUARIO_ID
        self._LISTA_CONTROLES = ft.Column()
        self._CONSTRUIR()

    def _CONSTRUIR(self):
        HEADER = ft.Text("Dashboard Limpieza", size=24, weight=ft.FontWeight.BOLD)

        # Asistencia del mes
        self._CALENDARIO_ASISTENCIA = ft.Column()

        # Formulario para subir foto
        self._DROPDOWN_SUCURSAL = ft.Dropdown(label="Seleccionar Sucursal")
        self._CAMPO_NOTAS = ft.TextField(label="Notas", multiline=True)
        self._BOTON_SUBIR_FOTO = ft.Button("Subir Foto del Local", on_click=self._SUBIR_FOTO)

        self._LISTA_CONTROLES = ft.Column(spacing=10)

        self.controls = [
            ft.Container(content=ft.Column([
                HEADER,
                ft.Text("Asistencia del mes", size=18, weight=ft.FontWeight.BOLD),
                self._CALENDARIO_ASISTENCIA,
                ft.Text("Reportes diarios", size=18, weight=ft.FontWeight.BOLD),
                self._DROPDOWN_SUCURSAL,
                self._CAMPO_NOTAS,
                self._BOTON_SUBIR_FOTO,
                self._LISTA_CONTROLES
            ]), padding=20, expand=True)
        ]
        self.expand = True
        import asyncio

        async def _delayed_load():
            await asyncio.sleep(0)
            try:
                self._CARGAR_SUCURSALES()
                self._CARGAR_ASISTENCIA()
            except Exception:
                pass

        asyncio.create_task(_delayed_load())

    def _CARGAR_SUCURSALES(self):
        sesion = OBTENER_SESION()
        sucursales = sesion.query(MODELO_SUCURSAL).filter_by(ACTIVA=True).all()
        opciones = [ft.dropdown.Option(key=str(s.ID), text=s.NOMBRE) for s in sucursales]
        self._DROPDOWN_SUCURSAL.options = opciones
        if opciones:
            self._DROPDOWN_SUCURSAL.value = opciones[0].key
        if getattr(self, 'page', None):
            self.update()

    def _CARGAR_ASISTENCIA(self):
        sesion = OBTENER_SESION()
        hoy = datetime.utcnow()
        inicio_mes = hoy.replace(day=1)
        asistencias = sesion.query(MODELO_ASISTENCIA).filter(
            MODELO_ASISTENCIA.USUARIO_ID == self._USUARIO_ID,
            MODELO_ASISTENCIA.FECHA >= inicio_mes
        ).all()

        # Crear calendario simple
        dias_mes = {}
        for i in range(1, 32):
            try:
                fecha = inicio_mes.replace(day=i)
                dias_mes[fecha.day] = False
            except ValueError:
                break

        for a in asistencias:
            dias_mes[a.FECHA.day] = a.ASISTIO

        filas = []
        semana = []
        for dia in range(1, len(dias_mes) + 1):
            asistio = dias_mes.get(dia, False)
            color = ft.Colors.GREEN_600 if asistio else ft.Colors.RED_600
            semana.append(ft.Container(
                content=ft.Text(str(dia), color=color, weight=ft.FontWeight.BOLD),
                width=40, height=40, alignment=ft.alignment(1, 1)
            ))
            if len(semana) == 7:
                filas.append(ft.Row(semana, alignment=ft.MainAxisAlignment.CENTER))
                semana = []
        if semana:
            filas.append(ft.Row(semana, alignment=ft.MainAxisAlignment.CENTER))

        self._CALENDARIO_ASISTENCIA.controls = filas
        if getattr(self, 'page', None):
            self.update()

    def _SUBIR_FOTO(self, e):
        import asyncio
        asyncio.create_task(self._MANEJAR_SUBIDA_FOTO())

    async def _MANEJAR_SUBIDA_FOTO(self):
        if not self._DROPDOWN_SUCURSAL.value:
            self._PAGINA.snack_bar = ft.SnackBar(ft.Text("Selecciona una sucursal"))
            self._PAGINA.snack_bar.open = True
            self._PAGINA.update()
            return

        # En producción, usar file picker para seleccionar imagen
        # Por ahora, simular subida
        ruta_foto = f"uploads/limpieza_{self._USUARIO_ID}_{int(datetime.utcnow().timestamp())}.jpg"

        sesion = OBTENER_SESION()
        reporte = MODELO_REPORTE_LIMPIEZA(
            USUARIO_ID=self._USUARIO_ID,
            SUCURSAL_ID=int(self._DROPDOWN_SUCURSAL.value),
            FOTO_LOCAL=ruta_foto,
            NOTAS=self._CAMPO_NOTAS.value
        )
        sesion.add(reporte)
        sesion.commit()

        # Notificar a admin
        from core.websocket.ManejadorConexion import ManejadorConexion
        manejador = ManejadorConexion()
        try:
            await manejador.BROADCAST({
                'tipo': 'reporte_limpieza',
                'usuario_id': self._USUARIO_ID,
                'sucursal_id': int(self._DROPDOWN_SUCURSAL.value),
                'foto': ruta_foto,
                'notas': self._CAMPO_NOTAS.value
            })
        except Exception:
            pass

        self._CAMPO_NOTAS.value = ""
        self._PAGINA.snack_bar = ft.SnackBar(ft.Text("Reporte enviado correctamente"))
        self._PAGINA.snack_bar.open = True
        self._PAGINA.update()
        self._CARGAR_REPORTES()

    def _CARGAR_REPORTES(self):
        sesion = OBTENER_SESION()
        reportes = sesion.query(MODELO_REPORTE_LIMPIEZA).filter_by(USUARIO_ID=self._USUARIO_ID).order_by(MODELO_REPORTE_LIMPIEZA.FECHA.desc()).limit(10).all()

        self._LISTA_CONTROLES.controls.clear()
        for r in reportes:
            sucursal = sesion.query(MODELO_SUCURSAL).filter_by(ID=r.SUCURSAL_ID).first()
            nombre_suc = sucursal.NOMBRE if sucursal else "Sucursal desconocida"
            fila = ft.Row([
                ft.Column([
                    ft.Text(f"Reporte {r.FECHA.strftime('%Y-%m-%d')}", weight=ft.FontWeight.BOLD),
                    ft.Text(f"Sucursal: {nombre_suc}"),
                    ft.Text(f"Notas: {r.NOTAS or 'Sin notas'}")
                ]),
                ft.Text("Foto subida" if r.FOTO_LOCAL else "Sin foto")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            self._LISTA_CONTROLES.controls.append(ft.Container(content=fila, padding=10, border=ft.border.all(1, ft.Colors.GREY_200), border_radius=8))
        if getattr(self, 'page', None):
            self.update()
