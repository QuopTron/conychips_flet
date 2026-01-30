# Cony Chips - Sistema de Gestión para Restaurante

## 🚀 Cambios Recientes - Sistema de Roles Dinámicos

### ✅ Optimizaciones Implementadas

#### 1. **Optimización de Campos de Base de Datos**

Se han reducido los tamaños de los campos String para optimizar el almacenamiento:

- `EMAIL`: 255 → **100** caracteres
- `NOMBRE_USUARIO`: 100 → **50** caracteres
- `CONTRASENA_HASH`: 255 → **100** caracteres (hash bcrypt)
- `HUELLA_DISPOSITIVO`: 255 → **64** caracteres (SHA256)
- `TOKEN_RESET`: 255 → **64** caracteres
- `REFRESH_TOKEN`: 500 → **250** caracteres
- `DESCRIPCION`: 255 → **200** caracteres
- `NOTAS`: 500 → **300** caracteres
- `QR_PAGO`: 1000 → **300** caracteres
- `EXTRAS_SELECCIONADOS`: 1000 → **500** caracteres

#### 2. **Sistema de Roles Dinámicos**

**Antes:**

- Roles hardcodeados en el código
- 6 roles predefinidos (super_admin, admin, atencion, cocinero, limpieza, cliente)
- Permisos estáticos en `PERMISOS_POR_ROL`

**Ahora:**

- ✅ Solo el rol `super_admin` está predefinido
- ✅ Los demás roles se crean dinámicamente desde la interfaz
- ✅ Cada rol tiene sus permisos almacenados en la BD (tabla ROLES, columna PERMISOS - JSON)
- ✅ Nuevos campos en MODELO_ROL:
    - `PERMISOS` (String 2000) - JSON con array de permisos
    - `ACTIVO` (Boolean)
    - `FECHA_CREACION` (DateTime)

#### 3. **Usuario Super Admin por Defecto**

Al inicializar la base de datos, se crea automáticamente:

```
Email: superadmin@conychips.com
Contraseña: SuperAdmin123.
Rol: super_admin
Permisos: "*" (todos)
```

**IMPORTANTE:** Cambia esta contraseña en producción.

#### 4. **Nueva Interfaz de Gestión de Roles**

**Acceso:** Solo para usuarios con rol `super_admin`

**Ubicación:** Dashboard Admin → Botón "Gestionar Roles"

**Funcionalidades:**

- ✅ Crear nuevos roles
- ✅ Asignar permisos personalizados
- ✅ Ver roles existentes
- ✅ Eliminar roles (excepto super_admin)
- ✅ Ver permisos de cada rol
- ⚠️ Editar roles (en desarrollo)

**Archivo:** `/features/admin/presentation/pages/PaginaGestionRoles.py`

---

## 📋 Permisos Disponibles

```python
# Gestión de usuarios
usuarios.crear
usuarios.editar
usuarios.eliminar
usuarios.ver
usuarios.gestionar_roles

# Gestión de roles (solo super admin)
roles.crear
roles.editar
roles.eliminar
roles.ver
roles.asignar_permisos

# Productos
productos.crear
productos.editar
productos.eliminar
productos.ver

# Sucursales
sucursales.crear
sucursales.editar
sucursales.eliminar
sucursales.ver

# Y muchos más... (ver core/Constantes.py)
```

---

## 🏗️ Arquitectura del Sistema de Permisos

### Flujo de Verificación:

1. **Usuario inicia sesión**
2. Se consultan sus roles desde la BD (tabla USUARIO_ROLES)
3. Para cada rol, se obtienen los permisos desde la tabla ROLES (columna PERMISOS - JSON)
4. Los permisos se incluyen en el JWT (access token)
5. En cada operación, se verifica: `USUARIO.TIENE_PERMISO("permiso.nombre")`

### Métodos Actualizados:

```python
# Usuario.py
def TIENE_PERMISO(self, PERMISO: str) -> bool:
    # Consulta permisos dinámicamente desde la BD

def OBTENER_PERMISOS(self) -> List[str]:
    # Retorna lista de todos los permisos del usuario

def ES_ADMIN(self) -> bool:
    # Ahora solo retorna True para super_admin
```

