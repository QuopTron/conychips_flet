# 🎨 Sistema de Navegación Unificado - Guía Completa

## 📋 Resumen
Sistema de navegación global con diseño Material Design, filtros de sucursales, gestos de swipe y arquitectura limpia.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────┐
│           NavbarGlobal                       │
│  [Logo] [Sucursales ▼] [Usuario] [Logout]   │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│         Header de Vista                      │
│  [← Volver]  Título de la Vista              │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│                                              │
│         CONTENIDO ESPECÍFICO                 │
│       (GestureDetector para swipe)           │
│                                              │
│                                              │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│         BottomNavigation                     │
│  [📊] [📋] [💰] [👥] [🔍]                   │
└─────────────────────────────────────────────┘
```

## 🎯 Componentes Principales

### 1. NavbarGlobal
**Ubicación:** `features/admin/presentation/widgets/NavbarGlobal.py`

**Características:**
- ✅ Selector múltiple de sucursales con checkboxes
- ✅ Opción "Todas las Sucursales"
- ✅ Panel desplegable con animación
- ✅ Registro en auditoría de cambios
- ✅ Display de usuario actual
- ✅ Botón de cierre de sesión

**Uso:**
```python
navbar = NavbarGlobal(
    pagina=self._pagina,
    usuario=self._usuario,
    on_cambio_sucursales=self._callback_sucursales,
    on_cerrar_sesion=self._callback_logout
)

def _callback_sucursales(self, sucursales_ids: Optional[List[int]]):
    # None = Todas las sucursales
    # List[int] = Sucursales específicas seleccionadas
    if sucursales_ids is None:
        print("Mostrando todas las sucursales")
    else:
        print(f"Filtrando por: {sucursales_ids}")
```

**API Pública:**
```python
sucursales = navbar.obtener_sucursales_seleccionadas()
# Retorna: None (todas) o List[int] (específicas)
```

### 2. BottomNavigation
**Ubicación:** `features/admin/presentation/widgets/BottomNavigation.py`

**Características:**
- ✅ Material Design con elevación y sombras
- ✅ Animación parallax en hover (scale 1.0 → 1.1)
- ✅ Items filtrados por rol (SUPERADMIN ve todo)
- ✅ Estado seleccionado con fondo azul
- ✅ Iconos filled vs outlined

**Items de Navegación:**
| Index | Label | Icon | Route | Rol Mínimo |
|-------|-------|------|-------|------------|
| 0 | Dashboard | dashboard | dashboard | ADMIN |
| 1 | Vouchers | receipt | vouchers | ADMIN |
| 2 | Finanzas | attach_money | finanzas | ADMIN |
| 3 | Usuarios | people | usuarios | SUPERADMIN |
| 4 | Auditoría | search | auditoria | SUPERADMIN |

**Uso:**
```python
bottom_nav = BottomNavigation(
    pagina=self._pagina,
    usuario=self._usuario,
    on_navigate=self._navegar,
    selected_index=2  # Finanzas
)

def _navegar(self, route: str):
    if route == "vouchers":
        # Navegar a vouchers
        pass
```

### 3. LayoutBase
**Ubicación:** `features/admin/presentation/widgets/LayoutBase.py`

**Características:**
- ✅ Plantilla base para todas las vistas
- ✅ Integra NavbarGlobal + Header + Content + BottomNav
- ✅ Detección de gestos de swipe (horizontal drag)
- ✅ Navegación automática entre vistas
- ✅ Template Method Pattern

**Uso Completo:**
```python
from features.admin.presentation.widgets import LayoutBase

