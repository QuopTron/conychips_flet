# 🧪 Sistema de Testing y Benchmarking

## 📋 Descripción

Sistema unificado de testing con 3 categorías de pruebas:
- **White Box**: Pruebas de caja blanca (estructura interna)
- **Black Box**: Pruebas de caja negra (comportamiento externo)
- **Benchmark**: Medición de performance

## 🚀 Inicio Rápido

```bash
# Ejecutar TODOS los tests
./run_tests.sh all

# Solo white box
./run_tests.sh whitebox

# Solo black box
./run_tests.sh blackbox

# Solo benchmarks
./run_tests.sh benchmark

# Coverage completo
./run_tests.sh coverage
```

## 📂 Estructura

```
tests/
├── whitebox/              # Pruebas de caja blanca
│   └── test_layout_base.py
├── blackbox/              # Pruebas de caja negra
│   └── test_layout_integration.py
├── benchmark/             # Benchmarks de performance
│   └── benchmark_navigation.py
└── reports/               # Reportes generados
    ├── whitebox-report.html
    ├── blackbox-report.html
    └── coverage/
```

## 🎯 Tipos de Pruebas

### White Box (Caja Blanca)
Conocen la implementación interna. Prueban:
- Herencia correcta de clases
- Atributos privados inicializados
- Métodos internos funcionando
- Estructura de código

**Ejemplo:**
```python
def test_herencia_correcta(self):
    """Verifica que LayoutBase hereda de ft.Column"""
    assert issubclass(LayoutBase, ft.Column)
```

### Black Box (Caja Negra)
No conocen implementación. Prueban:
- Comportamiento externo
- Entrada/Salida
- Integración entre componentes
- Casos extremos

**Ejemplo:**
```python
def test_construccion_basica(self):
    """Verifica que se puede construir LayoutBase"""
    layout = LayoutBase(pagina=page, usuario=usuario)
    assert layout is not None
```

### Benchmark (Performance)
Miden tiempos de ejecución:
- Creación de componentes
- Renderizado
- Operaciones complejas
- Comparación entre versiones

**Ejemplo:**
```python
def benchmark_layout_creation(self, iterations=100):
    start = time.perf_counter()
    for _ in range(iterations):
        layout = LayoutBase(...)
    end = time.perf_counter()
    return (end - start) / iterations * 1000  # ms
```

## 📊 Comandos Disponibles

### Ejecutar Tests

```bash
# Todos los tests
./run_tests.sh all

# White box solamente
./run_tests.sh whitebox

# Black box solamente
./run_tests.sh blackbox

# Benchmarks
./run_tests.sh benchmark
```

### Utilidades

```bash
# Limpiar reportes anteriores
./run_tests.sh clean

# Ver reportes disponibles
./run_tests.sh reports

# Análisis de cobertura
./run_tests.sh coverage

# Ayuda
./run_tests.sh help
```

### Prueba Rápida de Flujo

```bash
# Ejecuta prueba simple de imports y creación
python test_flujo_rapido.py
```

### Prueba de App Completa

```bash
# Inicia app y captura logs
./test_app.sh

# Ver logs en vivo
tail -f app_test_output.log

# Buscar errores
grep -i error app_test_output.log
```

## 📈 Benchmarking

### Ejecutar Benchmark

```bash
./run_tests.sh benchmark
```

### Salida Esperada

```
╔════════════════════════════════════════════════════════╗
║      🔥 BENCHMARK - Sistema de Navegación              ║
╚════════════════════════════════════════════════════════╝

Iteraciones por test: 100

✓ LayoutBase Creation:        2.3450 ms/op
✓ construir() Method:          3.1230 ms/op
✓ NavbarGlobal Creation:       1.8970 ms/op
✓ BottomNavigation Creation:   2.5601 ms/op

╔════════════════════════════════════════════════════════╗
║ Total tiempo: 978.51 ms                                ║
╚════════════════════════════════════════════════════════╝
```

### Comparar Versiones

