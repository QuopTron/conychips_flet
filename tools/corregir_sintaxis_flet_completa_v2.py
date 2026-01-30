"""
Script para corregir TODA la sintaxis de Flet en el proyecto
Basado en inspección real de Flet 0.80.3
"""
import re
import os
from pathlib import Path

class CorrectorSintaxisFlet:
    def __init__(self, directorio_base):
        self.directorio = Path(directorio_base)
        self.cambios = []
        
    def corregir_todo(self):
        """Corregir toda la sintaxis de Flet"""
        print("🔧 CORRIGIENDO SINTAXIS DE FLET...")
        print("=" * 60)
        
        # Archivos a procesar
        archivos_python = list(self.directorio.rglob("*.py"))
        archivos_python = [f for f in archivos_python if 
                          'venv' not in str(f) and 
                          '__pycache__' not in str(f) and
                          'tools' not in str(f)]
        
        for archivo in archivos_python:
            self._procesar_archivo(archivo)
        
        print(f"\n✅ COMPLETADO: {len(self.cambios)} archivos modificados")
        for cambio in self.cambios:
            print(f"  📝 {cambio}")
    
    def _procesar_archivo(self, archivo):
        """Procesar un archivo Python"""
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            contenido_original = contenido
            
            # 1. Corregir iconos mal formados
            contenido = self._corregir_iconos(contenido, archivo)
            
            # 2. Corregir botones
            contenido = self._corregir_botones(contenido, archivo)
            
            # 3. Corregir Tabs
            contenido = self._corregir_tabs(contenido, archivo)
            
            # Solo escribir si hay cambios
            if contenido != contenido_original:
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                    
        except Exception as e:
            print(f"❌ Error en {archivo}: {e}")
    
    def _corregir_iconos(self, contenido, archivo):
        """Corregir sintaxis de iconos"""
        modificado = False
        
        # Patrón 1: ft.icons.NOMBRE_ICONO (sin Icons.) → ft.icons.Icons.NOMBRE_ICONO
        # Solo si NOMBRE_ICONO está en mayúsculas (es un icono)
        def reemplazar_icono(match):
            nombre = match.group(1)
            # Solo si está en mayúsculas y no es Icons
            if nombre.isupper() and nombre != 'Icons':
                nonlocal modificado
                modificado = True
                return f'ft.icons.Icons.{nombre}'
            return match.group(0)
        
        contenido = re.sub(
            r'ft\.icons\.([A-Z_]+)',
            reemplazar_icono,
            contenido
        )
        
        # Patrón 2: icon=ft.icons.NOMBRE → icon=ft.icons.Icons.NOMBRE
        contenido = re.sub(
            r'(icon\s*=\s*)ft\.icons\.([A-Z_]+)(?!\.Icons)',
            r'\1ft.icons.Icons.\2',
            contenido
        )
        
        # Patrón 3: Eliminar duplicación ft.icons.Icons.X → ft.icons.Icons.X
        if 'ft.icons.Icons.' in contenido:
            contenido = re.sub(
                r'ft\.icons\.Icons\.Icons\.',
                'ft.icons.Icons.',
                contenido
            )
            modificado = True
        
        if modificado:
            self.cambios.append(f"{archivo.name} - Iconos corregidos")
        
        return contenido
    
    def _corregir_botones(self, contenido, archivo):
        """Verificar sintaxis de botones (ya deberían estar correctos)"""
        # ElevatedButton, TextButton, IconButton usan 'content' no 'text'
        # Ya están correctos en el proyecto según el grep
        return contenido
    
    def _corregir_tabs(self, contenido, archivo):
        """Verificar sintaxis de Tabs"""
        # Tab usa 'label' e 'icon' directamente
        # Ya están correctos según el grep
        return contenido


if __name__ == "__main__":
    corrector = CorrectorSintaxisFlet('/mnt/flox/conychips')
    corrector.corregir_todo()
