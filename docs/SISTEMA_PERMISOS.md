# Sistema de Permisos por Rol

## 🔐 Jerarquía de Roles

### 1. SUPERADMIN (superadmin@conychips.com)
**Acceso Total al Sistema**

✅ **Permisos Completos:**
- ✅ Gestionar Roles (crear, editar, eliminar roles)
- ✅ Gestionar Sucursales (todas las sucursales)
- ✅ Gestión de Usuarios (crear, editar, activar/desactivar TODOS los usuarios)
- ✅ Cambiar Roles de cualquier usuario
- ✅ Resetear contraseñas de cualquier usuario
- ✅ Auditoría completa (ver todos los logs del sistema)
- ✅ Gestionar Productos
- ✅ Gestión de Pedidos
- ✅ Validar Vouchers
- ✅ Finanzas y Control
- ✅ Insumos y Proveedores
- ✅ Extras, Ofertas, Horarios
- ✅ Caja y Reseñas
- ✅ Filtrar datos por sucursal (dropdown selector)
- ✅ Ver estadísticas globales

**Restricciones:** Ninguna

---

### 2. ADMIN
**Administrador con permisos limitados a su sucursal**

✅ **Permisos:**
- ✅ Gestión de Usuarios (solo de su sucursal y roles menores)
  - ⚠️ NO puede editar SUPERADMIN ni otros ADMIN
  - ⚠️ NO puede cambiar roles
- ✅ Gestionar Productos
- ✅ Gestión de Pedidos
- ✅ Validar Vouchers
- ✅ Finanzas y Control (solo su sucursal)
- ✅ Insumos y Proveedores
- ✅ Extras, Ofertas, Horarios
- ✅ Caja y Reseñas
- ✅ Ver estadísticas de su sucursal

❌ **Sin Acceso:**
- ❌ Gestionar Roles
- ❌ Gestionar Sucursales
- ❌ Auditoría (logs del sistema)
- ❌ Cambiar roles de usuarios
- ❌ Editar usuarios SUPERADMIN o ADMIN
- ❌ Ver datos de otras sucursales

---

### 3. COCINERO
**Personal de cocina**

✅ **Permisos:**
- ✅ Ver pedidos asignados
- ✅ Marcar pedidos como "En Preparación"
- ✅ Marcar pedidos como "Listos"
- ✅ Ver inventario de insumos

❌ **Sin Acceso:**
- ❌ Gestión de usuarios
- ❌ Finanzas
- ❌ Configuraciones del sistema
- ❌ Validar vouchers

---

### 4. ATENCION
**Personal de atención al cliente**

✅ **Permisos:**
- ✅ Tomar pedidos
- ✅ Ver estado de pedidos
- ✅ Registrar clientes
- ✅ Aplicar ofertas y extras

❌ **Sin Acceso:**
- ❌ Gestión de usuarios
- ❌ Finanzas
- ❌ Inventario completo
- ❌ Validar vouchers

---

### 5. MOTORIZADO
**Personal de delivery**

✅ **Permisos:**
- ✅ Ver pedidos asignados
- ✅ Marcar pedidos "En Camino"
- ✅ Marcar pedidos "Entregados"
- ✅ Ver direcciones de entrega

❌ **Sin Acceso:**
- ❌ Gestión de pedidos de otros
- ❌ Finanzas
- ❌ Inventario
- ❌ Configuraciones

---

### 6. LIMPIEZA
**Personal de limpieza**

✅ **Permisos:**
- ✅ Registrar actividades de limpieza
- ✅ Ver horarios asignados

❌ **Sin Acceso:**
- ❌ Pedidos
- ❌ Finanzas
- ❌ Gestión de usuarios
- ❌ Configuraciones

---

### 7. CLIENTE
**Usuario final de la aplicación**

✅ **Permisos:**
- ✅ Hacer pedidos
- ✅ Ver historial de pedidos
- ✅ Dejar reseñas
- ✅ Actualizar perfil

❌ **Sin Acceso:**
- ❌ Acceso al dashboard administrativo
- ❌ Ver otros clientes
- ❌ Gestión del sistema

---

## 📊 Matriz de Permisos

| Función                  | SUPERADMIN | ADMIN | COCINERO | ATENCION | MOTORIZADO | LIMPIEZA | CLIENTE |
|--------------------------|------------|-------|----------|----------|------------|----------|---------|
| Gestionar Roles          | ✅         | ❌    | ❌       | ❌       | ❌         | ❌       | ❌      |
| Gestionar Sucursales     | ✅         | ❌    | ❌       | ❌       | ❌         | ❌       | ❌      |
| Gestión Usuarios (Todos) | ✅         | ❌    | ❌       | ❌       | ❌         | ❌       | ❌      |
| Gestión Usuarios (Sucursal)| ✅       | ✅    | ❌       | ❌       | ❌         | ❌       | ❌      |
| Cambiar Roles            | ✅         | ❌    | ❌       | ❌       | ❌         | ❌       | ❌      |
| Auditoría (Logs)         | ✅         | ❌    | ❌       | ❌       | ❌         | ❌       | ❌      |
| Filtro Sucursales        | ✅         | ✅    | ❌       | ❌       | ❌         | ❌       | ❌      |
| Gestionar Productos      | ✅         | ✅    | ❌       | ❌       | ❌         | ❌       | ❌      |
| Gestión Pedidos          | ✅         | ✅    | ✅       | ✅       | ✅         | ❌       | ❌      |
| Validar Vouchers         | ✅         | ✅    | ❌       | ❌       | ❌         | ❌       | ❌      |
| Finanzas                 | ✅         | ✅    | ❌       | ❌       | ❌         | ❌       | ❌      |
| Caja                     | ✅         | ✅    | ❌       | ❌       | ❌         | ❌       | ❌      |
| Hacer Pedidos            | ✅         | ✅    | ❌       | ✅       | ❌         | ❌       | ✅      |

---

## 🔒 Implementación de Seguridad

### A nivel de Página (Decoradores)
```python
@REQUIERE_ROL(ROLES.SUPERADMIN)
class AuditoriaPage(ft.Column):
    # Solo SUPERADMIN puede acceder
```

### A nivel de Función (Decoradores UI)
```python
@requiere_rol_ui(ROLES.SUPERADMIN, ROLES.ADMIN)
def _VALIDAR_VOUCHER(self, e):
    # Solo SUPERADMIN y ADMIN pueden ejecutar
```

### A nivel de Datos (Repositorio)
```python
# Admin solo ve usuarios de su sucursal
if usuario.ROL == "ADMIN":
    query = query.filter(MODELO_USUARIO.SUCURSAL_ID == usuario.SUCURSAL_ID)
```

### Auditoría Automática
Todas las acciones críticas se registran en `MODELO_AUDITORIA`:
- Creación de usuarios
- Cambio de roles
- Modificación de permisos
- Validación de vouchers
- Cambios en finanzas

---

## 📝 Notas Importantes

1. **SUPERADMIN es intocable**: Solo puede haber un SUPERADMIN principal (superadmin@conychips.com)
2. **ADMIN limitado**: No puede modificar otros administradores para evitar conflictos
3. **Auditoría protegida**: Solo SUPERADMIN ve los logs completos del sistema
4. **Filtro automático**: ADMIN solo ve datos de su sucursal automáticamente
5. **Jerarquía estricta**: Un rol no puede modificar roles superiores o iguales
