#!/bin/bash
#
# Script de inicio para Cony Chips
# Sistema completo con PostgreSQL + Redis + JWT RS256
#

clear
echo "============================================"
echo "   CONY CHIPS - Sistema de Gestión"
echo "============================================"
echo ""
echo "📦 Versiones del sistema:"
echo "  - Python: 3.12.7"
echo "  - Flet: 0.80.3"
echo "  - PostgreSQL: 18.1"
echo "  - Redis: 7.2.4"
echo "  - SQLAlchemy: 2.0.46"
echo ""
echo "🔒 Credenciales de acceso:"
echo "  Email: superadmin@conychips.com"
echo "  Password: SuperAdmin123."
echo ""
echo "============================================"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    echo "❌ Error: Debes ejecutar este script desde /mnt/flox/conychips"
    exit 1
fi

# Activar entorno virtual
if [ ! -d "venv" ]; then
    echo "❌ Error: Entorno virtual no encontrado"
    echo "   Ejecuta: python -m venv venv"
    exit 1
fi

source venv/bin/activate

# Verificar servicios
echo "🔍 Verificando servicios..."
echo ""

# PostgreSQL
if systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL: Running"
else
    echo "⚠️  PostgreSQL: No está ejecutándose"
    echo "   Inicia con: sudo systemctl start postgresql"
fi

# Redis
if systemctl is-active --quiet redis; then
    echo "✅ Redis: Running"
else
    echo "⚠️  Redis: No está ejecutándose"
    echo "   Inicia con: sudo systemctl start redis"
fi

echo ""
echo "============================================"
echo "🚀 Iniciando aplicación..."
echo "============================================"
echo ""

# Ejecutar la aplicación
python main.py
