"""
CORRECTOR FINAL - Sintaxis REAL de Flet 0.80.3
Basado en inspección directa del código
"""
import re
from pathlib import Path

def corregir_todo(directorio):
    archivos = list(Path(directorio).rglob("*.py"))
    archivos = [f for f in archivos if 'venv' not in str(f) and '__pycache__' not in str(f) and 'tools' not in str(f)]
    
    cambios = []
    
    for archivo in archivos:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            contenido_original = contenido
            
            # 1. REVERTIR ft.Icon(name=...) → ft.Icon(...)
            contenido = re.sub(
                r'ft\.Icon\(\s*name\s*=\s*',
                'ft.Icon(',
                contenido
            )
            
            # 2. ElevatedButton → Button
            contenido = re.sub(
                r'ft\.ElevatedButton\(',
                'ft.Button(',
                contenido
            )
            
            # 3. Dropdown.Option debe tener solo text y key posicionales
            # Patrón: ft.dropdown.Option(key, text) - ya está correcto
            
            if contenido != contenido_original:
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                cambios.append(archivo.name)
        
        except Exception as e:
            print(f"❌ Error en {archivo}: {e}")
    
    print(f"✅ {len(cambios)} archivos corregidos:")
    for c in cambios:
        print(f"  📝 {c}")

if __name__ == "__main__":
    corregir_todo('/mnt/flox/conychips')
