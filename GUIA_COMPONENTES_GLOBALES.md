# 🎨 Guía de Componentes Globales Reutilizables

## 📍 Ubicación
`core/ui/componentes_globales.py`

## 🎯 Propósito
Componentes UI estandarizados que siguen la sintaxis correcta de **Flet 0.80.3** y pueden ser reutilizados en cualquier vista.

---

## 📦 Componentes Disponibles

### 1️⃣ DateRangePicker
**Selector de rango de fechas con DatePicker nativo**

```python
from core.ui import DateRangePicker

# Uso básico
selector = DateRangePicker(
    on_change=lambda inicio, fin: print(f"{inicio} - {fin}"),
    label="Seleccionar Período"
)

# Obtener valores
inicio, fin = selector.obtener_valores()

# Limpiar
selector.limpiar()
```

**Características:**
- Click 1: Selecciona fecha inicio
- Click 2: Selecciona fecha fin
- Muestra rango seleccionado debajo del botón
- Usa `page.overlay` para los DatePickers nativos

---

### 2️⃣ BotonBuscar
**Botón de búsqueda estandarizado**

```python
from core.ui import BotonBuscar

btn = BotonBuscar(
    on_click=lambda e: buscar(),
    tooltip="Buscar pedidos"
)
```

**Estilo:**
- Icono: 🔍 (SEARCH)
- Color: Azul (#1976D2)
- Tamaño: 48x48px
- Border radius: 8px

---

### 3️⃣ BotonLimpiar
**Botón para limpiar filtros**

```python
from core.ui import BotonLimpiar

btn = BotonLimpiar(
    on_click=lambda e: limpiar_todo(),
    tooltip="Resetear filtros"
)
```

**Estilo:**
- Icono: 🗑️ (CLEAR_ALL)
- Color: Rojo (#EF5350)
- Tamaño: 48x48px

---

### 4️⃣ CampoBusqueda
**Campo de texto para búsqueda**

```python
from core.ui import CampoBusqueda

campo = CampoBusqueda(
    hint="Buscar por código o nombre...",
    width=300,
    on_submit=lambda e: realizar_busqueda(e.control.value)
)
```

**Características:**
- Icono de lupa al inicio
- Enter para buscar
- Tamaño: 250x45px (configurable)

---

### 5️⃣ FiltroDropdown
**Dropdown estandarizado para filtros**

```python
from core.ui import FiltroDropdown

filtro = FiltroDropdown(
    label="Estado",
    opciones=[
        ("TODOS", "Todos"),
        ("ACTIVO", "Activos"),
        ("INACTIVO", "Inactivos")
    ],
    on_change=lambda e: filtrar(e.control.value),
    width=180
)
```

**Características:**
- Hint por defecto: "Todos"
- Tamaño: 180x45px (configurable)
- Border radius: 8px

---

### 6️⃣ ContenedorFiltros
**Contenedor visual para agrupar filtros**

```python
from core.ui import ContenedorFiltros

contenedor = ContenedorFiltros(
    controles=[campo_busqueda, filtro_estado, filtro_fecha]
)
```

**Estilo:**
- Fondo: Gris claro
- Border: Gris 300
- Border radius: 8px
- Padding: 15px
- Responsive (wrap=True)

---

### 7️⃣ TablaResponsive
**Wrapper responsive para DataTable**

```python
from core.ui import TablaResponsive

# Crear tabla
tabla = ft.DataTable(...)

# Envolver en contenedor responsive
tabla_responsive = TablaResponsive(tabla)
```

**Características:**
- Scroll horizontal y vertical automático
- `expand=True` para ocupar todo el espacio
- Border y padding incluidos
- Fondo blanco

---

### 8️⃣ TarjetaEstadistica
**Tarjeta para mostrar métricas**

```python
from core.ui import TarjetaEstadistica

tarjeta = TarjetaEstadistica(
    titulo="Total Ventas",
    valor="Bs 15,420.50",
    icono=ft.icons.Icons.ATTACH_MONEY,
    color=ft.Colors.GREEN
)
```

**Estilo:**
- Icono grande (32px)
- Valor destacado (20px, bold)
- Border con color del icono
- Sombra sutil

---

### 9️⃣ IndicadorCarga
**Spinner de carga estandarizado**

```python
from core.ui import IndicadorCarga

cargando = IndicadorCarga(mensaje="Cargando datos financieros...")
```

**Características:**
- ProgressRing animado
- Texto personalizable
- Centrado vertical y horizontal
- `expand=True`

---

## 🔧 Ejemplo Completo: Vista con Filtros

```python
from core.ui import (
    DateRangePicker, BotonBuscar, BotonLimpiar,
    CampoBusqueda, FiltroDropdown, TablaResponsive,
    IndicadorCarga
)

class MiVista(ft.Column):
    def __init__(self):
        super().__init__()
        
        # Componentes de búsqueda
        self.campo = CampoBusqueda(on_submit=self._buscar)
        self.fechas = DateRangePicker(on_change=self._on_fecha_change)
        self.btn_buscar = BotonBuscar(on_click=self._buscar)
        self.btn_limpiar = BotonLimpiar(on_click=self._limpiar)
        
        # Filtros
        self.filtro_estado = FiltroDropdown(
            label="Estado",
            opciones=[("TODOS", "Todos"), ("ACTIVO", "Activos")],
            on_change=self._filtrar
        )
        
        # Tabla
        tabla = ft.DataTable(...)
        self.tabla_responsive = TablaResponsive(tabla)
        
        # Layout
        self.controls = [
            # Filtros
            ft.Container(
                content=ft.Column([
                    ft.Row([self.campo, self.fechas, self.btn_buscar, self.btn_limpiar]),
                    ft.Row([self.filtro_estado])
                ], spacing=10),
                bgcolor=ft.Colors.GREY_50,
                padding=15,
                border_radius=8
            ),
            # Tabla responsive
            self.tabla_responsive
        ]
        self.expand = True
    
    def _buscar(self, e):
        inicio, fin = self.fechas.obtener_valores()
        codigo = self.campo.value
        # Realizar búsqueda...
    
    def _limpiar(self, e):
        self.campo.value = ""
        self.fechas.limpiar()
        self.filtro_estado.value = "TODOS"
```

---

## ✅ Ventajas

1. **Sintaxis Correcta**: Todos siguen Flet 0.80.3
2. **Consistencia**: Mismo estilo en toda la app
3. **Mantenibilidad**: Cambios en un solo lugar
4. **Reutilización**: Import y usa en cualquier vista
5. **Responsive**: Diseñados para adaptarse a diferentes tamaños

---

## 📝 Notas Importantes

### Sintaxis de Botones en Flet 0.80.3
```python
# ❌ INCORRECTO
btn = ft.ElevatedButton(text="Click", icon=ft.icons.Icons.SEARCH)

# ✅ CORRECTO
btn = ft.ElevatedButton(
    content=ft.Row([
        ft.Icon(ft.icons.Icons.SEARCH),
        ft.Text("Click")
    ])
)
```

### Dropdown Options
```python
# ✅ CORRECTO
options = [
    ft.dropdown.Option(key="valor", text="Texto Mostrado")
]
```

### Eventos
- `on_click`: Botones e IconButtons
- `on_change`: Dropdowns y DatePickers  
- `on_submit`: TextFields (Enter)

---

## 🚀 Agregar Nuevos Componentes

1. Agregar clase en `componentes_globales.py`
2. Exportar en `core/ui/__init__.py`
3. Documentar en este archivo
4. Usar en vistas con `from core.ui import NuevoComponente`
