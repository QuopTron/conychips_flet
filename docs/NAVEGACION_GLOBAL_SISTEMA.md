# Sistema de Navegación Global - Guía de Implementación

## 🎯 Resumen

Sistema completo de navegación con:
- ✅ **NavbarGlobal**: Header superior con filtro de sucursales
- ✅ **BottomNavigation**: Menú inferior con animaciones parallax
- ✅ **LayoutBase**: Plantilla base para todas las vistas
- ✅ **Gestos táctiles**: Swipe izquierda/derecha para navegar
- ✅ **Responsive**: Funciona en desktop y móvil

---

## 🏗️ Arquitectura

```
┌────────────────────────────────────┐
│      NavbarGlobal (Header)         │
│  [Logo] [Usuario] [Sucursales] [X] │
└────────────────────────────────────┘
┌────────────────────────────────────┐
│         Header de Vista            │
│  [←] Título de la Vista            │
└────────────────────────────────────┘
┌────────────────────────────────────┐
│                                    │
│         CONTENIDO                  │
│        (Con gestos)                │
│                                    │
└────────────────────────────────────┘
┌────────────────────────────────────┐
│    BottomNavigation (Menú)         │
│ [Dashboard] [Vouchers] [Finanzas]  │
└────────────────────────────────────┘
```

---

## 📦 Componentes Creados

### 1. NavbarGlobal
**Ubicación**: `features/admin/presentation/widgets/NavbarGlobal.py`

**Características**:
- Botón desplegable para seleccionar múltiples sucursales
- Checkboxes con "Todas las Sucursales"
- Info del usuario actual
- Botón de cerrar sesión
- Registro en auditoría

**Uso**:
```python
navbar = NavbarGlobal(
    pagina=page,
    usuario=usuario,
    on_cambio_sucursales=self._recargar_datos,
    on_cerrar_sesion=self._logout
)
```

### 2. BottomNavigation
**Ubicación**: `features/admin/presentation/widgets/BottomNavigation.py`

**Características**:
- Items con íconos y labels
- Animación parallax al hover (scale 1.1)
- Sombra dinámica
- Selección visual clara
- Items según rol del usuario

**Efectos**:
- ✨ Hover: Elemento se eleva con sombra
- 🎯 Selected: Fondo azul claro + ícono relleno
- ⚡ Click: Navegación instantánea

**Uso**:
```python
bottom_nav = BottomNavigation(
    pagina=page,
    usuario=usuario,
    on_navigate=self._navegar,
    selected_index=0
)
```

### 3. LayoutBase
**Ubicación**: `features/admin/presentation/widgets/LayoutBase.py`

**Características**:
- Combina NavbarGlobal + Header Vista + Contenido + BottomNav
- Gestos de swipe para navegación
- Método `construir()` para injectar contenido
- Callbacks centralizados

**Uso**:
```python
class MiVista(LayoutBase):
    def __init__(self, pagina, usuario):
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo_vista="Mi Vista",
            index_navegacion=0,
            on_volver_dashboard=self._ir_dashboard,
            on_cerrar_sesion=self._logout
        )
        
        # Crear contenido
        contenido = ft.Column([...])
        
        # Construir layout
        self.construir(contenido)
    
    def _on_sucursales_change(self, sucursales_ids):
        # Recargar con filtro
        pass
```

---

## 🚀 Migración de Vistas Existentes

### Antes (Sin layout global)

```python
class VistaAntigua(ft.Column):
    def __init__(self, pagina, usuario):
        super().__init__()
        self._pagina = pagina
        self._usuario = usuario
        
        # Crear header manualmente
        header = ft.Row([...])
        
        # Crear contenido
        contenido = ft.Column([...])
        
        self.controls = [header, contenido]
```

### Después (Con LayoutBase)

```python
from features.admin.presentation.widgets import LayoutBase

class VistaNueva(LayoutBase):
    def __init__(self, pagina, usuario):
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo_vista="Mi Vista",
            index_navegacion=1,  # Índice en bottom nav
            on_volver_dashboard=self._ir_home,
            on_cerrar_sesion=self._logout
        )
        
        # Solo crear contenido específico
        contenido = ft.Column([...])
        
        # Layout se construye automáticamente
        self.construir(contenido)
    
    def _on_sucursales_change(self, sucursales_ids):
        """Override para manejar cambios de sucursal"""
        # Actualizar BLoC con nuevo filtro
        self.mi_bloc.cambiar_sucursales(sucursales_ids)
```

---

## 🎨 Personalización

### Colores del Bottom Navigation

Editar en `BottomNavigation._crear_nav_item()`:

```python
color = COLORES.PRIMARIO if is_selected else COLORES.TEXTO_SECUNDARIO
bg_color = ft.Colors.BLUE_50 if is_selected else ft.Colors.TRANSPARENT
```

### Animación Parallax

Ajustar en `_on_item_hover()`:

```python
e.control.scale = 1.1  # ← Cambiar intensidad
e.control.shadow = ft.BoxShadow(
    blur_radius=8,  # ← Tamaño sombra
    offset=ft.Offset(0, -3)  # ← Elevación
)
```

### Items del Menú

Modificar `_obtener_items_menu()`:

