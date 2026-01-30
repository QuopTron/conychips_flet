#!/usr/bin/env python3
"""
Corregir ft.colors (minúscula) a ft.Colors (mayúscula)
En Flet 0.80.3, ft.colors NO EXISTE - debe ser ft.Colors
"""
import re
from pathlib import Path

# Patrones a corregir
CORRECCIONES = {
    # ft.Colors.X → ft.Colors.X (mayúscula)
    r'\bft\.colors\.': 'ft.Colors.',
}

# Directorios a excluir
EXCLUIR = {'.git', 'venv', '__pycache__', 'node_modules', '.pytest_cache', 'build', 'dist'}

def corregir_archivo(ruta: Path) -> int:
    """Corregir sintaxis de colors en un archivo"""
    try:
        contenido = ruta.read_text(encoding='utf-8')
        contenido_original = contenido
        
        # Aplicar correcciones
        for patron, reemplazo in CORRECCIONES.items():
            contenido = re.sub(patron, reemplazo, contenido)
        
        # Si hubo cambios, guardar
        if contenido != contenido_original:
            ruta.write_text(contenido, encoding='utf-8')
            return 1
        return 0
            
    except Exception as e:
        print(f"  ⚠️ Error en {ruta}: {e}")
        return 0

def main():
    """Ejecutar correcciones"""
    raiz = Path(__file__).parent.parent
    archivos_corregidos = 0
    total_correcciones = 0
    
    print("🔍 Buscando archivos .py con ft.colors (minúscula)...")
    
    for archivo in raiz.rglob('*.py'):
        # Saltar directorios excluidos
        if any(parte in EXCLUIR for parte in archivo.parts):
            continue
        
        # Saltar este script
        if archivo.name == 'corregir_colors_mayuscula.py':
            continue
        
        correcciones = corregir_archivo(archivo)
        if correcciones > 0:
            archivos_corregidos += 1
            total_correcciones += correcciones
            print(f"  ✓ {archivo.relative_to(raiz)}: {correcciones} corrección(es)")
    
    print(f"\n✅ Corrección completada:")
    print(f"   - {archivos_corregidos} archivo(s) corregido(s)")
    print(f"   - {total_correcciones} cambio(s) total(es)")
    print(f"\n📝 Cambio aplicado: ft.Colors.X → ft.Colors.X")

if __name__ == "__main__":
    main()