```python
from tests.benchmark.benchmark_navigation import NavigationBenchmark

bench = NavigationBenchmark()

# Resultados v1.0
results_v1 = bench.run_all_benchmarks(iterations=50)

# ... hacer cambios ...

# Resultados v1.1
results_v2 = bench.run_all_benchmarks(iterations=50)

# Comparar
bench.compare_versions(results_v1, results_v2)
```

## 🔍 Coverage

### Ejecutar Análisis

```bash
./run_tests.sh coverage
```

### Ver Reporte HTML

```bash
# Se genera en htmlcov/index.html
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # macOS
```

### Interpretar Resultados

- **Verde**: Código ejecutado (cubierto)
- **Rojo**: Código no ejecutado (sin cobertura)
- **Meta**: >80% de cobertura

## 📝 Escribir Nuevas Pruebas

### White Box Test

```python
# tests/whitebox/test_mi_componente.py
import pytest
from features.mi_modulo.MiClase import MiClase

class TestMiClaseWhiteBox:
    def test_atributo_privado(self):
        """Verifica que _atributo existe"""
        obj = MiClase()
        assert hasattr(obj, '_atributo')
```

### Black Box Test

```python
# tests/blackbox/test_mi_integracion.py
import pytest
from features.mi_modulo.MiClase import MiClase

class TestMiClaseBlackBox:
    def test_comportamiento_esperado(self):
        """Verifica salida correcta"""
        obj = MiClase()
        resultado = obj.hacer_algo(input="test")
        assert resultado == "esperado"
```

### Benchmark

```python
# tests/benchmark/benchmark_mi_modulo.py
import time
from features.mi_modulo.MiClase import MiClase

class MiBenchmark:
    def benchmark_operacion(self, iterations=100):
        start = time.perf_counter()
        for _ in range(iterations):
            MiClase().operacion_pesada()
        end = time.perf_counter()
        
        return (end - start) / iterations * 1000  # ms
```

## 🐛 Debugging

### Ver Logs de Tests

```bash
# Tests con output detallado
pytest tests/whitebox/ -v -s

# Solo tests que fallan
pytest tests/ --tb=short --maxfail=1

# Tests específicos
pytest tests/whitebox/test_layout_base.py::TestLayoutBaseWhiteBox::test_herencia_correcta -v
```

### Modo Interactivo

```bash
# Entrar en debugger al fallar
pytest --pdb

# Usar breakpoint en código
def test_algo():
    obj = MiClase()
    breakpoint()  # Se detiene aquí
    assert obj.valor == 5
```

## 📚 Mejores Prácticas

### Naming

- **White Box**: `test_atributo_privado`, `test_metodo_interno`
- **Black Box**: `test_comportamiento_esperado`, `test_caso_extremo`
- **Benchmark**: `benchmark_operacion_compleja`

### Organización

```python
class TestMiClase:
    """Grupo de tests para MiClase"""
    
    def test_caso_1(self):
        """Descripción clara del caso"""
        # Arrange
        obj = MiClase()
        
        # Act
        resultado = obj.hacer()
        
        # Assert
        assert resultado == esperado
```

### Fixtures

```python
import pytest

@pytest.fixture
def usuario_admin():
    """Usuario de prueba con rol admin"""
    return Usuario(ID=1, EMAIL="admin@test.com", ROLES=["ADMIN"])

def test_con_fixture(usuario_admin):
    assert usuario_admin.TIENE_ROL("ADMIN")
```

## 📊 CI/CD Integration

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install Dependencies
        run: pip install -r requirements-test.txt
      - name: Run Tests
        run: ./run_tests.sh all
      - name: Upload Coverage
        uses: codecov/codecov-action@v2
```

## 🎯 Objetivos de Calidad

- ✅ Cobertura de código > 80%
- ✅ Todos los tests pasando
- ✅ Performance estable entre versiones
- ✅ Sin regresiones detectadas

## 📞 Soporte

Para problemas o preguntas:
1. Ver logs: `cat app_test_output.log`
2. Ejecutar prueba rápida: `python test_flujo_rapido.py`
3. Verificar coverage: `./run_tests.sh coverage`

---

**Última actualización:** 28 Enero 2026
**Versión:** 1.0.0
