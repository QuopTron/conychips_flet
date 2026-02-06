#!/usr/bin/env python3
"""
Script para corregir automáticamente sintaxis incorrecta de Flet 0.80.3
Busca y reemplaza patrones incorrectos en todo el proyecto
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Directorio raíz del proyecto
PROYECTO_ROOT = Path(__file__).parent.parent

# Directorios a excluir
EXCLUIR_DIRS = {
    '__pycache__', 'venv', '.git', 'node_modules', 
    '.pytest_cache', 'build', 'dist', '.vscode',
    'keys', 'assets'
}

# Extensiones de archivos a procesar
EXTENSIONES = {'.py'}

class CorrectorSintaxis:
    """Corrige automáticamente sintaxis incorrecta de Flet 0.80.3"""
    
    def __init__(self):
        self.correcciones = 0
        self.archivos_modificados = []
        
    def obtener_archivos_python(self) -> List[Path]:
        """Obtiene todos los archivos Python del proyecto"""
        archivos = []
        for root, dirs, files in os.walk(PROYECTO_ROOT):
            # Excluir directorios
            dirs[:] = [d for d in dirs if d not in EXCLUIR_DIRS]
            
            for file in files:
                if Path(file).suffix in EXTENSIONES:
                    archivos.append(Path(root) / file)
        
        return archivos
    
    def crear_patrones_reemplazo(self) -> List[Tuple[re.Pattern, str, str]]:
        """
        Retorna lista de tuplas (patron_regex, reemplazo, descripcion)
        """
        patrones = []
        
        # 1. ft.icons.Icons.ICON_NAME → ft.icons.Icons.ICON_NAME (sin repetir .Icons.Icons)
        patrones.append((
            re.compile(r'ft\.icons\.([A-Z_]+)(?!\.Icons)'),
            r'ft.icons.Icons.\1',
            'Iconos: ft.icons.Icons.X → ft.icons.Icons.X'
        ))
        
        # 2. ft.Icon(→ ft.Icon(
        patrones.append((
            re.compile(r'ft\.Icon\(\s*name\s*=\s*'),
            r'ft.Icon(',
            'Icon: Eliminar parámetro name='
        ))
        
        # 3. ft.ImageFit → ft.BoxFit
        patrones.append((
            re.compile(r'ft\.ImageFit\.'),
            r'ft.BoxFit.',
            'ImageFit → BoxFit'
        ))
        
        # 4. ft.Alignment(0, 0) → ft.Alignment(0, 0)
        alignment_map = {
            'center': '(0, 0)',
            'top_left': '(-1, -1)',
            'top_center': '(0, -1)',
            'top_right': '(1, -1)',
            'center_left': '(-1, 0)',
            'center_right': '(1, 0)',
            'bottom_left': '(-1, 1)',
            'bottom_center': '(0, 1)',
            'bottom_right': '(1, 1)',
        }
        
        for old, new in alignment_map.items():
            patrones.append((
                re.compile(rf'ft\.alignment\.{old}\b'),
                f'ft.Alignment{new}',
                f'Alignment: ft.alignment.{old} → ft.Alignment{new}'
            ))
        
        # 5. page.width → page.width
        patrones.append((
            re.compile(r'\bpage\.window_width\b'),
            r'page.width',
            'Page: window_width → width'
        ))
        
        # 6. page.height → page.height
        patrones.append((
            re.compile(r'\bpage\.window_height\b'),
            r'page.height',
            'Page: window_height → height'
        ))
        
        # 7. self._PAGINA.width → self._PAGINA.width
        patrones.append((
            re.compile(r'self\._PAGINA\.window_width\b'),
            r'self._PAGINA.width',
            'Page: self._PAGINA.width → width'
        ))
        
        # 8. self._PAGINA.height → self._PAGINA.height
        patrones.append((
            re.compile(r'self\._PAGINA\.window_height\b'),
            r'self._PAGINA.height',
            'Page: self._PAGINA.height → height'
        ))
        
        # 9. ft.Rotate → ft.Rotate
        patrones.append((
            re.compile(r'ft\.transform\.Rotate\b'),
            r'ft.Rotate',
            'Transform: ft.Rotate → ft.Rotate'
        ))
        
        # 10. ft.Scale → ft.Scale
        patrones.append((
            re.compile(r'ft\.transform\.Scale\b'),
            r'ft.Scale',
            'Transform: ft.Scale → ft.Scale'
        ))
        
        # 11. page.snack_bar = → page.overlay.append(
        # Este es más complejo, requiere análisis contextual
        # Lo dejamos para corrección manual
        
        return patrones
    
    def corregir_archivo(self, archivo: Path, patrones: List[Tuple]) -> int:
        """Corrige un archivo y retorna el número de correcciones"""
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            contenido_original = contenido
            correcciones_archivo = 0
            
            for patron, reemplazo, descripcion in patrones:
                matches = patron.findall(contenido)
                if matches:
                    contenido_nuevo = patron.sub(reemplazo, contenido)
                    if contenido_nuevo != contenido:
                        num_cambios = len(matches)
                        correcciones_archivo += num_cambios
                        contenido = contenido_nuevo
                        print(f"  ✓ {descripcion}: {num_cambios} cambio(s)")
            
            # Si hubo cambios, escribir el archivo
            if contenido != contenido_original:
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                self.archivos_modificados.append(archivo)
                return correcciones_archivo
            
            return 0
            
        except Exception as e:
            print(f"  ✗ Error procesando {archivo}: {e}")
            return 0
    
    def ejecutar(self):
        """Ejecuta el corrector en todo el proyecto"""
        print("=" * 70)
        print("CORRECTOR AUTOMÁTICO DE SINTAXIS FLET 0.80.3")
        print("=" * 70)
        print()
        
        archivos = self.obtener_archivos_python()
        print(f"📁 Archivos Python encontrados: {len(archivos)}")
        print()
        
        patrones = self.crear_patrones_reemplazo()
        print(f"🔍 Patrones de corrección: {len(patrones)}")
        print()
        
        print("Procesando archivos...")
        print("-" * 70)
        
        for archivo in archivos:
            ruta_relativa = archivo.relative_to(PROYECTO_ROOT)
            correcciones = self.corregir_archivo(archivo, patrones)
            
            if correcciones > 0:
                print(f"\n📝 {ruta_relativa}")
                self.correcciones += correcciones
        
        print()
        print("=" * 70)
        print("RESUMEN")
        print("=" * 70)
        print(f"✅ Archivos modificados: {len(self.archivos_modificados)}")
        print(f"✅ Total de correcciones: {self.correcciones}")
        print()
        
        if self.archivos_modificados:
            print("Archivos modificados:")
            for archivo in self.archivos_modificados:
                print(f"  - {archivo.relative_to(PROYECTO_ROOT)}")
        else:
            print("✓ No se encontraron errores de sintaxis")
        
        print()
        print("=" * 70)


if __name__ == "__main__":
    corrector = CorrectorSintaxis()
    corrector.ejecutar()
