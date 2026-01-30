#!/bin/bash
# Sistema de Testing Unificado - Cony Chips
# Ejecuta white box, black box, o benchmarks

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      🧪 Sistema de Testing Unificado v1.0         ║${NC}"
echo -e "${BLUE}║         Cony Chips - Quality Assurance            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Directorio raíz
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activar entorno virtual
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo -e "${RED}✗ Error: No se encontró el entorno virtual${NC}"
    exit 1
fi

# Función: Ejecutar tests white box
run_whitebox() {
    echo -e "${YELLOW}📦 Ejecutando White Box Tests...${NC}"
    echo -e "${YELLOW}   (Pruebas de caja blanca - estructura interna)${NC}\n"
    
    pytest tests/whitebox/ -v --tb=short --color=yes \
        --junit-xml=tests/reports/whitebox-results.xml \
        --html=tests/reports/whitebox-report.html \
        --self-contained-html
    
    echo -e "\n${GREEN}✓ White Box Tests completados${NC}\n"
}

# Función: Ejecutar tests black box
run_blackbox() {
    echo -e "${YELLOW}🎯 Ejecutando Black Box Tests...${NC}"
    echo -e "${YELLOW}   (Pruebas de caja negra - comportamiento externo)${NC}\n"
    
    pytest tests/blackbox/ -v --tb=short --color=yes \
        --junit-xml=tests/reports/blackbox-results.xml \
        --html=tests/reports/blackbox-report.html \
        --self-contained-html
    
    echo -e "\n${GREEN}✓ Black Box Tests completados${NC}\n"
}

# Función: Ejecutar benchmarks
run_benchmark() {
    echo -e "${YELLOW}🔥 Ejecutando Benchmarks...${NC}"
    echo -e "${YELLOW}   (Medición de performance)${NC}\n"
    
    python tests/benchmark/benchmark_navigation.py
    
    echo -e "\n${GREEN}✓ Benchmarks completados${NC}\n"
}

# Función: Ejecutar todos los tests
run_all() {
    echo -e "${BLUE}🚀 Ejecutando TODOS los tests...${NC}\n"
    
    run_whitebox
    run_blackbox
    run_benchmark
    
    echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           ✓ TODOS LOS TESTS COMPLETADOS           ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
}

# Función: Limpiar reportes anteriores
clean_reports() {
    echo -e "${YELLOW}🧹 Limpiando reportes anteriores...${NC}"
    rm -rf tests/reports/*.xml tests/reports/*.html
    mkdir -p tests/reports
    echo -e "${GREEN}✓ Reportes limpiados${NC}\n"
}

# Función: Ver reportes
view_reports() {
    echo -e "${BLUE}📊 Reportes disponibles:${NC}\n"
    
    if [ -f "tests/reports/whitebox-report.html" ]; then
        echo -e "${GREEN}✓ White Box: tests/reports/whitebox-report.html${NC}"
    fi
    
    if [ -f "tests/reports/blackbox-report.html" ]; then
        echo -e "${GREEN}✓ Black Box: tests/reports/blackbox-report.html${NC}"
    fi
    
    echo ""
}

# Función: Coverage
run_coverage() {
    echo -e "${YELLOW}📈 Ejecutando análisis de cobertura...${NC}\n"
    
    pytest tests/ --cov=features --cov-report=html --cov-report=term
    
    echo -e "\n${GREEN}✓ Coverage report: htmlcov/index.html${NC}\n"
}

# Función: Ayuda
show_help() {
    echo -e "${BLUE}Uso:${NC} $0 [opción]"
    echo ""
    echo -e "${YELLOW}Opciones:${NC}"
    echo "  whitebox       Ejecutar solo White Box tests"
    echo "  blackbox       Ejecutar solo Black Box tests"
    echo "  benchmark      Ejecutar solo Benchmarks"
    echo "  all            Ejecutar todos los tests (por defecto)"
    echo "  clean          Limpiar reportes anteriores"
    echo "  reports        Ver reportes disponibles"
    echo "  coverage       Análisis de cobertura de código"
    echo "  help           Mostrar esta ayuda"
    echo ""
    echo -e "${YELLOW}Ejemplos:${NC}"
    echo "  $0 whitebox    # Solo pruebas de caja blanca"
    echo "  $0 all         # Todos los tests"
    echo "  $0 benchmark   # Solo benchmarks de performance"
    echo ""
}

# Crear directorio de reportes si no existe
mkdir -p tests/reports tests/whitebox tests/blackbox tests/benchmark

# Procesar argumentos
case "${1:-all}" in
    whitebox)
        run_whitebox
        ;;
    blackbox)
        run_blackbox
        ;;
    benchmark)
        run_benchmark
        ;;
    all)
        run_all
        ;;
    clean)
        clean_reports
        ;;
    reports)
        view_reports
        ;;
    coverage)
        run_coverage
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}✗ Opción desconocida: $1${NC}"
        show_help
        exit 1
        ;;
esac
