# Tests del Sistema Cony Chips

Este directorio contiene tests automatizados organizados por módulos.

## Estructura

```
tests/
├── admin/           # Tests del módulo de administración
├── autenticacion/   # Tests de login y autenticación
├── configuracion/   # Tests de sistema de configuración
├── finanzas/        # Tests del módulo financiero
├── pedidos/         # Tests de gestión de pedidos
├── vouchers/        # Tests de vouchers y validación
├── conftest.py      # Configuración de pytest
└── requirements-dev.txt
```

## Requisitos

```bash
pip install -r requirements-dev.txt
```

## Ejecutar las pruebas

```bash
# Todos los tests
pytest -v

# Tests de un módulo específico
pytest tests/admin/
pytest tests/vouchers/
pytest tests/finanzas/

# Test específico
pytest tests/admin/test_admin_dashboard.py -v

# Con cobertura
pytest --cov=features --cov-report=html
```

## Notas de desarrollo

- Las pruebas white-box usan una `FakePage` ligera y previenen llamadas de fondo a
  `asyncio.create_task` durante la importación para evitar errores en entornos de CI.
- El test black-box depende de `tools/test_admin_pages.py`. Si no existe, el test
  se marcará como skip.
