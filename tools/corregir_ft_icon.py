"""
Corregir sintaxis de ft.Icon - usa 'name' como primer parámetro
"""
import re
from pathlib import Path

def corregir_icons(directorio_base):
    archivos = list(Path(directorio_base).rglob("*.py"))
    archivos = [f for f in archivos if 'venv' not in str(f) and '__pycache__' not in str(f) and 'tools' not in str(f)]
    
    cambios = []
    
    for archivo in archivos:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            contenido_original = contenido
            
            # Patrón: ft.Icon(ft.icons.Icons.NOMBRE, ...) → ft.Icon(name=ft.icons.Icons.NOMBRE, ...)
            # Solo si no tiene 'name=' ya
            contenido = re.sub(
                r'ft\.Icon\((\s*)(ft\.icons\.Icons\.[A-Z_]+)(\s*,)',
                r'ft.Icon(\1name=\2\3',
                contenido
            )
            
            # Patrón: ft.Icon(ICONOS.NOMBRE, ...) → ft.Icon(name=ICONOS.NOMBRE, ...)
            contenido = re.sub(
                r'ft\.Icon\((\s*)(ICONOS\.[A-Z_]+)(\s*,)',
                r'ft.Icon(\1name=\2\3',
                contenido
            )
            
            if contenido != contenido_original:
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                cambios.append(archivo.name)
        
        except Exception as e:
            print(f"Error en {archivo}: {e}")
    
    print(f"✅ {len(cambios)} archivos corregidos")
    for c in cambios:
        print(f"  📝 {c}")

if __name__ == "__main__":
    corregir_icons('/mnt/flox/conychips')
