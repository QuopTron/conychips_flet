# 🚀 GUÍA RÁPIDA - Módulo Admin Refactorizado

## 📍 Navegación por la Nueva Estructura

### Páginas CRUD (gestion/)

```python
# Todas siguen el mismo patrón:
from features.admin.presentation.pages.gestion.ExtrasPage import ExtrasPage
from features.admin.presentation.pages.gestion.ProveedoresPage import ProveedoresPage
from features.admin.presentation.pages.gestion.InsumosPage import InsumosPage
from features.admin.presentation.pages.gestion.OfertasPage import OfertasPage
from features.admin.presentation.pages.gestion.ProductosPage import ProductosPage
from features.admin.presentation.pages.gestion.SucursalesPage import SucursalesPage
from features.admin.presentation.pages.gestion.UsuariosPage import UsuariosPage
from features.admin.presentation.pages.gestion.RolesPage import RolesPage
from features.admin.presentation.pages.gestion.HorariosPage import HorariosPage
from features.admin.presentation.pages.gestion.CajaPage import CajaPage
```

### Vistas Especializadas (vistas/)

```python
from features.admin.presentation.pages.vistas.AuditoriaPage import AuditoriaPage
from features.admin.presentation.pages.vistas.FinanzasPage import FinanzasPage
from features.admin.presentation.pages.vistas.PedidosPage import PedidosPage
from features.admin.presentation.pages.vistas.VouchersPage import VouchersPage
from features.admin.presentation.pages.vistas.ResenasPage import ResenasPage
```

---

## 🆕 Crear Nueva Página CRUD (5 minutos)

### Paso 1: Crear archivo en `gestion/`

```python
# features/admin/presentation/pages/gestion/MiNuevaPagina.py

from features.admin.presentation.widgets.PaginaCRUDBase import PaginaCRUDBase
from features.admin.presentation.widgets.ComponentesGlobales import FormularioCRUD
from core.base_datos.ConfiguracionBD import MODELO_MI_ENTIDAD
from core.Constantes import ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL


@REQUIERE_ROL(ROLES.ADMINISTRADOR)
class MiNuevaPagina(PaginaCRUDBase):
    """Gestión de mi nueva entidad."""

    def __init__(self, PAGINA, USUARIO):
        super().__init__(PAGINA, USUARIO, "Mi Título")

    def _OBTENER_MODELO(self):
        return MODELO_MI_ENTIDAD

    def _OBTENER_CAMPOS_TABLA(self):
        return ["CAMPO1", "CAMPO2", "CAMPO3"]

    def _OBTENER_COLUMNAS_TABLA(self):
        return ["Campo 1", "Campo 2", "Campo 3"]

    def _CREAR_FORMULARIO(self, item=None):
        return [
            FormularioCRUD.CREAR_CAMPO(
                "Campo 1",
                item.CAMPO1 if item else ""
            ),
            FormularioCRUD.CREAR_CAMPO(
                "Campo 2",
                item.CAMPO2 if item else ""
            ),
            FormularioCRUD.CREAR_DROPDOWN(
                "Campo 3",
                [
                    {"label": "Opción 1", "value": "OP1"},
                    {"label": "Opción 2", "value": "OP2"},
                ],
                item.CAMPO3 if item else "OP1"
            ),
        ]

    def _EXTRAER_DATOS_FORMULARIO(self, campos):
        return {
            "CAMPO1": campos[0].value.strip(),
            "CAMPO2": campos[1].value.strip(),
            "CAMPO3": campos[2].value,
        }
```

### Paso 2: Agregar al `__init__.py`

```python
# features/admin/presentation/pages/gestion/__init__.py

from .MiNuevaPagina import MiNuevaPagina

__all__ = [
    # ... existentes
    "MiNuevaPagina",
]
```

### Paso 3: Agregar navegación en `PaginaAdmin.py`

```python
def _VER_MI_NUEVA_PAGINA(self, e):
    """Abre mi nueva página"""
    from features.admin.presentation.pages.gestion.MiNuevaPagina import MiNuevaPagina

    self._PAGINA.controls.clear()
    self._PAGINA.controls.append(MiNuevaPagina(self._PAGINA, self._USUARIO))
    self._PAGINA.update()
```

**¡LISTO!** Tienes CRUD completo funcionando:

- ✅ Listar con tabla
- ✅ Crear con formulario
- ✅ Editar con formulario prellenado
- ✅ Eliminar con confirmación
- ✅ Búsqueda
- ✅ Navegación
- ✅ Notificaciones

---

## 🎨 Personalizar Comportamiento

### Formatear valores en tabla

```python
def _FORMATEAR_VALOR_CELDA(self, item, campo):
    """Personaliza cómo se muestran los valores."""
    if campo == "ACTIVO":
        return "✓ Activo" if item.ACTIVO else "✗ Inactivo"
    elif campo == "PRECIO":
        return f"S/. {item.PRECIO:.2f}"
    return super()._FORMATEAR_VALOR_CELDA(item, campo)
```

### Validaciones personalizadas

```python
def _VALIDAR_ANTES_GUARDAR(self, datos):
    """Validación antes de guardar."""
    if float(datos.get("PRECIO", 0)) < 0:
        raise ValueError("El precio no puede ser negativo")
    return datos
```

### Agregar campos adicionales antes de guardar

```python
def _EXTRAER_DATOS_FORMULARIO(self, campos):
    datos = super()._EXTRAER_DATOS_FORMULARIO(campos)
    # Agregar campos automáticos
    datos["CREADO_POR"] = self._USUARIO.USUARIO
    datos["FECHA_CREACION"] = datetime.now()
    return datos
```