class MiVista(LayoutBase):
    """Vista personalizada usando layout global"""
    
    def __init__(self, pagina: ft.Page, usuario):
        # 1. Inicializar layout base
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo_vista="📊 Mi Vista",
            mostrar_boton_volver=True,
            index_navegacion=1,  # Posición en bottom nav
            on_volver_dashboard=self._ir_home,
            on_cerrar_sesion=self._logout
        )
        
        # 2. Crear BLoC con filtro de sucursales
        sucursales = self.obtener_sucursales_seleccionadas()
        self.bloc = MiBloc(sucursales_ids=sucursales)
        
        # 3. Construir contenido
        self._construir_ui()
    
    def _construir_ui(self):
        """Construir UI específica de la vista"""
        contenido = ft.Column([
            ft.Text("Contenido de mi vista"),
            ft.DataTable(...)
        ])
        
        # 4. Llamar a construir() con el contenido
        self.construir(contenido)
    
    def _on_sucursales_change(self, sucursales_ids: Optional[List[int]]):
        """OVERRIDE: Callback cuando cambian sucursales"""
        # Recrear BLoC con nuevo filtro
        self.bloc = MiBloc(sucursales_ids=sucursales_ids)
        self.bloc.cargar_datos()
    
    def _ir_home(self):
        """Navegar al dashboard"""
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._pagina.controls.clear()
        self._pagina.add(PaginaAdmin(self._pagina, self._usuario))
        safe_update(self._pagina)
    
    def _logout(self, e=None):
        """Cerrar sesión"""
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._pagina.controls.clear()
        self._pagina.add(PaginaLogin(self._pagina))
        safe_update(self._pagina)
```

## 🎮 Gestos de Swipe

### Umbrales de Velocidad
```python
# Swipe DERECHA (vista anterior)
if velocity > 500:
    navegar_anterior()

# Swipe IZQUIERDA (vista siguiente)
elif velocity < -500:
    navegar_siguiente()
```

### Ejemplo de Navegación con Swipe
```
[Dashboard] → swipe izquierda → [Vouchers]
[Vouchers] → swipe izquierda → [Finanzas]
[Finanzas] → swipe derecha → [Vouchers]
```

## 🔄 Integración con BLoCs

### Patrón Recomendado: Multi-Sucursal

```python
class MiBloc:
    def __init__(self, sucursales_ids: Optional[List[int]] = None):
        self._sucursales_ids = sucursales_ids
    
    def _obtener_datos(self):
        sesion = OBTENER_SESION()
        query = sesion.query(MODELO)
        
        # Filtrar por sucursales
        if self._sucursales_ids:
            query = query.filter(MODELO.SUCURSAL_ID.in_(self._sucursales_ids))
        
        return query.all()
    
    def cambiar_sucursales(self, sucursales_ids: Optional[List[int]]):
        """Actualizar filtro de sucursales"""
        self._sucursales_ids = sucursales_ids
        self.invalidar_cache()
        self._cargar_datos()
```

### Actualización Dinámica
```python
def _on_sucursales_change(self, sucursales_ids):
    """En la vista (LayoutBase override)"""
    # Opción 1: Recrear BLoC
    self.bloc = NuevoBloc(sucursales_ids=sucursales_ids)
    
    # Opción 2: Actualizar BLoC existente
    self.bloc.cambiar_sucursales(sucursales_ids)
```

## 📝 Migración de Vistas Antiguas

### Antes (sin LayoutBase):
```python
class ViejaVista(ft.Column):
    def __init__(self, pagina, usuario):
        super().__init__()
        self._pagina = pagina
        self._usuario = usuario
        
        # Navbar manual
        navbar = NavbarAdmin(...)
        
        # Contenido manual
        contenido = ft.Column([...])
        
        # Ensamblaje manual
        self.controls = [navbar, contenido]
```

### Después (con LayoutBase):
```python
class NuevaVista(LayoutBase):
    def __init__(self, pagina, usuario):
        super().__init__(
            pagina=pagina,
            usuario=usuario,
            titulo_vista="Mi Vista",
            index_navegacion=1,
            on_volver_dashboard=self._ir_home,
            on_cerrar_sesion=self._logout
        )
        
        # Solo construir contenido
        contenido = ft.Column([...])
        self.construir(contenido)
    
    def _on_sucursales_change(self, sucursales_ids):
        # Manejar cambio de sucursales
        pass
