"""Constantes de alineación centralizadas para evitar errores.

Usar estas constantes en lugar de escribir `ft.Alignment(0, 0)` u otros
valores ad-hoc. Los valores son instancias de
`ft.alignment.Alignment(x, y)` donde x,y están en [-1, 1].

Ejemplos:
  - CENTER = Alignment(0, 0)
  - TOP_LEFT = Alignment(-1, -1)
  - BOTTOM_RIGHT = Alignment(1, 1)

Esto evita confusiones sobre la API y facilita la reutilización.
"""
import flet as ft

# Centro
CENTER = ft.alignment.Alignment(0, 0)

# Regiones superiores / inferiores
TOP_LEFT = ft.alignment.Alignment(-1, -1)
TOP_CENTER = ft.alignment.Alignment(0, -1)
TOP_RIGHT = ft.alignment.Alignment(1, -1)

BOTTOM_LEFT = ft.alignment.Alignment(-1, 1)
BOTTOM_CENTER = ft.alignment.Alignment(0, 1)
BOTTOM_RIGHT = ft.alignment.Alignment(1, 1)

# Centro-izquierda / centro-derecha
CENTER_LEFT = ft.alignment.Alignment(-1, 0)
CENTER_RIGHT = ft.alignment.Alignment(1, 0)

# Mapa por nombre
BY_NAME = {
    'CENTER': CENTER,
    'TOP_LEFT': TOP_LEFT,
    'TOP_CENTER': TOP_CENTER,
    'TOP_RIGHT': TOP_RIGHT,
    'BOTTOM_LEFT': BOTTOM_LEFT,
    'BOTTOM_CENTER': BOTTOM_CENTER,
    'BOTTOM_RIGHT': BOTTOM_RIGHT,
    'CENTER_LEFT': CENTER_LEFT,
    'CENTER_RIGHT': CENTER_RIGHT,
}

def get(name: str, default=CENTER):
    return BY_NAME.get(name.upper(), default)
