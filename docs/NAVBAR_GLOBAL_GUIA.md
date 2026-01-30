# NavbarGlobal - Barra de Navegación Mejorada

## 🎯 Características

### ✅ Mejoras Implementadas

1. **Diseño Moderno y Elegante**
   - Botón principal con íconos y contador de sucursales
   - Panel desplegable con sombras y bordes redondeados
   - Colores consistentes con la paleta de la app

2. **Selección Múltiple de Sucursales**
   - Checkbox "Todas las Sucursales" (seleccionado por defecto)
   - Checkboxes individuales para cada sucursal activa
   - Contador dinámico (ej: "3 Sucursales")

3. **Global y Reutilizable**
   - Se puede usar en cualquier vista (Vouchers, Finanzas, Usuarios, etc.)
   - Mantiene estado entre navegaciones
   - Callback para notificar cambios

4. **Registro de Auditoría**
   - Cada cambio de filtro se registra en la tabla AUDITORIA
   - Detalles de qué sucursales fueron seleccionadas

---

## 📖 Uso

### Importación

```python
from features.admin.presentation.widgets import NavbarGlobal
```

### Ejemplo Básico

```python
class MiPagina(ft.Column):
    def __init__(self, pagina: ft.Page, usuario):
        self._pagina = pagina
        self._usuario = usuario
        
        # Crear navbar global
        self.navbar = NavbarGlobal(
            pagina=self._pagina,
            usuario=self._usuario,
            on_cambio_sucursales=self._on_sucursales_change,
            on_cerrar_sesion=self._on_logout
        )
        
        super().__init__()
        self._construir()
    
    def _construir(self):
        self.controls = [
            self.navbar,  # ← Navbar en la parte superior
            ft.Container(
                content=ft.Text("Contenido de la página"),
                expand=True
            )
        ]
    
    def _on_sucursales_change(self, sucursales_ids: Optional[List[int]]):
        """
        Callback cuando cambian las sucursales seleccionadas
        
        Args:
            sucursales_ids: None = todas, List[int] = IDs específicos
        """
        print(f"Sucursales seleccionadas: {sucursales_ids}")
        
        # Recargar datos con el nuevo filtro
        if sucursales_ids is None:
            # Mostrar todas las sucursales
            self._cargar_datos(sucursal_filtro=None)
        else:
            # Mostrar solo las sucursales seleccionadas
            self._cargar_datos(sucursal_filtro=sucursales_ids)
    
    def _on_logout(self):
        """Callback para cerrar sesión"""
        # Navegar a login
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._pagina.controls.clear()
        self._pagina.add(PaginaLogin(self._pagina))
        self._pagina.update()
```

---

## 🔧 Integración con BLoCs

### Finanzas

```python
class FinanzasPage(ft.Column):
    def __init__(self, PAGINA, USUARIO):
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        
        # Crear navbar
        self.navbar = NavbarGlobal(
            pagina=self._PAGINA,
            usuario=self._USUARIO,
            on_cambio_sucursales=self._recargar_con_filtro,
            on_cerrar_sesion=self._SALIR
        )
        
        # BLoC (se creará con filtro inicial)
        self.bloc = None
        
        super().__init__()
        self._inicializar_bloc()
    
    def _inicializar_bloc(self):
        """Inicializa BLoC con sucursales seleccionadas"""
        sucursales = self.navbar.obtener_sucursales_seleccionadas()
        self.bloc = FinanzasBloc(sucursales_ids=sucursales)
    
    def _recargar_con_filtro(self, sucursales_ids):
        """Recarga datos cuando cambia el filtro"""
        # Actualizar BLoC
        if hasattr(self.bloc, 'cambiar_sucursales'):
            self.bloc.cambiar_sucursales(sucursales_ids)
        else:
            # Recrear BLoC si no tiene método de cambio dinámico
            self._inicializar_bloc()
```

### Vouchers

```python
class VouchersPage(ft.Column):
    def __init__(self, PAGINA, USUARIO):
        # ...
        self.navbar = NavbarGlobal(
            pagina=self._PAGINA,
            usuario=self._USUARIO,
            on_cambio_sucursales=self._filtrar_vouchers,
            on_cerrar_sesion=self._SALIR
        )
    
    def _filtrar_vouchers(self, sucursales_ids):
        """Filtra vouchers por sucursales"""
        from features.vouchers.presentation.bloc import CargarVouchers
        
        # Cargar vouchers con filtro de múltiples sucursales
        VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(
            estado="PENDIENTE",
            offset=0,
            sucursales_ids=sucursales_ids  # ← Nueva funcionalidad
        ))
```

