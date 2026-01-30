#!/usr/bin/env python3
"""
Script para detectar patrones complejos de sintaxis Flet 0.80.3
que requieren corrección manual o inspección adicional
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

PROYECTO_ROOT = Path(__file__).parent.parent
EXCLUIR_DIRS = {'__pycache__', 'venv', '.git', 'node_modules', '.pytest_cache', 'build', 'dist', '.vscode', 'keys', 'assets'}
EXTENSIONES = {'.py'}

class DetectorPatronesComplejos:
    """Detecta patrones que requieren inspección manual"""
    
    def __init__(self):
        self.hallazgos = []
        
    def obtener_archivos_python(self) -> List[Path]:
        """Obtiene todos los archivos Python del proyecto"""
        archivos = []
        for root, dirs, files in os.walk(PROYECTO_ROOT):
            dirs[:] = [d for d in dirs if d not in EXCLUIR_DIRS]
            for file in files:
                if Path(file).suffix in EXTENSIONES:
                    archivos.append(Path(root) / file)
        return archivos
    
    def crear_detectores(self) -> List[Tuple[re.Pattern, str, str]]:
        """
        Retorna lista de tuplas (patron_regex, nivel, descripcion)
        nivel: 'WARNING' o 'INFO'
        """
        detectores = []
        
        # 1. page.snack_bar = (requiere cambiar a overlay)
        detectores.append((
            re.compile(r'page\.snack_bar\s*='),
            'WARNING',
            'page.snack_bar = X → Usar page.overlay.append(X) con X.open=True'
        ))
        
        # 2. page.dialog = (requiere cambiar a show_dialog o overlay)
        detectores.append((
            re.compile(r'page\.dialog\s*='),
            'WARNING',
            'page.dialog = X → Usar page.show_dialog(X) o page.overlay.append()'
        ))
        
        # 3. ft.Icons.X usado sin ft.icons (puede ser correcto o error)
        detectores.append((
            re.compile(r'ft\.Icons\.[A-Z_]+'),
            'INFO',
            'Verificar: ft.Icons.X debe ser ft.icons.Icons.X'
        ))
        
        # 4. Emojis en código (mejor usar iconos)
        detectores.append((
            re.compile(r'[🍔🍕💰👤⏰📊📈📉🔍👁️🎯✅❌⚠️ℹ️🧾]'),
            'INFO',
            'Emoji encontrado - Considerar reemplazar con ft.Icon()'
        ))
        
        # 5. ft.Image sin especificar fit
        detectores.append((
            re.compile(r'ft\.Image\([^)]*\)(?![^)]*fit\s*=)'),
            'INFO',
            'ft.Image sin parámetro fit - Considerar agregar fit=ft.BoxFit.X'
        ))
        
        # 6. Container sin alignment (puede necesitar centrado)
        detectores.append((
            re.compile(r'ft\.Container\([^)]*content\s*=(?![^)]*alignment\s*=)'),
            'INFO',
            'Container con content sin alignment - Verificar si necesita alineación'
        ))
        
        # 7. Uso de ft.alignment.Alignment (puede ser correcto)
        detectores.append((
            re.compile(r'ft\.alignment\.Alignment\('),
            'INFO',
            'ft.alignment.Alignment(...) - Debería ser ft.Alignment(...)'
        ))
        
        # 8. import flet as ft verificación
        detectores.append((
            re.compile(r'^import flet(?! as ft)'),
            'WARNING',
            'import flet - Debería ser "import flet as ft"'
        ))
        
        # 9. Closures en on_click con variables de loop
        detectores.append((
            re.compile(r'on_click\s*=\s*lambda\s+e\s*:\s*\w+\([^)]*\w+\)(?=.*for\s+\w+\s+in)'),
            'WARNING',
            'Closure en loop - Verificar captura de variable (usar lambda e, x=x)'
        ))
        
        # 10. page.update() sin try-except en handlers async
        detectores.append((
            re.compile(r'def\s+\w+.*async.*:.*page\.update\(\)(?!.*except)', re.DOTALL),
            'INFO',
            'page.update() en función async sin try-except'
        ))
        
        return detectores
    
    def analizar_archivo(self, archivo: Path, detectores: List[Tuple]) -> List[Dict]:
        """Analiza un archivo y retorna hallazgos"""
        hallazgos_archivo = []
        
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
            
            for num_linea, linea in enumerate(lineas, 1):
                for patron, nivel, descripcion in detectores:
                    if patron.search(linea):
                        hallazgos_archivo.append({
                            'archivo': archivo,
                            'linea': num_linea,
                            'nivel': nivel,
                            'descripcion': descripcion,
                            'codigo': linea.strip()
                        })
            
            return hallazgos_archivo
            
        except Exception as e:
            print(f"✗ Error leyendo {archivo}: {e}")
            return []
    
    def ejecutar(self):
        """Ejecuta el detector en todo el proyecto"""
        print("=" * 70)
        print("DETECTOR DE PATRONES COMPLEJOS - FLET 0.80.3")
        print("=" * 70)
        print()
        
        archivos = self.obtener_archivos_python()
        print(f"📁 Archivos Python: {len(archivos)}")
        print()
        
        detectores = self.crear_detectores()
        print(f"🔍 Detectores activos: {len(detectores)}")
        print()
        
        print("Analizando archivos...")
        print("-" * 70)
        
        for archivo in archivos:
            hallazgos = self.analizar_archivo(archivo, detectores)
            self.hallazgos.extend(hallazgos)
        
        # Agrupar por nivel
        warnings = [h for h in self.hallazgos if h['nivel'] == 'WARNING']
        infos = [h for h in self.hallazgos if h['nivel'] == 'INFO']
        
        print()
        print("=" * 70)
        print("RESUMEN")
        print("=" * 70)
        print(f"⚠️  WARNINGS (requieren atención): {len(warnings)}")
        print(f"ℹ️  INFO (revisar si aplica): {len(infos)}")
        print()
        
        if warnings:
            print("=" * 70)
            print("⚠️  WARNINGS")
            print("=" * 70)
            for h in warnings:
                ruta_rel = h['archivo'].relative_to(PROYECTO_ROOT)
                print(f"\n📍 {ruta_rel}:{h['linea']}")
                print(f"   {h['descripcion']}")
                print(f"   Código: {h['codigo'][:70]}")
        
        if infos:
            print()
            print("=" * 70)
            print("ℹ️  INFO (primeros 10)")
            print("=" * 70)
            for h in infos[:10]:
                ruta_rel = h['archivo'].relative_to(PROYECTO_ROOT)
                print(f"\n📍 {ruta_rel}:{h['linea']}")
                print(f"   {h['descripcion']}")
                print(f"   Código: {h['codigo'][:70]}")
        
        print()
        print("=" * 70)


if __name__ == "__main__":
    detector = DetectorPatronesComplejos()
    detector.ejecutar()
