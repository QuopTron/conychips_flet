"""
Fondo animado con emojis de comida cayendo para el login.
"""
import flet as ft
import random
import asyncio


class EmojiCayendo(ft.Container):
    """Emoji que cae desde arriba con animación."""
    
    EMOJIS_COMIDA = ["🍔", "🍟", "🌮", "🍕", "🥤", "🌭", "🍿", "🥗", "🧃", "🍦"]
    
    def __init__(self, ancho_pantalla, alto_pantalla):
        super().__init__()
        
        # Emoji random
        self.content = ft.Text(
            value=random.choice(self.EMOJIS_COMIDA),
            size=random.randint(20, 60),
            opacity=random.uniform(0.1, 0.3),  # Muy difuminado
        )
        
        # Posición inicial (arriba, posición X random)
        self.left = random.randint(0, int(ancho_pantalla))
        self.top = -100  # Empieza arriba de la pantalla
        
        # Velocidad random
        self.velocidad = random.uniform(1, 3)  # segundos para caer
        
        # Configurar animación
        self.animate_position = ft.Animation(
            int(self.velocidad * 1000),
            ft.AnimationCurve.LINEAR
        )
        
        # Rotación random
        self.rotate = ft.Rotate(
            random.uniform(-0.5, 0.5),
            alignment=ft.Alignment(0, 0)  # center
        )
        self.animate_rotation = ft.Animation(
            int(self.velocidad * 1000),
            ft.AnimationCurve.LINEAR
        )
        
        self.alto_pantalla = alto_pantalla
    
    async def caer(self):
        """Anima la caída del emoji."""
        # Mover a la parte inferior
        self.top = self.alto_pantalla + 100
        
        # Rotar mientras cae
        if self.rotate:
            angulo_actual = self.rotate.angle
            self.rotate.angle = angulo_actual + random.uniform(1, 3)
        
        self.update()
        
        # Esperar a que termine la animación
        await asyncio.sleep(self.velocidad)


class FondoAnimadoLogin(ft.Stack):
    """
    Fondo blanco con emojis de comida cayendo difuminados.
    """
    
    def __init__(self, ancho=None, alto=None):
        super().__init__()
        
        self.ancho = ancho or 1920
        self.alto = alto or 1080
        
        # Fondo blanco
        self.fondo = ft.Container(
            width=self.ancho,
            height=self.alto,
            bgcolor=ft.Colors.WHITE,
        )
        
        # Lista de emojis cayendo
        self.emojis = []
        
        # Stack: fondo + emojis
        self.controls = [self.fondo]
        
        # Control de animación
        self._animando = False
    
    async def iniciar_animacion(self, page):
        """Inicia la animación de emojis cayendo."""
        self._animando = True
        
        while self._animando:
            # Verificar que la página aún existe
            if not self.page:
                break
            
            # Crear nuevo emoji cada cierto tiempo
            emoji = EmojiCayendo(self.ancho, self.alto)
            self.emojis.append(emoji)
            self.controls.append(emoji)
            
            # Solo actualizar si la página aún existe
            try:
                if self.page:
                    self.update()
                else:
                    break
            except (RuntimeError, AttributeError):
                # Sesión destruida o página eliminada
                break
            
            # Animar caída
            page.run_task(emoji.caer)
            
            # Esperar antes de crear el siguiente
            await asyncio.sleep(random.uniform(0.3, 0.8))
            
            # Limpiar emojis que ya cayeron (mantener máximo 20)
            if len(self.emojis) > 20:
                emoji_viejo = self.emojis.pop(0)
                if emoji_viejo in self.controls:
                    self.controls.remove(emoji_viejo)
                    # Solo actualizar si la página aún existe
                    try:
                        if self.page:
                            self.update()
                    except (RuntimeError, AttributeError):
                        # Sesión destruida
                        break
    
    def detener_animacion(self):
        """Detiene la animación."""
        self._animando = False


def crear_fondo_login(page):
    """
    Crea el fondo animado para la página de login.
    
    Args:
        page: Página de Flet
    
    Returns:
        Stack con fondo blanco y emojis animados
    """
    # Obtener dimensiones de la ventana
    ancho = page.width or 1200
    alto = page.height or 800
    
    # Crear fondo animado
    fondo = FondoAnimadoLogin(ancho, alto)
    
    # Iniciar animación
    page.run_task(fondo.iniciar_animacion, page)
    
    return fondo


def crear_login_card(fondo_animado):
    """
    Crea la tarjeta de login centrada sobre el fondo animado.
    
    Args:
        fondo_animado: FondoAnimadoLogin
    
    Returns:
        Container con el formulario de login
    """
    from core.ui.colores import (
        PRIMARIO, 
        SECUNDARIO,
        obtener_gradiente_primario,
        obtener_sombra_elevada,
    )
    
    # Card de login con sombra y gradiente
    login_card = ft.Container(
        content=ft.Column(
            [
                # Logo / Título
                ft.Container(
                    content=ft.Text(
                        "🍔 ConyChi's",
                        size=48,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    gradient=obtener_gradiente_primario(),
                    padding=20,
                    border_radius=15,
                    margin=ft.margin.only(bottom=30),
                ),
                
                # Subtítulo
                ft.Text(
                    "Iniciar Sesión",
                    size=24,
                    weight=ft.FontWeight.W_500,
                    color=PRIMARIO,
                    text_align=ft.TextAlign.CENTER,
                ),
                
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                
                # Campo usuario
                ft.TextField(
                    label="Usuario",
                    prefix_icon=ft.Icons.PERSON,
                    border_color=PRIMARIO,
                    focused_border_color=SECUNDARIO,
                    filled=True,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                ),
                
                # Campo contraseña
                ft.TextField(
                    label="Contraseña",
                    prefix_icon=ft.Icons.LOCK,
                    password=True,
                    can_reveal_password=True,
                    border_color=PRIMARIO,
                    focused_border_color=SECUNDARIO,
                    filled=True,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                ),
                
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                
                # Botón login
                ft.Button(
                    "Entrar",
                    icon=ft.Icons.LOGIN,
                    width=300,
                    height=50,
                    bgcolor=PRIMARIO,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        ),
        width=400,
        padding=40,
        bgcolor=ft.Colors.WHITE,
        border_radius=20,
        shadow=obtener_sombra_elevada(),
    )
    
    # Centrar la card sobre el fondo animado
    fondo_animado.controls.append(
        ft.Container(
            content=login_card,
            alignment=ft.Alignment(0, 0),  # center
            expand=True,
        )
    )
    
    return fondo_animado


# Ejemplo de uso:
"""
def main(page: ft.Page):
    page.title = "Login Animado"
    page.padding = 0
    page.bgcolor = ft.Colors.WHITE
    
    # Crear fondo con emojis cayendo
    fondo = crear_fondo_login(page)
    
    # Agregar card de login
    login_completo = crear_login_card(fondo)
    
    page.add(login_completo)

ft.app(target=main)
"""