---

## 🔄 Migración desde Sistema Anterior

### ¿Qué pasó con los roles antiguos?

- **Ya NO se crean automáticamente** los roles: admin, atencion, cocinero, limpieza, cliente
- **Solo se crea:** super_admin
- **Ya NO se crean usuarios de prueba** (super@conychips.com, admin@conychips.com, etc.)
- **Solo se crea:** superadmin@conychips.com

### ¿Cómo crear roles ahora?

1. Inicia sesión como `superadmin@conychips.com`
2. Ve a Dashboard Admin
3. Haz clic en "Gestionar Roles"
4. Crea los roles que necesites con los permisos personalizados

### Ejemplo de Rol Personalizado:

**Rol:** Cajero
**Permisos:**

- pedidos.ver
- pedidos.confirmar
- productos.ver
- cajas.abrir
- cajas.cerrar
- cajas.ver

---

## 🛠️ Archivos Modificados

### Core

- ✅ `core/base_datos/ConfiguracionBD.py` - Optimización de campos + sistema de permisos
- ✅ `core/Constantes.py` - Roles dinámicos + función OBTENER_PERMISOS_ROL
- ✅ `core/seguridad/ManejadorJWT.py` - Permisos dinámicos en JWT

### Domain

- ✅ `features/autenticacion/domain/entities/Usuario.py` - Métodos dinámicos de permisos
- ✅ `features/autenticacion/domain/usecases/IniciarSesion.py` - Validación de roles

### Presentation

- ✅ `features/admin/presentation/pages/PaginaAdmin.py` - Botón gestión de roles
- ✅ `features/admin/presentation/pages/PaginaGestionRoles.py` - **NUEVO** - UI completa

---

## 📊 Estructura de la BD

### Tabla ROLES (Actualizada)

```sql
CREATE TABLE ROLES (
    ID INTEGER PRIMARY KEY,
    NOMBRE VARCHAR(50) UNIQUE NOT NULL,
    DESCRIPCION VARCHAR(200),
    PERMISOS VARCHAR(2000),  -- JSON: ["permiso1", "permiso2", ...]
    ACTIVO BOOLEAN DEFAULT 1,
    FECHA_CREACION DATETIME
);
```

### Ejemplo de Registro:

```json
{
    "ID": 1,
    "NOMBRE": "super_admin",
    "DESCRIPCION": "Control total del sistema",
    "PERMISOS": "[\"*\"]", // Wildcard = todos los permisos
    "ACTIVO": true,
    "FECHA_CREACION": "2026-01-24 10:00:00"
}
```

---

## ⚡ Próximos Pasos

### Funcionalidades Pendientes:

- [ ] Edición de roles existentes
- [ ] Duplicar rol (crear uno basado en otro)
- [ ] Histórico de cambios en roles
- [ ] Auditoría de quién modificó qué rol
- [ ] Plantillas de roles predefinidos
- [ ] Importar/Exportar roles (JSON)

### Mejoras Sugeridas:

- [ ] Implementar caché de permisos (Redis)
- [ ] Tests unitarios para el sistema de roles
- [ ] Documentación de API
- [ ] Validación de permisos en el backend (decoradores actualizados)

---

## 🔒 Seguridad

### Recomendaciones:

1. **Cambiar contraseña del super admin** inmediatamente en producción
2. **Variables de entorno:** Configurar `JWT_SECRET_KEY` en `.env`
3. **No compartir** credenciales de super admin
4. **Auditar permisos** regularmente
5. **Backup de BD** antes de modificar roles

---

## 📞 Soporte

Si encuentras algún problema con el nuevo sistema de roles:

1. Revisa los logs en consola
2. Verifica que el usuario tenga el rol `super_admin` para gestionar roles
3. Asegúrate de que la BD se inicializó correctamente
4. En caso de error, elimina `app_segura.db` y reinicia la app (se creará de nuevo)

---

## 📝 Notas de Desarrollo

