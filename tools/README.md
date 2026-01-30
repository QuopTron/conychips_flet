# 🛠️ Herramientas de Desarrollo - Cony Chips

Scripts de utilidad para desarrollo, mantenimiento y administración del sistema.

## 📦 Scripts Principales

### Configuración y Setup

- **`configurar_sistema.py`** - Configuración inicial del sistema (PostgreSQL, Redis, claves JWT)
- **`generar_claves_jwt.py`** - Genera claves RSA para JWT RS256
- **`migrar_bd.py`** - Migración completa de base de datos
- **`migrar_nuevas_tablas.py`** - Migración incremental de nuevas tablas

### Datos de Prueba

- **`crear_datos_prueba.py`** - Genera datos de prueba generales
- **`crear_datos_finanzas.py`** - Genera datos específicos del módulo de finanzas
- **`format_users_db.py`** - Formatea usuarios en la base de datos
- **`remove_all_users.py`** - Elimina todos los usuarios (excepto super admin)

### Generadores de Código

- **`generar_bloc.py`** - Generador automático de BLoCs con patrón Clean Architecture
  ```bash
  python tools/generar_bloc.py NombreEntidad
  ```

### Mantenimiento de Código

- **`fix_datetime_utcnow.py`** - Corrige uso deprecado de `datetime.utcnow()`
- **`fix_deprecations.py`** - Corrige deprecaciones en el código
- **`corregir_sintaxis_flet.py`** - Corrige sintaxis de Flet 0.80.3
- **`corregir_sintaxis_flet_completa.py`** - Corrección completa de sintaxis Flet
- **`replace_elevated_with_button.py`** - Reemplaza ElevatedButton deprecado

### Limpieza y Análisis

- **`clean_all_comments.py`** - Elimina comentarios del código
- **`clean_comments_docstrings.py`** - Limpia comentarios y docstrings
- **`detectar_patrones_complejos.py`** - Detecta patrones complejos en el código
- **`flet_inspector.py`** - Inspector de componentes Flet

### Correcciones Específicas

- **`corregir_colors_mayuscula.py`** - Corrige uso de colors con mayúscula
- **`corregir_duplicacion_icons.py`** - Corrige duplicación en imports de icons

### Verificación

- **`verificar_sistema.py`** - Verifica que el sistema esté correctamente configurado
- **`test_admin_pages.py`** - Test harness para páginas de admin

## 🚀 Uso Común

### Primera Instalación

```bash
# 1. Generar claves JWT
python tools/generar_claves_jwt.py

# 2. Configurar sistema (PostgreSQL + Redis)
python tools/configurar_sistema.py

# 3. Migrar base de datos
python tools/migrar_bd.py

# 4. Crear datos de prueba
python tools/crear_datos_prueba.py
python tools/crear_datos_finanzas.py

# 5. Verificar instalación
python tools/verificar_sistema.py
```

### Desarrollo

```bash
# Generar nuevo BLoC
python tools/generar_bloc.py Productos

# Verificar sistema
python tools/verificar_sistema.py
```

## 📝 Notas

- La mayoría de scripts requieren que el entorno virtual esté activado
- Algunos scripts modifican la base de datos, usar con precaución
- Los scripts de corrección modifican archivos del proyecto

---

**Última actualización**: Enero 2026
