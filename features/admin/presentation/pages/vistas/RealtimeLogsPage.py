import flet as ft
from core.realtime import recent
from core.constantes import COLORES, TAMANOS


class RealtimeLogsPage:
    def __init__(self, PAGINA: ft.Page):
        self.PAGINA = PAGINA
        self.LIST = ft.ListView(spacing=6, expand=True)
        self._REFRESH()
        try:
            from core.realtime import dispatcher
            dispatcher.register('*', self._on_event)
        except Exception:
            pass

    def _on_event(self, payload: dict):
        try:
            # prepend to list
            self.LIST.controls.insert(0, ft.Container(content=ft.Column([
                ft.Text(payload.get('type', 'event'), weight=ft.FontWeight.BOLD),
                ft.Text(str(payload), size=12, color=COLORES.TEXTO_SECUNDARIO)
            ]), padding=8, border=ft.Border.all(1, COLORES.BORDE), border_radius=6))
            # keep manageable
            if len(self.LIST.controls) > 200:
                self.LIST.controls.pop()
            if self.PAGINA:
                self.PAGINA.update()
        except Exception:
            pass

    def _REFRESH(self):
        self.LIST.controls.clear()
        for ev in recent(100):
            self.LIST.controls.append(ft.Container(content=ft.Column([
                ft.Text(ev.get('type', 'event'), weight=ft.FontWeight.BOLD),
                ft.Text(str(ev), size=12, color=COLORES.TEXTO_SECUNDARIO)
            ]), padding=8, border=ft.Border.all(1, COLORES.BORDE), border_radius=6))
        if self.PAGINA:
            self.PAGINA.update()

    def CONSTRUIR(self) -> ft.Control:
        return ft.Column([
            ft.Text("Realtime Events", size=TAMANOS.TITULO, weight=ft.FontWeight.BOLD),
            ft.Row([ft.Button("Refresh", on_click=lambda e: self._REFRESH()), ft.Container(expand=True)]),
            ft.Container(content=self.LIST, padding=10, expand=True)
        ], expand=True)
