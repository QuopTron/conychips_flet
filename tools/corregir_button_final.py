"""
CORRECTOR COMPLETO Y FINAL - Verificado contra Flet 0.80.3
"""
import re
from pathlib import Path

def corregir_todo_final(directorio):
    archivos = list(Path(directorio).rglob("*.py"))
    archivos = [f for f in archivos if 'venv' not in str(f) and '__pycache__' not in str(f) and 'tools' not in str(f)]
    
    cambios = []
    errores = []
    
    for archivo in archivos:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            original = contenido
            
            # 1. ft.Button(texto, ...) → ft.Button(content=ft.Text(texto), ...)
            # Solo si el primer parámetro es string literal
            def corregir_button(match):
                indent = match.group(1)
                texto = match.group(2)
                resto = match.group(3)
                
                # Si ya tiene content=, skip
                if 'content=' in resto[:50]:
                    return match.group(0)
                
                return f'{indent}ft.Button(\\n{indent}    content=ft.Text({texto}),{resto}'
            
            contenido = re.sub(
                r'([ \t]*)ft\.Button\(\\n\1    (["\'][^"\']+["\'])([,)])',
                corregir_button,
                contenido
            )
            
            # También para Button inline
            contenido = re.sub(
                r'ft\.Button\((["\'][^"\']*["\'])(?=,)',
                r'ft.Button(content=ft.Text(\1)',
                contenido
            )
            
            # 2. CircleAvatar con foreground_image → foreground_image_src
            contenido = re.sub(
                r'foreground_image\s*=',
                'foreground_image_src=',
                contenido
            )
            
            # 3. Image con src correcto
            # Ya debe estar correcto
            
            if contenido != original:
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                cambios.append(archivo.name)
        
        except Exception as e:
            errores.append(f"{archivo.name}: {str(e)}")
    
    print(f"✅ {len(cambios)} archivos corregidos")
    for c in cambios:
        print(f"  📝 {c}")
    
    if errores:
        print(f"\\n❌ {len(errores)} errores:")
        for e in errores:
            print(f"  {e}")

if __name__ == "__main__":
    corregir_todo_final('/mnt/flox/conychips')
