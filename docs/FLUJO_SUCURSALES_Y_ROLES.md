# 🏪 Flujo de Sucursales y Sistema de Roles/Permisos

## 📍 Navegación a Sucursales

### Desde el Dashboard Admin

1. **Entrada**: El usuario hace clic en el botón "Sucursales" del dashboard
   - **Ubicación**: [PaginaAdmin.py](../features/admin/presentation/pages/PaginaAdmin.py#L473)
   - **Método**: `_VER_SUCURSALES(self, e)`
   
```python
def _VER_SUCURSALES(self, e):
    from features.admin.presentation.pages.vistas.SucursalesPage import SucursalesPage
    
    self._pagina.controls.clear()
    self._pagina.controls.append(SucursalesPage(self._pagina, self._usuario))
    safe_update(self._pagina)
```

2. **Verificación de Permisos**: 
   - El decorador `@REQUIERE_ROL(ROLES.ADMIN)` valida que el usuario tenga rol ADMIN o SUPERADMIN
   - Si no tiene permisos, se rechaza el acceso

---

## 🔄 Flujo de Carga de Sucursales

### Inicialización de SucursalesPage

**Archivo**: [SucursalesPage.py](../features/admin/presentation/pages/vistas/SucursalesPage.py)

1. **Constructor** (línea 18-34):
```python
def __init__(self, PAGINA: ft.Page, USUARIO):
    super().__init__(
        pagina=PAGINA,
        usuario=USUARIO,
        titulo_vista="🏪 Sucursales",
        mostrar_boton_volver=True,
        index_navegacion=2,
        on_volver_dashboard=self._ir_dashboard,
        on_cerrar_sesion=self._cerrar_sesion
    )
    
    self._sucursales: List = []
    self._filtro_estado = "TODAS"
    self._overlay_crear = None
    self._overlay_editar = None
    
    self._CONSTRUIR_UI()
    self._cargar_sucursales()  # ← CARGA INICIAL
```

### Carga de Datos desde Base de Datos

2. **Método `_cargar_sucursales()`** (línea 204-215):
```python
def _cargar_sucursales(self):
    """Carga sucursales desde la BD"""
    with OBTENER_SESION() as sesion:
        query = sesion.query(MODELO_SUCURSAL)
        
        # Aplica filtro si no es "TODAS"
        if self._filtro_estado != "TODAS":
            query = query.filter_by(ESTADO=self._filtro_estado)
        
        # Ordena por fecha de creación (más reciente primero)
        self._sucursales = query.order_by(
            MODELO_SUCURSAL.FECHA_CREACION.desc()
        ).all()
    
    self._actualizar_ui()
```

### Renderizado de la UI

3. **Método `_actualizar_ui()`** (línea 217-285):
   - Si no hay sucursales: muestra mensaje vacío con botón "Crear Primera Sucursal"
   - Si hay sucursales: crea un card por cada sucursal usando `_crear_card_sucursal()`

---

## 📝 CRUD de Sucursales

### ✅ Crear Sucursal

**Método**: `_mostrar_overlay_crear()` (línea 584-655)

**Flujo**:
1. Se crea un formulario con campos:
   - Nombre de la sucursal
   - Dirección
   - Teléfono
   - Horario
   - Estado inicial (ACTIVA, MANTENIMIENTO, VACACIONES, CERRADA)

2. Al guardar:
```python
def guardar(e):
    with OBTENER_SESION() as sesion:
        nueva = MODELO_SUCURSAL(
            NOMBRE=nombre_field.value,
            DIRECCION=direccion_field.value,
            TELEFONO=telefono_field.value,
            HORARIO=horario_field.value,
            ESTADO=estado_dropdown.value,
            ACTIVA=estado_dropdown.value == "ACTIVA"
        )
        sesion.add(nueva)
        sesion.commit()
    
    # Recarga la lista de sucursales
    self._cargar_sucursales()
    
    # Recarga el dropdown de sucursales en el navbar
    if hasattr(self, '_navbar') and self._navbar:
        self._navbar.recargar_sucursales()
```

### ✏️ Editar Sucursal

**Método**: `_mostrar_overlay_editar(sucursal)` (línea 655-782)

**Flujo**:
1. Pre-llena el formulario con datos actuales
2. Al guardar, actualiza los campos modificados en la BD
3. Recarga la vista y el navbar

### 🔄 Cambiar Estado (Activar/Desactivar)

**Método**: `_mostrar_menu_estado(sucursal)` (línea 782-920)

**Estados disponibles**:
- ✅ **ACTIVA**: Operando normalmente
- 🔧 **MANTENIMIENTO**: En reparación o actualización
- 🏖️ **VACACIONES**: Cerrada temporalmente
- ❌ **CERRADA**: Fuera de servicio

**Flujo**:
```python
def cambiar_estado(nuevo_estado):
    with OBTENER_SESION() as sesion:
        s = sesion.query(MODELO_SUCURSAL).filter_by(ID=sucursal.ID).first()
        s.ESTADO = nuevo_estado
        s.ACTIVA = nuevo_estado == "ACTIVA"  # Flag booleano
        sesion.commit()
    
    # Recarga todo
    self._cargar_sucursales()
    self._navbar.recargar_sucursales()
```

**Importante**: 
- El campo `ACTIVA` es un **booleano** que indica si la sucursal está operativa
- El campo `ESTADO` es un **string** con el estado específico
- Solo `ESTADO="ACTIVA"` hace que `ACTIVA=True`

### 🗑️ Eliminar Sucursal (Cambiar flag a Eliminado)

**Método**: `_confirmar_eliminar(sucursal)` (línea 920-1035)

**⚠️ PROBLEMA ACTUAL**: 
Actualmente se hace **eliminación física** (DELETE), no lógica:

```python
def eliminar(e):
    with OBTENER_SESION() as sesion:
        s = sesion.query(MODELO_SUCURSAL).filter_by(ID=sucursal.ID).first()
        sesion.delete(s)  # ← ELIMINACIÓN FÍSICA
        sesion.commit()
```

**✅ SOLUCIÓN RECOMENDADA**: 
Cambiar a eliminación lógica usando un flag `ELIMINADA`:

```python
def eliminar(e):
    with OBTENER_SESION() as sesion:
        s = sesion.query(MODELO_SUCURSAL).filter_by(ID=sucursal.ID).first()
        s.ELIMINADA = True  # ← FLAG DE ELIMINACIÓN
        s.ACTIVA = False    # Desactivar también
        s.FECHA_ELIMINACION = datetime.now()
        sesion.commit()
```

**Ventajas**:
- ✅ Preserva historial de pedidos/ventas
- ✅ Permite auditoría
- ✅ Recuperación de datos si fue eliminación accidental
- ✅ No rompe relaciones con otras tablas

---

## 👥 Sistema de Roles y Permisos

### Estructura de Roles

**Archivo**: [ConstantesRoles.py](../core/constantes/ConstantesRoles.py)

```python
class ROLES:
    INVITADO = "INVITADO"
    COCINERO = "COCINERO"
    CLIENTE = "CLIENTE"
    ATENCION = "ATENCION"
    MOTORIZADO = "MOTORIZADO"
    ADMIN = "ADMIN"
    LIMPIEZA = "LIMPIEZA"
    SUPERADMIN = "SUPERADMIN"
```

### Permisos Disponibles

**Archivo**: [ConstantesPermisos.py](../core/constantes/ConstantesPermisos.py)

**Permisos de Usuarios**:
- `usuarios.crear`
- `usuarios.editar`
- `usuarios.eliminar`
- `usuarios.ver`
- `usuarios.gestionar_roles`

**Permisos de Roles** (solo SUPERADMIN):
- `roles.crear`
- `roles.editar`
- `roles.eliminar`
- `roles.ver`
- `roles.asignar_permisos`

**Permisos de Sucursales**:
- `sucursales.crear`
- `sucursales.editar`
- `sucursales.eliminar`
- `sucursales.ver`

**Permisos de Productos**:
- `productos.crear`
- `productos.editar`
- `productos.eliminar`
- `productos.ver`

**Permisos de Pedidos**:
- `pedidos.crear`
- `pedidos.ver`
- `pedidos.ver_todos`
- `pedidos.editar`
- `pedidos.confirmar`
- `pedidos.actualizar_estado`

*... y muchos más (95 permisos en total)*

### Obtención de Permisos por Rol

```python
def OBTENER_PERMISOS_ROL(NOMBRE_ROL: str) -> list:
    # SUPERADMIN tiene todos los permisos
    if NOMBRE_ROL == ROLES.SUPERADMIN:
        return ["*"]
    
    # Para otros roles, se obtienen desde la BD
    with OBTENER_SESION() as sesion:
        rol = sesion.query(MODELO_ROL).filter_by(NOMBRE=NOMBRE_ROL).first()
        if rol and rol.PERMISOS:
            return json.loads(rol.PERMISOS)
        return []
```

### Asignación de Roles a Empleados

**Gestión de Usuarios**: [PaginaGestionUsuarios.py](../features/gestion_usuarios/presentation/pages/PaginaGestionUsuarios.py)

#### 1. Crear Usuario con Rol

```python
def _CREAR_USUARIO(self, datos):
    self._bloc.AGREGAR_EVENTO(CrearUsuario(
        nombre_usuario=datos["nombre_usuario"],
        email=datos["email"],
        contrasena=datos["contrasena"],
        nombre_completo=datos["nombre_completo"],
        rol=datos["rol"],  # ← Asignación de rol
        sucursal_id=datos["sucursal_id"],
        activo=datos["activo"]
    ))
```

#### 2. Cambiar Rol de Usuario

```python
def _CAMBIAR_ROL(self, usuario_id, nuevo_rol):
    self._bloc.AGREGAR_EVENTO(
        CambiarRolUsuario(
            usuario_id=usuario_id,
            nuevo_rol=nuevo_rol
        )
    )
```

**Proceso en BD**:
```python
async def ASIGNAR_ROL_A_USUARIO(self, USUARIO_ID: int, NOMBRE_ROL: str):
    with OBTENER_SESION() as sesion:
        USUARIO = sesion.query(MODELO_USUARIO).filter_by(ID=USUARIO_ID).first()
        ROL = sesion.query(MODELO_ROL).filter_by(NOMBRE=NOMBRE_ROL).first()
        
        if USUARIO and ROL:
            if ROL not in USUARIO.ROLES:
                USUARIO.ROLES.append(ROL)  # ← Relación Many-to-Many
                sesion.commit()
```

### Gestión de Permisos de Vistas

**Archivo**: [Usuario.py](../features/autenticacion/domain/entities/Usuario.py)

```python
def OBTENER_PERMISOS(self) -> List[str]:
    PERMISOS_TOTALES = set()
    
    for ROL in self.ROLES:
        if ROL == ROLES.SUPERADMIN:
            return ["*"]  # Todos los permisos
        
        PERMISOS_TOTALES.update(OBTENER_PERMISOS_ROL(ROL))
    
    return list(PERMISOS_TOTALES)

def TIENE_PERMISO(self, PERMISO: str) -> bool:
    permisos = self.OBTENER_PERMISOS()
    return "*" in permisos or PERMISO in permisos

def TIENE_ROL(self, ROL: str) -> bool:
    return ROL in self.ROLES
```

### Control de Acceso a Vistas

**Decorador**: `@REQUIERE_ROL()`

```python
@REQUIERE_ROL(ROLES.ADMIN)
class SucursalesPage(LayoutBase):
    # Solo usuarios con rol ADMIN o SUPERADMIN pueden acceder
    pass

@REQUIERE_ROL(ROLES.SUPERADMIN, ROLES.ADMIN)
class PaginaGestionUsuarios(LayoutBase):
    # Usuarios con SUPERADMIN o ADMIN pueden acceder
    pass
```

### Gestión Avanzada de Roles (Solo SUPERADMIN)

**Archivo**: [RolesPage.py](../features/admin/presentation/pages/gestion/RolesPage.py)

Solo el SUPERADMIN puede:
- ✅ Crear nuevos roles personalizados
- ✅ Editar roles existentes
- ✅ Asignar permisos específicos a roles
- ✅ Eliminar roles (si no están en uso)

**Ejemplo de creación de rol**:
```python
def _CREAR_FORMULARIO(self, item=None):
    permisos_disponibles = [
        "usuarios.crear", "usuarios.editar", "usuarios.eliminar",
        "productos.crear", "productos.editar", "productos.ver",
        "pedidos.crear", "pedidos.ver", "pedidos.confirmar",
        # ... 95 permisos disponibles
    ]
    
    return [
        FormularioCRUD.CREAR_CAMPO("Nombre del Rol", ""),
        FormularioCRUD.CREAR_CAMPO("Descripción", ""),
        ft.Column([
            ft.Checkbox(label=permiso, value=False)
            for permiso in permisos_disponibles
        ])
    ]
```

---

## 🔄 Flujo Completo de Permisos

### 1. Creación de Empleado con Rol y Permisos

```
1. SUPERADMIN/ADMIN → Gestión de Usuarios
2. Crear Nuevo Usuario
3. Asignar Rol (EMPLEADO, ATENCION, COCINERO, etc.)
4. El rol ya tiene permisos pre-configurados
5. El empleado obtiene acceso a vistas según sus permisos
```

### 2. Cambio de Permisos de un Rol

```
1. SUPERADMIN → Gestión de Roles
2. Editar Rol (ej: "ATENCION")
3. Modificar permisos:
   - Agregar: pedidos.confirmar
   - Quitar: productos.editar
4. Guardar cambios
5. TODOS los empleados con rol ATENCION obtienen nuevos permisos
```

### 3. Verificación en Runtime

```python
# En cualquier vista
if usuario.TIENE_PERMISO("sucursales.editar"):
    mostrar_boton_editar()

if usuario.TIENE_ROL(ROLES.ADMIN):
    mostrar_panel_admin()
```

---

## 📊 Diagrama de Flujo: Sucursales

```
Usuario hace click en "Sucursales"
          ↓
Verificar permisos (@REQUIERE_ROL)
          ↓
    ¿Tiene rol ADMIN?
          ↓
    SÍ         NO → Rechazar acceso
          ↓
Inicializar SucursalesPage
          ↓
_CONSTRUIR_UI() → Crear interfaz
          ↓
_cargar_sucursales()
          ↓
Consultar BD: SELECT * FROM sucursales
  WHERE ESTADO = filtro
  ORDER BY FECHA_CREACION DESC
          ↓
Renderizar cards de sucursales
          ↓
Usuario puede:
  - Crear nueva sucursal
  - Editar existente
  - Cambiar estado (ACTIVA/MANTENIMIENTO/etc)
  - Eliminar (actualmente física, debe ser lógica)
```

---

## 🛠️ Mejoras Recomendadas

### 1. Implementar Eliminación Lógica

**Modificar MODELO_SUCURSAL**:
```python
class Sucursal(Base):
    # ... campos existentes ...
    ELIMINADA = Column(Boolean, default=False)
    FECHA_ELIMINACION = Column(DateTime, nullable=True)
    USUARIO_ELIMINO_ID = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
```

**Actualizar método eliminar**:
```python
def eliminar(e):
    with OBTENER_SESION() as sesion:
        s = sesion.query(MODELO_SUCURSAL).filter_by(ID=sucursal.ID).first()
        s.ELIMINADA = True
        s.ACTIVA = False
        s.FECHA_ELIMINACION = datetime.now()
        s.USUARIO_ELIMINO_ID = self._usuario.ID
        sesion.commit()
```

**Actualizar consultas para excluir eliminadas**:
```python
def _cargar_sucursales(self):
    with OBTENER_SESION() as sesion:
        query = sesion.query(MODELO_SUCURSAL).filter_by(ELIMINADA=False)
        # ... resto del código
```

### 2. Agregar Funcionalidad "Restaurar"

Para SUPERADMIN, permitir restaurar sucursales eliminadas:
```python
def _restaurar_sucursal(self, sucursal):
    with OBTENER_SESION() as sesion:
        s = sesion.query(MODELO_SUCURSAL).filter_by(ID=sucursal.ID).first()
        s.ELIMINADA = False
        s.FECHA_ELIMINACION = None
        s.USUARIO_ELIMINO_ID = None
        sesion.commit()
```

### 3. Auditoría de Cambios

Registrar quién y cuándo modificó cada sucursal:
```python
class SucursalAuditoria(Base):
    ID = Column(Integer, primary_key=True)
    SUCURSAL_ID = Column(Integer, ForeignKey("sucursales.id"))
    USUARIO_ID = Column(Integer, ForeignKey("usuarios.id"))
    ACCION = Column(String)  # CREAR, EDITAR, CAMBIAR_ESTADO, ELIMINAR
    VALORES_ANTERIORES = Column(Text)
    VALORES_NUEVOS = Column(Text)
    FECHA = Column(DateTime, default=datetime.now)
```

---

## 📌 Resumen

### Sucursales
- ✅ Carga desde BD con filtros por estado
- ✅ CRUD completo (Crear, Editar, Cambiar Estado)
- ⚠️ Eliminación física (debe cambiarse a lógica)
- ✅ Recarga automática del navbar al modificar
- ✅ UI moderna con diseño card-based

### Roles y Permisos
- ✅ Sistema de 95 permisos granulares
- ✅ Asignación de roles a empleados
- ✅ SUPERADMIN puede crear/editar roles
- ✅ Permisos dinámicos desde BD
- ✅ Control de acceso a vistas con decoradores
- ✅ Verificación de permisos en runtime

### Vistas Protegidas
- Sucursales: `@REQUIERE_ROL(ROLES.ADMIN)`
- Usuarios: `@REQUIERE_ROL(ROLES.SUPERADMIN, ROLES.ADMIN)`
- Roles: `@REQUIERE_ROL(ROLES.SUPERADMIN)`
