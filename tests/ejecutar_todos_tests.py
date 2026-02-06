#!/usr/bin/env python3
"""
🧪 SUITE DE PRUEBAS COMPLETA
Ejecuta todos los tests organizados en Caja Negra y Caja Blanca
"""
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Colores para terminal
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def imprimir_banner():
    """Imprime el banner inicial"""
    print(f"\n{Color.HEADER}{'=' * 80}{Color.ENDC}")
    print(f"{Color.BOLD}{Color.OKCYAN}🧪 SUITE DE PRUEBAS COMPLETA - CONYCHIPS{Color.ENDC}")
    print(f"{Color.OKBLUE}📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Color.ENDC}")
    print(f"{Color.HEADER}{'=' * 80}{Color.ENDC}\n")


def ejecutar_tests_caja_negra():
    """Ejecuta todos los tests de caja negra (integración)"""
    print(f"\n{Color.BOLD}{Color.OKBLUE}📦 TESTS DE CAJA NEGRA (Integración){Color.ENDC}")
    print(f"{Color.OKCYAN}{'─' * 80}{Color.ENDC}")
    
    tests = [
        "tests/caja_negra/test_flujo_navegacion.py",
        "tests/caja_negra/test_dropdown_interaccion.py"
    ]
    
    resultados = []
    
    for test in tests:
        test_path = Path(test)
        if not test_path.exists():
            print(f"{Color.WARNING}⚠️  {test} no encontrado{Color.ENDC}")
            continue
        
        print(f"\n{Color.OKBLUE}🔄 Ejecutando: {test_path.name}{Color.ENDC}")
        
        try:
            resultado = subprocess.run(
                [sys.executable, str(test_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if resultado.returncode == 0:
                print(f"{Color.OKGREEN}✅ {test_path.name} - PASÓ{Color.ENDC}")
                resultados.append((test_path.name, True))
            else:
                print(f"{Color.FAIL}❌ {test_path.name} - FALLÓ{Color.ENDC}")
                if resultado.stderr:
                    print(f"{Color.WARNING}Error: {resultado.stderr[:200]}{Color.ENDC}")
                resultados.append((test_path.name, False))
                
        except subprocess.TimeoutExpired:
            print(f"{Color.WARNING}⏱️  {test_path.name} - TIMEOUT{Color.ENDC}")
            resultados.append((test_path.name, False))
        except Exception as e:
            print(f"{Color.FAIL}❌ {test_path.name} - ERROR: {str(e)}{Color.ENDC}")
            resultados.append((test_path.name, False))
    
    return resultados


def ejecutar_tests_caja_blanca():
    """Ejecuta todos los tests de caja blanca (unitarios)"""
    print(f"\n{Color.BOLD}{Color.OKBLUE}🔬 TESTS DE CAJA BLANCA (Unitarios){Color.ENDC}")
    print(f"{Color.OKCYAN}{'─' * 80}{Color.ENDC}")
    
    tests = [
        "tests/caja_blanca/test_layout_estructura.py",
        "tests/caja_blanca/test_navbar_logica.py"
    ]
    
    resultados = []
    
    for test in tests:
        test_path = Path(test)
        if not test_path.exists():
            print(f"{Color.WARNING}⚠️  {test} no encontrado{Color.ENDC}")
            continue
        
        print(f"\n{Color.OKBLUE}🔄 Ejecutando: {test_path.name}{Color.ENDC}")
        
        try:
            resultado = subprocess.run(
                [sys.executable, str(test_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if resultado.returncode == 0:
                print(f"{Color.OKGREEN}✅ {test_path.name} - PASÓ{Color.ENDC}")
                resultados.append((test_path.name, True))
            else:
                print(f"{Color.FAIL}❌ {test_path.name} - FALLÓ{Color.ENDC}")
                if resultado.stderr:
                    print(f"{Color.WARNING}Error: {resultado.stderr[:200]}{Color.ENDC}")
                resultados.append((test_path.name, False))
                
        except subprocess.TimeoutExpired:
            print(f"{Color.WARNING}⏱️  {test_path.name} - TIMEOUT{Color.ENDC}")
            resultados.append((test_path.name, False))
        except Exception as e:
            print(f"{Color.FAIL}❌ {test_path.name} - ERROR: {str(e)}{Color.ENDC}")
            resultados.append((test_path.name, False))
    
    return resultados


def imprimir_resumen(resultados_negra, resultados_blanca):
    """Imprime el resumen final de todos los tests"""
    print(f"\n{Color.HEADER}{'=' * 80}{Color.ENDC}")
    print(f"{Color.BOLD}{Color.OKCYAN}📊 RESUMEN DE RESULTADOS{Color.ENDC}")
    print(f"{Color.HEADER}{'=' * 80}{Color.ENDC}")
    
    total_tests = len(resultados_negra) + len(resultados_blanca)
    pasaron = sum(1 for _, resultado in resultados_negra + resultados_blanca if resultado)
    fallaron = total_tests - pasaron
    
    print(f"\n{Color.OKBLUE}📦 Tests de Caja Negra:{Color.ENDC}")
    for nombre, resultado in resultados_negra:
        icono = f"{Color.OKGREEN}✅{Color.ENDC}" if resultado else f"{Color.FAIL}❌{Color.ENDC}"
        print(f"   {icono} {nombre}")
    
    print(f"\n{Color.OKBLUE}🔬 Tests de Caja Blanca:{Color.ENDC}")
    for nombre, resultado in resultados_blanca:
        icono = f"{Color.OKGREEN}✅{Color.ENDC}" if resultado else f"{Color.FAIL}❌{Color.ENDC}"
        print(f"   {icono} {nombre}")
    
    print(f"\n{Color.BOLD}TOTALES:{Color.ENDC}")
    print(f"   Total de tests: {total_tests}")
    print(f"   {Color.OKGREEN}✅ Pasaron: {pasaron}{Color.ENDC}")
    print(f"   {Color.FAIL}❌ Fallaron: {fallaron}{Color.ENDC}")
    
    porcentaje = (pasaron / total_tests * 100) if total_tests > 0 else 0
    
    if porcentaje == 100:
        print(f"\n{Color.OKGREEN}{Color.BOLD}🎉 ¡TODOS LOS TESTS PASARON! ({porcentaje:.0f}%){Color.ENDC}")
    elif porcentaje >= 70:
        print(f"\n{Color.WARNING}{Color.BOLD}⚠️  {porcentaje:.0f}% de tests pasaron{Color.ENDC}")
    else:
        print(f"\n{Color.FAIL}{Color.BOLD}❌ Solo {porcentaje:.0f}% de tests pasaron{Color.ENDC}")
    
    print(f"\n{Color.HEADER}{'=' * 80}{Color.ENDC}\n")
    
    return fallaron == 0


def main():
    """Función principal"""
    imprimir_banner()
    
    # Ejecutar tests
    resultados_negra = ejecutar_tests_caja_negra()
    resultados_blanca = ejecutar_tests_caja_blanca()
    
    # Mostrar resumen
    exito = imprimir_resumen(resultados_negra, resultados_blanca)
    
    # Exit code
    sys.exit(0 if exito else 1)


if __name__ == "__main__":
    main()
