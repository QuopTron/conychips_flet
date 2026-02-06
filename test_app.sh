#!/bin/bash
# Script de prueba completa del sistema
# Ejecuta la aplicación y captura logs para debugging

cd /mnt/flox/conychips

echo "╔════════════════════════════════════════════════════════╗"
echo "║     🔍 PRUEBA DE FLUJO COMPLETO - Cony Chips          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Matar procesos previos
echo "🧹 Limpiando procesos anteriores..."
pkill -f "python.*main.py" 2>/dev/null
sleep 1

# Activar venv
echo "🐍 Activando entorno virtual..."
source venv/bin/activate

# Ejecutar app en background
echo "🚀 Iniciando aplicación..."
echo ""
python main.py > app_test_output.log 2>&1 &
APP_PID=$!

# Esperar inicio
echo "⏳ Esperando inicio de la aplicación..."
sleep 5

# Verificar que está corriendo
if ps -p $APP_PID > /dev/null; then
    echo "✓ Aplicación corriendo (PID: $APP_PID)"
    echo ""
    echo "📊 Últimas líneas del log:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    tail -n 20 app_test_output.log
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📝 Log completo en: app_test_output.log"
    echo ""
    echo "Para ver errores:"
    echo "  grep -i error app_test_output.log"
    echo ""
    echo "Para seguir logs en vivo:"
    echo "  tail -f app_test_output.log"
    echo ""
    echo "Para detener:"
    echo "  kill $APP_PID"
else
    echo "✗ La aplicación no se inició correctamente"
    echo ""
    echo "📊 Log de error:"
    cat app_test_output.log
    exit 1
fi