```

## ✅ Checklist de Migración

- [ ] 1. Cambiar herencia: `ft.Column` → `LayoutBase`
- [ ] 2. Llamar `super().__init__()` con parámetros correctos
- [ ] 3. Crear contenido específico de la vista
- [ ] 4. Llamar `self.construir(contenido)` al final
- [ ] 5. Implementar `_on_sucursales_change()` si usa BLoC
- [ ] 6. Actualizar BLoC para aceptar `sucursales_ids: Optional[List[int]]`
- [ ] 7. Filtrar queries con `.filter(MODELO.SUCURSAL_ID.in_(sucursales_ids))`
- [ ] 8. Implementar callbacks `_ir_home` y `_logout`
- [ ] 9. Probar swipe gestures
- [ ] 10. Probar filtro de sucursales

## 🐛 Troubleshooting

### Problema: Pantalla en blanco
**Causa:** No se llamó `self.construir(contenido)`
**Solución:**
```python
def __init__(...):
    super().__init__(...)
    contenido = self._crear_contenido()
    self.construir(contenido)  # ← IMPORTANTE
```

### Problema: Error "_LOGOUT not found"
**Causa:** Método tiene nombre incorrecto
**Solución:** Verificar nombre del método:
```python
# PaginaAdmin usa:
on_cerrar_sesion=self._SALIR

# LayoutBase espera:
on_cerrar_sesion=self._cerrar_sesion
```

### Problema: Swipe no funciona
**Causa:** `on_horizontal_drag_end` no detecta velocidad
**Solución:** Verificar que `e.primary_velocity` existe:
```python
def _on_swipe(self, e):
    if not hasattr(e, 'primary_velocity'):
        return
    velocity = e.primary_velocity
```

### Problema: Filtro de sucursales no actualiza datos
**Causa:** BLoC no recibe nuevo filtro
**Solución:** Implementar `_on_sucursales_change()`:
```python
def _on_sucursales_change(self, sucursales_ids):
    self.bloc.cambiar_sucursales(sucursales_ids)
```

## 🎨 Diseño Material

### Paleta de Colores
- **Primario:** `#1976D2` (Azul)
- **Seleccionado:** `rgba(25, 118, 210, 0.1)`
- **Hover:** `rgba(0, 0, 0, 0.04)`
- **Sombra:** `blur_radius=8, offset=(0, -3)`

### Animaciones
- **Scale en Hover:** `1.0 → 1.1` (100ms)
- **Shadow en Hover:** `blur_radius: 4 → 8`
- **Panel Sucursales:** Slide down con fade

### Elevaciones
- **NavbarGlobal:** `elevation=4`
- **BottomNavigation:** `elevation=8`
- **Panel Sucursales:** `elevation=16` con sombra

## 📊 Métricas de Performance

### Antes (sin Layout Global):
- Código duplicado: ~200 líneas por vista
- Navbar creado: 1 por cada vista
- Manejo manual de navegación

### Después (con LayoutBase):
- Código reutilizable: ~50 líneas por vista (-75%)
- Navbar singleton: 1 instancia compartida
- Navegación automática con gestos

## 🚀 Próximos Pasos

1. ✅ ~~NavbarGlobal con filtro de sucursales~~
2. ✅ ~~BottomNavigation con Material Design~~
3. ✅ ~~LayoutBase con gestos de swipe~~
4. ✅ ~~FinanzasPage migrado como ejemplo~~
5. 🔄 Migrar VouchersPage a LayoutBase
6. 🔄 Migrar PaginaGestionUsuarios a LayoutBase
7. 🔄 Crear página de Auditoría
8. 🔄 Agregar modo burger para móvil (<720px)
9. 🔄 Tests unitarios de componentes
10. 🔄 Optimización de cache para filtros

## 📚 Referencias

- **Flet Docs:** https://flet.dev/docs/
- **Material Design:** https://m3.material.io/
- **BLoC Pattern:** Clean Architecture
- **Gestures:** `ft.GestureDetector` API

---

**Última actualización:** 28 de Enero 2026
**Versión:** 1.0.0
**Autor:** GitHub Copilot