---

## 🎨 Personalización

### Colores

El navbar usa colores de `core.Constantes`:
- `COLORES.PRIMARIO`: Botón principal
- `COLORES.INFO`: Checkboxes de sucursales
- `COLORES.EXITO`: Botón "Aplicar Filtros"
- `COLORES.PELIGRO`: Botón cerrar sesión

### Tamaño

Ajusta el ancho del panel en `NavbarGlobal._construir()`:

```python
self._panel_sucursales = ft.Container(
    content=self._crear_contenido_panel(),
    width=350,  # ← Cambiar aquí
    # ...
)
```

---

## 🔍 Métodos Públicos

### `obtener_sucursales_seleccionadas()`

Retorna las sucursales actualmente seleccionadas.

**Returns:**
- `None`: Todas las sucursales
- `List[int]`: IDs de sucursales específicas

**Ejemplo:**
```python
navbar = NavbarGlobal(...)
sucursales = navbar.obtener_sucursales_seleccionadas()

if sucursales is None:
    print("Mostrando todas las sucursales")
else:
    print(f"Mostrando {len(sucursales)} sucursales: {sucursales}")
```

---

## 📊 Flujo de Datos

```
┌─────────────────────────┐
│ Usuario hace click en   │
│ botón "Sucursales"      │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ Se abre panel con       │
│ checkboxes              │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ Usuario selecciona      │
│ sucursales deseadas     │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ Click en "Aplicar       │
│ Filtros"                │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ 1. Actualiza estado     │
│ 2. Actualiza USUARIO    │
│ 3. Registra auditoría   │
│ 4. Llama callback       │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ Página recarga datos    │
│ con nuevo filtro        │
└─────────────────────────┘
```

---

## ⚙️ Actualizar BLoCs para Soportar Múltiples Sucursales

### Antes (Sucursal única)

```python
class FinanzasBloc:
    def __init__(self, sucursal_id: Optional[int] = None):
        self._sucursal_id = sucursal_id
    
    def _query(self, sesion):
        query = sesion.query(MODELO)
        if self._sucursal_id:
            query = query.filter(MODELO.SUCURSAL_ID == self._sucursal_id)
        return query.all()
```

### Después (Múltiples sucursales)

```python
class FinanzasBloc:
    def __init__(self, sucursales_ids: Optional[List[int]] = None):
        self._sucursales_ids = sucursales_ids
    
    def _query(self, sesion):
        query = sesion.query(MODELO)
        if self._sucursales_ids:
            # Filtrar por múltiples sucursales
            query = query.filter(MODELO.SUCURSAL_ID.in_(self._sucursales_ids))
        return query.all()
    
    def cambiar_sucursales(self, sucursales_ids: Optional[List[int]]):
        """Cambia el filtro de sucursales dinámicamente"""
        self._sucursales_ids = sucursales_ids
        self.invalidar_cache()
        self._manejar_cargar_datos()
```

---

## 🐛 Solución de Problemas

### El panel no se cierra

Verifica que `safe_update(self._pagina)` se llame después de cambiar `visible`.

### Las sucursales no se aplican

Asegúrate de que el BLoC soporte `List[int]` en lugar de `int` único.

### Error SQLAlchemy "lazy load"

Usa `joinedload()` para cargar relaciones:

```python
from sqlalchemy.orm import joinedload

query = sesion.query(MODELO).options(
    joinedload(MODELO.SUCURSAL)
)
```

---

## 📝 Notas

- El navbar guarda las sucursales en `USUARIO.SUCURSALES_SELECCIONADAS`
- Si `USUARIO.SUCURSALES_SELECCIONADAS` es `None`, significa "todas"
- Cada cambio se registra en la tabla `AUDITORIA`
- El estado persiste durante la sesión del usuario

---

## 🚀 Próximas Mejoras

- [ ] Guardar preferencia de sucursales en base de datos
- [ ] Animaciones al abrir/cerrar panel
- [ ] Búsqueda de sucursales en el panel
- [ ] Preset de combinaciones (ej: "Zona Norte", "Zona Sur")
- [ ] Estadísticas comparativas entre sucursales seleccionadas

---

**Creado**: 2026-01-28  
**Versión**: 1.0  
**Autor**: GitHub Copilot
