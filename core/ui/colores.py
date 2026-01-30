"""
Paleta de colores moderna y vibrante para la aplicación.
Colores optimizados para accesibilidad y estética.
"""
import flet as ft

# 🎨 Paleta principal - Gradientes modernos
PRIMARIO = "#6366F1"  # Indigo vibrante
PRIMARIO_CLARO = "#818CF8"
PRIMARIO_OSCURO = "#4F46E5"

SECUNDARIO = "#EC4899"  # Rosa fucsiaclaro
SECUNDARIO_CLARO = "#F472B6"
SECUNDARIO_OSCURO = "#DB2777"

# ✅ Estados de éxito/error mejorados
EXITO = "#10B981"  # Verde esmeralda
EXITO_CLARO = "#34D399"
EXITO_OSCURO = "#059669"

PELIGRO = "#EF4444"  # Rojo coral
PELIGRO_CLARO = "#F87171"
PELIGRO_OSCURO = "#DC2626"

ADVERTENCIA = "#F59E0B"  # Naranja dorado
ADVERTENCIA_CLARO = "#FBBF24"
ADVERTENCIA_OSCURO = "#D97706"

INFO = "#06B6D4"  # Cyan brillante
INFO_CLARO = "#22D3EE"
INFO_OSCURO = "#0891B2"

# 🌈 Fondos y superficies
FONDO = "#FFFFFF"
FONDO_OSCURO = "#111827"
FONDO_TARJETA = "#F9FAFB"
FONDO_TARJETA_HOVER = "#F3F4F6"

# 📝 Textos con mejor contraste
TEXTO = "#111827"
TEXTO_SECUNDARIO = "#6B7280"
TEXTO_TERCIARIO = "#9CA3AF"
TEXTO_BLANCO = "#FFFFFF"

# 🔲 Bordes y divisores
BORDE = "#E5E7EB"
BORDE_CLARO = "#F3F4F6"
BORDE_OSCURO = "#D1D5DB"

# 🍔 Colores temáticos de comida
COMIDA_NARANJA = "#FB923C"  # Naranjo pastel (burger/tacos)
COMIDA_AMARILLO = "#FBBF24"  # Amarillo dorado (papas)
COMIDA_ROJO = "#F87171"  # Rojo pastel (ketchup/tomate)
COMIDA_VERDE = "#4ADE80"  # Verde lechuga
COMIDA_MARRON = "#A16207"  # Marrón (carne/chocolate)

# 💫 Overlays y sombras
OVERLAY_OSCURO = "#80000000"  # Negro 50% transparencia
OVERLAY_CLARO = "#20000000"  # Negro 12% transparencia
SOMBRA_SUAVE = "#10000000"  # Negro 6% transparencia

# Mapeo de colores antiguos a nuevos (retrocompatibilidad)
COLORES_LEGACY = {
    "PRIMARIO": PRIMARIO,
    "SECUNDARIO": SECUNDARIO,
    "EXITO": EXITO,
    "PELIGRO": PELIGRO,
    "ADVERTENCIA": ADVERTENCIA,
    "INFO": INFO,
    "FONDO": FONDO,
    "FONDO_TARJETA": FONDO_TARJETA,
    "TEXTO": TEXTO,
    "TEXTO_SECUNDARIO": TEXTO_SECUNDARIO,
    "TEXTO_BLANCO": TEXTO_BLANCO,
    "BORDE": BORDE,
}

def obtener_gradiente_primario():
    """Gradiente hermoso para botones/headers"""
    return ft.LinearGradient(
        begin=ft.alignment.Alignment(-1, -1),  # top_left
        end=ft.alignment.Alignment(1, 1),      # bottom_right
        colors=[PRIMARIO, PRIMARIO_OSCURO],
    )

def obtener_gradiente_secundario():
    """Gradiente secundario para acentos"""
    return ft.LinearGradient(
        begin=ft.alignment.Alignment(-1, -1),
        end=ft.alignment.Alignment(1, 1),
        colors=[SECUNDARIO, SECUNDARIO_OSCURO],
    )

def obtener_gradiente_exito():
    """Gradiente de éxito"""
    return ft.LinearGradient(
        begin=ft.alignment.Alignment(-1, -1),
        end=ft.alignment.Alignment(1, 1),
        colors=[EXITO, EXITO_OSCURO],
    )

def obtener_gradiente_peligro():
    """Gradiente de peligro/rechazo"""
    return ft.LinearGradient(
        begin=ft.alignment.Alignment(-1, -1),
        end=ft.alignment.Alignment(1, 1),
        colors=[PELIGRO, PELIGRO_OSCURO],
    )

def obtener_sombra_elevada():
    """Sombra para overlays"""
    return ft.BoxShadow(
        spread_radius=1,
        blur_radius=20,
        color=OVERLAY_OSCURO,
        offset=ft.Offset(0, 10),
    )

def obtener_sombra_suave():
    """Sombra para cards"""
    return ft.BoxShadow(
        spread_radius=0,
        blur_radius=10,
        color=SOMBRA_SUAVE,
        offset=ft.Offset(0, 2),
    )
