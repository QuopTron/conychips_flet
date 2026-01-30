#!/usr/bin/env python3
"""
Corrección COMPLETA de sintaxis Flet 0.80.3
Basado en inspección real de la API con Python inspect
"""
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Directorios a excluir
EXCLUIR = {'.git', 'venv', '__pycache__', 'node_modules', '.pytest_cache', 'build', 'dist'}

class CorrectorSintaxisFlet:
    """Corrector de sintaxis Flet 0.80.3"""
    
    def __init__(self):
        self.correcciones_aplicadas: Dict[str, List[str]] = {}
        self.archivos_corregidos = 0
        self.total_correcciones = 0
    
    def corregir_dropdown_on_change(self, contenido: str, archivo: str) -> str:
        """Corregir Dropdown.on_change → on_select"""
        # Solo cambiar on_change que está en líneas con ft.Dropdown
        lineas = contenido.split('\n')
        lineas_modificadas = []
        dropdown_context = False
        cambios = 0
        
        for i, linea in enumerate(lineas):
            # Detectar inicio de ft.Dropdown
            if 'ft.Dropdown(' in linea or 'ft.dropdown.Dropdown(' in linea:
                dropdown_context = True
            
            # Si estamos en contexto de Dropdown y vemos on_change
            if dropdown_context and re.search(r'\bon_change\s*=', linea):
                linea = re.sub(r'\bon_change\b', 'on_select', linea)
                cambios += 1
                self._registrar_cambio(archivo, f"Dropdown: on_change → on_select (línea {i+1})")
            
            # Salir del contexto cuando vemos el cierre del paréntesis principal
            if dropdown_context and ')' in linea and 'ft.dropdown.Option' not in linea:
                # Contar paréntesis para detectar cierre
                if linea.strip().endswith(')') or linea.strip().endswith('),'):
                    dropdown_context = False
            
            lineas_modificadas.append(linea)
        
        return '\n'.join(lineas_modificadas)
    
    def corregir_colors_mayuscula(self, contenido: str, archivo: str) -> str:
        """Corregir ft.colors → ft.Colors"""
        patron = r'\bft\.colors\.'
        if re.search(patron, contenido):
            contenido = re.sub(patron, 'ft.Colors.', contenido)
            self._registrar_cambio(archivo, "ft.colors → ft.Colors")
        return contenido
    
    def corregir_icons_duplicados(self, contenido: str, archivo: str) -> str:
        """Corregir ft.icons.Icons.Icons → ft.icons.Icons"""
        patron = r'\bft\.icons\.Icons\.Icons\.'
        if re.search(patron, contenido):
            contenido = re.sub(patron, 'ft.icons.Icons.', contenido)
            self._registrar_cambio(archivo, "ft.icons.Icons.Icons → ft.icons.Icons")
        return contenido
    
    def corregir_icons_sin_clase(self, contenido: str, archivo: str) -> str:
        """Corregir ft.icons.ICON → ft.icons.Icons.ICON (sin duplicar)"""
        # Buscar ft.icons.NOMBRE donde NOMBRE está en mayúsculas (constante de icono)
        # Pero NO si ya es ft.icons.Icons.X
        patron = r'\bft\.icons\.([A-Z][A-Z_0-9]+)\b'
        
        def reemplazar(match):
            nombre_icono = match.group(1)
            # No duplicar si ya es Icons.
            if match.string[max(0, match.start()-6):match.start()] != 'Icons.':
                return f'ft.icons.Icons.{nombre_icono}'
            return match.group(0)
        
        nuevo_contenido = re.sub(patron, reemplazar, contenido)
        if nuevo_contenido != contenido:
            self._registrar_cambio(archivo, "ft.icons.ICON → ft.icons.Icons.ICON")
        return nuevo_contenido
    
    def corregir_alignment_constantes(self, contenido: str, archivo: str) -> str:
        """Corregir ft.alignment.center → ft.alignment.Alignment(0, 0)"""
        # Buscar patrones como ft.alignment.center, ft.alignment.top_left, etc.
        # Estos no existen en Flet 0.80.3
        patron = r'\bft\.alignment\.([a-z_]+)\b'
        
        def reemplazar_alignment(match):
            nombre = match.group(1)
            # Mapeo de nombres comunes a coordenadas
            mapeo = {
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
            
            if nombre in mapeo:
                self._registrar_cambio(archivo, f"ft.alignment.{nombre} → ft.Alignment{mapeo[nombre]}")
                return f'ft.Alignment{mapeo[nombre]}'
            
            return match.group(0)
        
        return re.sub(patron, reemplazar_alignment, contenido)
    
    def corregir_image_fit(self, contenido: str, archivo: str) -> str:
        """Corregir ft.ImageFit → ft.BoxFit"""
        patron = r'\bft\.ImageFit\.'
        if re.search(patron, contenido):
            contenido = re.sub(patron, 'ft.BoxFit.', contenido)
            self._registrar_cambio(archivo, "ft.ImageFit → ft.BoxFit")
        return contenido
    
    def corregir_page_deprecated(self, contenido: str, archivo: str) -> str:
        """Corregir page.window_width → page.width, etc."""
        cambios = [
            (r'\bpage\.window_width\b', 'page.width', 'page.window_width → page.width'),
            (r'\bpage\.window_height\b', 'page.height', 'page.window_height → page.height'),
        ]
        
        for patron, reemplazo, mensaje in cambios:
            if re.search(patron, contenido):
                contenido = re.sub(patron, reemplazo, contenido)
                self._registrar_cambio(archivo, mensaje)
        
        return contenido
    
    def _registrar_cambio(self, archivo: str, mensaje: str):
        """Registrar un cambio aplicado"""
        if archivo not in self.correcciones_aplicadas:
            self.correcciones_aplicadas[archivo] = []
        self.correcciones_aplicadas[archivo].append(mensaje)
    
    def corregir_archivo(self, ruta: Path) -> bool:
        """Aplicar todas las correcciones a un archivo"""
        try:
            contenido = ruta.read_text(encoding='utf-8')
            contenido_original = contenido
            
            # Aplicar todas las correcciones en orden
            contenido = self.corregir_colors_mayuscula(contenido, str(ruta))
            contenido = self.corregir_icons_duplicados(contenido, str(ruta))
            contenido = self.corregir_icons_sin_clase(contenido, str(ruta))
            contenido = self.corregir_dropdown_on_change(contenido, str(ruta))
            contenido = self.corregir_alignment_constantes(contenido, str(ruta))
            contenido = self.corregir_image_fit(contenido, str(ruta))
            contenido = self.corregir_page_deprecated(contenido, str(ruta))
            
            # Si hubo cambios, guardar
            if contenido != contenido_original:
                ruta.write_text(contenido, encoding='utf-8')
                return True
            
            return False
                
        except Exception as e:
            print(f"  ⚠️ Error en {ruta}: {e}")
            return False
    
    def procesar_proyecto(self, raiz: Path):
        """Procesar todo el proyecto"""
        print("🔍 Escaneando proyecto completo...\n")
        
        for archivo in raiz.rglob('*.py'):
            # Saltar directorios excluidos
            if any(parte in EXCLUIR for parte in archivo.parts):
                continue
            
            # Saltar este script
            if 'corregir_sintaxis' in archivo.name:
                continue
            
            if self.corregir_archivo(archivo):
                self.archivos_corregidos += 1
        
        # Mostrar resumen
        self.mostrar_resumen(raiz)
    
    def mostrar_resumen(self, raiz: Path):
        """Mostrar resumen de correcciones"""
        print(f"\n{'='*80}")
        print(f"✅ CORRECCIÓN COMPLETA FINALIZADA")
        print(f"{'='*80}\n")
        
        if self.correcciones_aplicadas:
            print(f"📊 {self.archivos_corregidos} archivo(s) corregido(s):\n")
            
            for archivo, cambios in sorted(self.correcciones_aplicadas.items()):
                try:
                    ruta_relativa = Path(archivo).relative_to(raiz)
                except:
                    ruta_relativa = Path(archivo)
                
                print(f"  📄 {ruta_relativa}")
                for cambio in cambios:
                    print(f"     • {cambio}")
                print()
            
            # Contar tipos de correcciones
            tipos_correcciones = {}
            for cambios in self.correcciones_aplicadas.values():
                for cambio in cambios:
                    # Extraer el tipo de corrección (antes del →)
                    tipo = cambio.split('→')[0].strip() if '→' in cambio else cambio.split(':')[0].strip()
                    tipos_correcciones[tipo] = tipos_correcciones.get(tipo, 0) + 1
            
            print(f"📈 Resumen por tipo de corrección:")
            for tipo, cantidad in sorted(tipos_correcciones.items()):
                print(f"   • {tipo}: {cantidad}")
        else:
            print("✨ No se encontraron errores de sintaxis Flet.")
            print("   El proyecto ya está actualizado a Flet 0.80.3")

def main():
    """Ejecutar corrector"""
    raiz = Path(__file__).parent.parent
    corrector = CorrectorSintaxisFlet()
    corrector.procesar_proyecto(raiz)

if __name__ == "__main__":
    main()