```python
items = [
    BottomNavItem("Inicio", ft.icons.Icons.HOME, "home"),
    BottomNavItem("Productos", ft.icons.Icons.INVENTORY, "productos"),
    # ... más items
]
```

---

## 📱 Gestos Táctiles

### Implementación

El `LayoutBase` incluye un `GestureDetector`:

```python
ft.GestureDetector(
    content=contenido,
    on_horizontal_drag_end=self._on_swipe,
    drag_interval=10
)
```

### Detección de Swipe

```python
def _on_swipe(self, e):
    velocity = e.primary_velocity
    
    # Swipe derecha (velocity > 500)
    if velocity > 500:
        # Ir a vista anterior
    
    # Swipe izquierda (velocity < -500)
    elif velocity < -500:
        # Ir a vista siguiente
```

### Velocidad de Activación

Ajustar umbral en `_on_swipe()`:

```python
if velocity > 500:  # ← Aumentar para gestos más rápidos
    # Vista anterior
```

---

## 🔧 Integración con BLoCs

### Finanzas (múltiples sucursales)

```python
class FinanzasBloc:
    def __init__(self, sucursales_ids: Optional[List[int]] = None):
        self._sucursales_ids = sucursales_ids
    
    def cambiar_sucursales(self, sucursales_ids):
        self._sucursales_ids = sucursales_ids
        self.invalidar_cache()
        self._recargar()
    
    def _query(self, sesion):
        query = sesion.query(MODELO)
        if self._sucursales_ids:
            query = query.filter(
                MODELO.SUCURSAL_ID.in_(self._sucursales_ids)
            )
        return query.all()
```

### Vouchers (similar)

```python
def _manejar_cargar(self, sucursales_ids):
    query = sesion.query(MODELO_VOUCHER)
    
    if sucursales_ids:
        # JOIN con pedidos para filtrar
        query = query.join(MODELO_PEDIDO).filter(
            MODELO_PEDIDO.SUCURSAL_ID.in_(sucursales_ids)
        )
    
    return query.all()
```

---

## 📊 Ejemplo Completo: Usuarios

```python
from features.admin.presentation.widgets import LayoutBase
from core.ui.safe_actions import safe_update

class PaginaUsuariosNueva(LayoutBase):
    def __init__(self, pagina, usuario):
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo_vista="👥 Gestión de Usuarios",
            index_navegacion=3,  # 4to item en menú
            on_volver_dashboard=self._volver,
            on_cerrar_sesion=self._logout
        )
        
        # BLoC
        sucursales = self.obtener_sucursales_seleccionadas()
        self.bloc = UsuariosBloc(sucursales_ids=sucursales)
        
        # UI
        self.tabla = TablaUsuarios()
        self.filtros = FiltrosUsuarios()
        
        # Construir
        self._construir_vista()
    
    def _construir_vista(self):
        contenido = ft.Column([
            self.filtros,
            ft.Divider(),
            self.tabla
        ], expand=True, scroll=ft.ScrollMode.AUTO)
        
        self.construir(contenido)
        self.bloc.AGREGAR_LISTENER(self._on_estado_cambio)
        self._cargar_datos()
    
    def _on_sucursales_change(self, sucursales_ids):
        """Override: Recargar cuando cambian sucursales"""
        self.bloc = UsuariosBloc(sucursales_ids=sucursales_ids)
        self.bloc.AGREGAR_LISTENER(self._on_estado_cambio)
        self._cargar_datos()
    
    def _on_estado_cambio(self, estado):
        if isinstance(estado, UsuariosCargados):
            self.tabla.actualizar(estado.usuarios)
            safe_update(self._pagina)
    
    def _cargar_datos(self):
        self.bloc.AGREGAR_EVENTO(CargarUsuarios())
```

---

## ✅ Checklist de Migración

Para cada vista:

- [ ] Heredar de `LayoutBase` en lugar de `ft.Column`
- [ ] Mover lógica de header/navbar al constructor de `LayoutBase`
- [ ] Implementar `_on_sucursales_change()` para filtros
- [ ] Actualizar BLoC para aceptar `List[int]` en lugar de `int`
- [ ] Usar `self.construir(contenido)` en lugar de `self.controls = [...]`
- [ ] Remover headers/footers manuales
- [ ] Actualizar imports de `features.admin.presentation.widgets`
- [ ] Probar gestos de swipe
- [ ] Verificar navegación con bottom nav

---

## 🐛 Troubleshooting

### El bottom nav no aparece
- Verifica que `LayoutBase.construir()` sea llamado
- Revisa que `index_navegacion` esté entre 0 y len(items)-1

### Los gestos no funcionan
- Asegúrate que el contenido esté dentro del `GestureDetector`
- Verifica que `drag_interval` no sea muy alto

### Filtro de sucursales no aplica
- Implementa `_on_sucursales_change()` en tu vista
- Verifica que el BLoC soporte `List[int]`

### Navegación circular
- Usa callbacks específicos (`on_volver_dashboard`) en lugar de navegación directa
- Evita imports circulares

---

**Creado**: 2026-01-28  
**Versión**: 2.0  
**Autor**: GitHub Copilot
