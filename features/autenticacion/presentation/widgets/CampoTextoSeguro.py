import flet as ft
from typing import Optional, Callable

class CampoTextoSeguro(ft.Column):
    
    
    def __init__(
        self,
        ETIQUETA: str,
        ICONO: Optional[str] = None,
        ES_CONTRASENA: bool = False,
        TIPO_TECLADO: ft.KeyboardType = ft.KeyboardType.TEXT,
        VALIDADOR: Optional[Callable[[str], Optional[str]]] = None,
        AL_CAMBIAR: Optional[Callable[[str], None]] = None,
        TEXTO_AYUDA: Optional[str] = None,
        ANCHO: Optional[float] = None
    ):
        super().__init__()
        self._ETIQUETA = ETIQUETA
        self._ICONO = ICONO
        self._ES_CONTRASENA = ES_CONTRASENA
        self._TIPO_TECLADO = TIPO_TECLADO
        self._VALIDADOR = VALIDADOR
        self._AL_CAMBIAR = AL_CAMBIAR
        self._TEXTO_AYUDA = TEXTO_AYUDA
        self._ANCHO = ANCHO
        
        self._CAMPO_TEXTO: Optional[ft.TextField] = None
        self._TEXTO_ERROR: Optional[ft.Text] = None
        
        self._CONSTRUIR()
    
    def _CONSTRUIR(self):
        
        
        self._CAMPO_TEXTO = ft.TextField(
            label=self._ETIQUETA,
            password=self._ES_CONTRASENA,
            can_reveal_password=self._ES_CONTRASENA,
            keyboard_type=self._TIPO_TECLADO,
            on_change=self._MANEJAR_CAMBIO,
            prefix_icon=self._ICONO,
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_600,
            cursor_color=ft.Colors.BLUE_600,
            text_size=16,
            height=60,
            content_padding=ft.padding.symmetric(horizontal=15, vertical=10),
            width=self._ANCHO if self._ANCHO else None,
            hint_text=self._TEXTO_AYUDA,
            hint_style=ft.TextStyle(
                size=14,
                color=ft.Colors.GREY_500
            )
        )
        
        self._TEXTO_ERROR = ft.Text(
            value="",
            color=ft.Colors.RED_400,
            size=12,
            visible=False,
            weight=ft.FontWeight.W_500
        )
        
        self.controls = [
            self._CAMPO_TEXTO,
            self._TEXTO_ERROR
        ]
        self.spacing = 5
        self.width = self._ANCHO if self._ANCHO else None
    
    def _MANEJAR_CAMBIO(self, e):
        
        VALOR = e.control.value
        
        if self._VALIDADOR:
            ERROR = self._VALIDADOR(VALOR)
            
            if ERROR:
                self._MOSTRAR_ERROR(ERROR)
            else:
                self._OCULTAR_ERROR()
        
        if self._AL_CAMBIAR:
            self._AL_CAMBIAR(VALOR)
    
    def _MOSTRAR_ERROR(self, MENSAJE: str):
        
        if self._TEXTO_ERROR:
            self._TEXTO_ERROR.value = MENSAJE
            self._TEXTO_ERROR.visible = True
            self._CAMPO_TEXTO.border_color = ft.Colors.RED_400
            self._CAMPO_TEXTO.focused_border_color = ft.Colors.RED_600
            self.update()
    
    def _OCULTAR_ERROR(self):
        
        if self._TEXTO_ERROR:
            self._TEXTO_ERROR.visible = False
            self._CAMPO_TEXTO.border_color = ft.Colors.BLUE_400
            self._CAMPO_TEXTO.focused_border_color = ft.Colors.BLUE_600
            self.update()
    
    def OBTENER_VALOR(self) -> str:
        
        return self._CAMPO_TEXTO.value if self._CAMPO_TEXTO else ""
    
    def ESTABLECER_VALOR(self, VALOR: str):
        
        if self._CAMPO_TEXTO:
            self._CAMPO_TEXTO.value = VALOR
            self.update()
    
    def LIMPIAR(self):
        
        if self._CAMPO_TEXTO:
            self._CAMPO_TEXTO.value = ""
            self._OCULTAR_ERROR()
            self.update()
    
    def VALIDAR(self) -> bool:
        
        if not self._VALIDADOR:
            return True
        
        VALOR = self.OBTENER_VALOR()
        ERROR = self._VALIDADOR(VALOR)
        
        if ERROR:
            self._MOSTRAR_ERROR(ERROR)
            return False
        
        self._OCULTAR_ERROR()
        return True
    
    def DESHABILITAR(self):
        
        if self._CAMPO_TEXTO:
            self._CAMPO_TEXTO.disabled = True
            self.update()
    
    def HABILITAR(self):
        
        if self._CAMPO_TEXTO:
            self._CAMPO_TEXTO.disabled = False
            self.update()