---

## 🔧 Componentes Disponibles

### FormularioCRUD

```python
# Campo de texto
FormularioCRUD.CREAR_CAMPO("Etiqueta", valor, hint="Ayuda", multiline=False)

# Dropdown/Select
FormularioCRUD.CREAR_DROPDOWN("Etiqueta", opciones, valor_inicial)

# Switch/Toggle
FormularioCRUD.CREAR_SWITCH("Etiqueta", valor_booleano)
```

### GestorCRUD

```python
# Cargar datos
items = GestorCRUD.CARGAR_DATOS(MODELO)

# Crear
GestorCRUD.CREAR(MODELO, datos)

# Actualizar
GestorCRUD.ACTUALIZAR(item, datos)

# Eliminar
GestorCRUD.ELIMINAR(item)
```

### TablaCRUD

```python
TablaCRUD.CREAR_TABLA(
    items=lista,
    campos=["CAMPO1", "CAMPO2"],
    columnas=["Columna 1", "Columna 2"],
    on_editar=self._ABRIR_FORMULARIO,
    on_eliminar=self._CONFIRMAR_ELIMINAR
)
```

### Notificador

```python
Notificador.EXITO(pagina, "Operación exitosa")
Notificador.ERROR(pagina, "Algo salió mal")
Notificador.INFO(pagina, "Información")
Notificador.ADVERTENCIA(pagina, "Cuidado")
```

### DialogoConfirmacion

```python
DialogoConfirmacion.MOSTRAR(
    pagina,
    "¿Estás seguro?",
    callback_confirmar
)
```

---

## 🔐 Control de Acceso

### Decoradores disponibles

```python
@REQUIERE_ROL(ROLES.SUPERADMIN)           # Solo superadmin
@REQUIERE_ROL(ROLES.ADMINISTRADOR)        # Admin o superior
@REQUIERE_ROL(ROLES.SUPERVISOR)           # Supervisor o superior
@REQUIERE_ROL(ROLES.EMPLEADO)             # Cualquier empleado
```

### Roles definidos

- `SUPERADMIN` - Acceso total
- `ADMINISTRADOR` - Gestión completa
- `SUPERVISOR` - Supervisión y reportes
- `EMPLEADO` - Acceso básico

---

## 🎯 Integrar con BLoC

### Para páginas complejas (ejemplo: UsuariosPage)

```python
@REQUIERE_ROL(ROLES.ADMINISTRADOR)
class MiPaginaConBloc(PaginaCRUDBase):

    def __init__(self, PAGINA, USUARIO):
        self._BLOC = MiBloc()
        super().__init__(PAGINA, USUARIO, "Título")
        self._SUSCRIBIR_BLOC()

    def _SUSCRIBIR_BLOC(self):
        """Escucha cambios de estado."""
        def _listener(state):
            if state.items:
                self._ITEMS = state.items
                self._ACTUALIZAR_LISTA()

            if state.error:
                self._MOSTRAR_ERROR(state.error)

        self._BLOC.stream.listen(_listener)

    def _CARGAR_DATOS_INICIAL(self):
        """Carga usando BLoC."""
        self._BLOC.add(CargarDatos())
```

---

## 📚 Archivos Importantes

| Archivo                  | Propósito                                  |
| ------------------------ | ------------------------------------------ |
| `PaginaCRUDBase.py`      | Base abstracta para todas las páginas CRUD |
| `ComponentesGlobales.py` | Todos los componentes reutilizables        |
| `gestion/__init__.py`    | Exports de páginas CRUD                    |
| `vistas/__init__.py`     | Exports de vistas especializadas           |
| `PaginaAdmin.py`         | Dashboard principal con navegación         |

---

## ❗ Errores Comunes

### 1. Import no encontrado

```python
# ❌ MAL
from features.admin.pages.MiPagina import MiPagina

# ✅ BIEN
from features.admin.presentation.pages.gestion.MiPagina import MiPagina
```

### 2. No hereda de PaginaCRUDBase

```python
# ❌ MAL
class MiPagina(ft.Column):

# ✅ BIEN
class MiPagina(PaginaCRUDBase):
```

### 3. Olvidar decorador de seguridad

```python
# ❌ MAL
class MiPagina(PaginaCRUDBase):

# ✅ BIEN
@REQUIERE_ROL(ROLES.ADMINISTRADOR)
class MiPagina(PaginaCRUDBase):
```

### 4. No actualizar **init**.py

```python
# Siempre agregar nueva página al __init__.py
from .MiNuevaPagina import MiNuevaPagina

__all__ = ["MiNuevaPagina", ...]
```

---

## 🎓 Mejores Prácticas

1. **Nomenclatura**: `*Page` para CRUD, `*Page` para vistas
2. **Ubicación**: CRUD en `gestion/`, vistas en `vistas/`
3. **Decoradores**: Siempre usar `@REQUIERE_ROL`
4. **DRY**: Si algo se repite 2+ veces, hacer componente global
5. **BLoC**: Usar para páginas con lógica compleja
6. **Validación**: Validar en `_EXTRAER_DATOS_FORMULARIO`
7. **Mensajes**: Usar `Notificador` para feedback al usuario

---

## 📞 Necesitas Ayuda?

1. Ver ejemplos existentes en `gestion/`
2. Revisar `REFACTORIZACION_COMPLETA_ADMIN.md`
3. Revisar `PaginaCRUDBase.py` para ver métodos disponibles
4. Revisar `ComponentesGlobales.py` para ver componentes

---

**¡Happy Coding!** 🚀