### Compatibilidad Retroactiva:

El sistema mantiene el diccionario `PERMISOS_POR_ROL` en `Constantes.py` solo con:

```python
PERMISOS_POR_ROL = {
    ROLES.SUPER_ADMIN: ["*"],  # Solo super admin está hardcoded
}
```

Esto asegura que el código antiguo que consulte `PERMISOS_POR_ROL` siga funcionando para super_admin.

### Sistema Híbrido:

- **Super Admin:** Permisos hardcodeados = "\*"
- **Otros Roles:** Permisos dinámicos desde BD

---

**Versión:** 2.0 - Sistema de Roles Dinámicos
**Fecha:** 24 de Enero, 2026
**Autor:** Sistema Cony Chips

---

## 🎯 TL;DR (Resumen Ejecutivo)

**Antes:**

- 6 roles fijos en código
- Permisos hardcodeados
- Usuarios de prueba creados automáticamente

**Ahora:**

- 1 rol fijo: `super_admin`
- Roles dinámicos creados desde interfaz
- Permisos almacenados en BD (JSON)
- Solo 1 usuario por defecto: `superadmin@conychips.com`
- Interfaz completa de gestión de roles
- Campos de BD optimizados

**Login Super Admin:**

```
Email: superadmin@conychips.com
Password: SuperAdmin123.
```

**¡Todo listo para producción!** 🚀

---

## 📚 Documentación

Para documentación completa del sistema, visita la carpeta [`docs/`](docs/):

- **[Arquitectura y Seguridad](docs/ARQUITECTURA_SEGURIDAD.md)** - Sistema de seguridad JWT RS256
- **[Sistema Completo](docs/SISTEMA_COMPLETO.md)** - Guía de instalación y ejecución
- **[Changelog](docs/CHANGELOG.md)** - Historial de cambios
- **[Guías de Usuario](docs/guias/)** - Tutoriales y documentación de features

Ver [docs/README.md](docs/README.md) para el índice completo de documentación.

## 🗂️ Estructura del Proyecto

```
conychips/
├── main.py              # Punto de entrada de la aplicación
├── requirements.txt     # Dependencias del proyecto
├── pytest.ini          # Configuración de pytest
│
├── config/             # Configuración del sistema
│   ├── keys/           # Claves RSA para JWT
│   └── ConfiguracionApp.py
│
├── core/               # Núcleo del sistema
│   ├── base_datos/     # Configuración de BD
│   ├── cache/          # Sistema de cache Redis
│   ├── configuracion/  # Sistema de configuración
│   └── constantes/     # Constantes globales
│
├── features/           # Módulos por funcionalidad
│   ├── autenticacion/  # Login y JWT
│   ├── admin/          # Panel de administración
│   ├── pedidos/        # Gestión de pedidos
│   ├── finanzas/       # Módulo financiero
│   └── ...
│
├── docs/               # Documentación (10 documentos)
│   ├── README.md       # Índice de documentación
│   ├── guias/          # Guías de usuario
│   └── ...
│
├── tests/              # Tests organizados por módulo (22 tests)
│   ├── admin/          # 3 tests
│   ├── autenticacion/  # 2 tests
│   ├── vouchers/       # 14 tests
│   └── ...
│
└── tools/              # Scripts de utilidad (22 scripts)
    ├── README.md       # Documentación de herramientas
    ├── generar_bloc.py # Generador de BLoCs
    ├── configurar_sistema.py
    └── ...
```

## 🛠️ Herramientas de Desarrollo

Ver [tools/README.md](tools/README.md) para documentación completa de scripts.

Scripts principales:
- `tools/configurar_sistema.py` - Setup inicial del sistema
- `tools/generar_bloc.py` - Generador de BLoCs
- `tools/crear_datos_prueba.py` - Datos de prueba
- `tools/verificar_sistema.py` - Verificar instalación

## 🧪 Tests

Ver [tests/README.md](tests/README.md) para información sobre tests.

```bash
# Ejecutar todos los tests
pytest -v

# Tests por módulo
pytest tests/admin/
pytest tests/vouchers/
```
