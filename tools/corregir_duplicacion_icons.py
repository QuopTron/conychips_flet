#!/usr/bin/env python3
"""
Script para corregir la duplicación de Icons en el código.
Arregla: ft.icons.Icons.X → ft.icons.Icons.X
"""

import re
from pathlib import Path

def corregir_duplicacion(contenido: str) -> tuple[str, int]:
    """Corrige la duplicación de Icons"""
    patron = r'ft\.icons\.Icons\.Icons\.'
    reemplazo = r'ft.icons.Icons.'
    
    nuevo_contenido = re.sub(patron, reemplazo, contenido)
    cambios = len(re.findall(patron, contenido))
    
    return nuevo_contenido, cambios

def procesar_archivo(ruta: Path) -> int:
    """Procesa un archivo y retorna el número de cambios"""
    try:
        contenido = ruta.read_text(encoding='utf-8')
        nuevo_contenido, cambios = corregir_duplicacion(contenido)
        
        if cambios > 0:
            ruta.write_text(nuevo_contenido, encoding='utf-8')
            print(f"  ✓ {ruta.relative_to(Path.cwd())}: {cambios} correcciones")
        
        return cambios
    except Exception as e:
        print(f"  ✗ Error en {ruta}: {e}")
        return 0

def main():
    proyecto = Path.cwd()
    
    # Excluir directorios
    excluir = {'.git', '__pycache__', 'venv', '.venv', 'node_modules', '.pytest_cache'}
    
    print("🔧 Corrigiendo duplicación de Icons...\n")
    
    archivos_python = []
    for ruta in proyecto.rglob('*.py'):
        if not any(parte in excluir for parte in ruta.parts):
            archivos_python.append(ruta)
    
    total_cambios = 0
    archivos_modificados = 0
    
    for archivo in archivos_python:
        cambios = procesar_archivo(archivo)
        if cambios > 0:
            total_cambios += cambios
            archivos_modificados += 1
    
    print(f"\n✅ Corrección completada:")
    print(f"   - Archivos modificados: {archivos_modificados}")
    print(f"   - Total de correcciones: {total_cambios}")

if __name__ == "__main__":
    main()
