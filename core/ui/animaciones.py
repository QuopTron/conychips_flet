"""
Decorador para animar cambios de color en controles de Flet.
Hace que los botones y containers cambien de color suavemente.
"""
import flet as ft
from functools import wraps
import random


def con_animacion_color(duration=300, curve=ft.AnimationCurve.EASE_IN_OUT):
    """
    Decorador que agrega animación de color a un control.
    
    Args:
        duration: Duración de la animación en ms
        curve: Curva de animación
    
    Ejemplo:
        @con_animacion_color(duration=500)
        def crear_boton():
            return ft.Button("Click", bgcolor=ft.Colors.BLUE)
    """
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            control = func(*args, **kwargs)
            
            # Agregar animación de color si el control la soporta
            if hasattr(control, 'bgcolor'):
                control.animate = ft.Animation(duration, curve)
            
            return control
        return wrapper
    return decorador


def animar_hover(control, color_normal, color_hover):
    """
    Agrega efecto hover con animación de color a un control.
    
    Args:
        control: Control de Flet (Button, Container, etc.)
        color_normal: Color en estado normal
        color_hover: Color cuando el mouse está encima
    """
    def on_hover(e):
        if e.data == "true":
            control.bgcolor = color_hover
        else:
            control.bgcolor = color_normal
        control.update()
    
    control.on_hover = on_hover
    control.animate = ft.Animation(200, ft.AnimationCurve.EASE_OUT)
    return control


def pulsar_atencion(control, page, veces=3, intervalo=500):
    """
    Hace que un control pulse para llamar la atención.
    
    Args:
        control: Control a animar
        page: Página de Flet
        veces: Número de pulsos
        intervalo: Tiempo entre pulsos en ms
    """
    import asyncio
    
    async def pulsar():
        color_original = control.bgcolor
        color_pulso = control.bgcolor if hasattr(control, 'bgcolor') else ft.Colors.BLUE
        
        for _ in range(veces):
            control.scale = 1.1
            control.update()
            await asyncio.sleep(intervalo / 2000)
            
            control.scale = 1.0
            control.update()
            await asyncio.sleep(intervalo / 2000)
    
    # Ejecutar animación
    if hasattr(control, 'scale'):
        control.animate_scale = ft.Animation(intervalo / 2, ft.AnimationCurve.EASE_IN_OUT)
        page.run_task(pulsar)
    
    return control


def gradiente_animado(colores, duracion_ciclo=5000):
    """
    Crea un gradiente que rota sus colores.
    
    Args:
        colores: Lista de colores para el gradiente
        duracion_ciclo: Tiempo para completar un ciclo en ms
    
    Returns:
        LinearGradient animado
    """
    # Rotar colores para crear efecto animado
    colores_rotados = colores[1:] + [colores[0]]
    
    return ft.LinearGradient(
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
        colors=colores,
        rotation=0,  # Se puede animar cambiando esto
    )


def efecto_ripple(control, color_ripple=None):
    """
    Agrega efecto ripple (ondas) al hacer click.
    
    Args:
        control: Control de Flet
        color_ripple: Color del efecto ripple
    """
    if color_ripple is None:
        color_ripple = ft.Colors.with_opacity(0.2, ft.Colors.WHITE)
    
    # Configurar ink para efecto ripple
    if hasattr(control, 'ink'):
        control.ink = True
        control.ink_color = color_ripple
    
    return control


def transicion_suave(control, propiedad, valor_inicial, valor_final, duracion=300):
    """
    Anima la transición de una propiedad de un valor a otro.
    
    Args:
        control: Control a animar
        propiedad: Nombre de la propiedad (ej: 'opacity', 'width')
        valor_inicial: Valor inicial
        valor_final: Valor final
        duracion: Duración en ms
    """
    import asyncio
    
    async def animar():
        # Configurar animación
        if propiedad == 'opacity':
            control.animate_opacity = ft.Animation(duracion, ft.AnimationCurve.EASE_IN_OUT)
            control.opacity = valor_final
        elif propiedad == 'width':
            control.animate_size = ft.Animation(duracion, ft.AnimationCurve.EASE_IN_OUT)
            control.width = valor_final
        elif propiedad == 'height':
            control.animate_size = ft.Animation(duracion, ft.AnimationCurve.EASE_IN_OUT)
            control.height = valor_final
        
        control.update()
    
    # Establecer valor inicial
    setattr(control, propiedad, valor_inicial)
    
    return animar


# Ejemplo de uso:
"""
# Decorador simple
@con_animacion_color(duration=500)
def crear_boton_animado():
    return ft.Button("Click me", bgcolor=ft.Colors.BLUE)

# Hover effect
boton = ft.Button("Hover me")
animar_hover(boton, ft.Colors.BLUE, ft.Colors.BLUE_700)

# Pulsar atención
boton_importante = ft.Button("¡Importante!")
pulsar_atencion(boton_importante, page, veces=5)

# Efecto ripple
boton_ripple = ft.Button("Ripple")
efecto_ripple(boton_ripple, ft.Colors.with_opacity(0.3, ft.Colors.WHITE))
"""
