#!/usr/bin/env python3
"""
Script de inspección de Flet instalado.
Busca ejemplos, documentación y código fuente en el paquete Flet instalado.

Uso:
    python tools/flet_inspector.py --search "AlertDialog"
    python tools/flet_inspector.py --search "BottomSheet" --show-examples
    python tools/flet_inspector.py --list-controls
"""

import argparse
import ast
import flet as ft
import inspect
import os
import re
import sys
from pathlib import Path


def get_flet_install_path():
    """Obtiene la ruta de instalación de Flet."""
    return Path(ft.__file__).parent


def search_in_flet_source(pattern, show_context=True):
    """Busca un patrón en el código fuente de Flet."""
    flet_path = get_flet_install_path()
    matches = []
    
    print(f"\n🔍 Buscando '{pattern}' en {flet_path}\n")
    
    for py_file in flet_path.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        rel_path = py_file.relative_to(flet_path)
                        matches.append({
                            'file': str(rel_path),
                            'line': i,
                            'content': line.strip()
                        })
                        
                        if show_context:
                            print(f"📄 {rel_path}:{i}")
                            print(f"   {line.strip()}")
                            # Mostrar contexto
                            start = max(0, i - 2)
                            end = min(len(lines), i + 2)
                            for j in range(start, end):
                                if j != i - 1:
                                    print(f"   {lines[j].rstrip()}")
                            print()
        except Exception as e:
            pass
    
    print(f"\n✅ Total: {len(matches)} coincidencias\n")
    return matches


def find_dialog_examples():
    """Busca ejemplos de uso de diálogos en Flet."""
    flet_path = get_flet_install_path()
    
    print(f"\n🎯 Buscando ejemplos de diálogos en {flet_path}\n")
    
    patterns = [
        r'AlertDialog\(',
        r'BottomSheet\(',
        r'page\.dialog\s*=',
        r'page\.bottom_sheet\s*=',
        r'\.open\s*=\s*True',
        r'show_dialog\(',
    ]
    
    for pattern in patterns:
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Patrón: {pattern}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        search_in_flet_source(pattern, show_context=False)


def list_dialog_controls():
    """Lista todos los controles de diálogo disponibles en Flet."""
    print("\n📋 Controles de diálogo disponibles en Flet:\n")
    
    dialog_controls = []
    
    for name in dir(ft):
        obj = getattr(ft, name)
        if inspect.isclass(obj):
            # Buscar clases que parezcan diálogos
            if any(keyword in name.lower() for keyword in ['dialog', 'sheet', 'modal', 'popup', 'snack']):
                dialog_controls.append(name)
                try:
                    sig = inspect.signature(obj.__init__)
                    print(f"✓ ft.{name}")
                    print(f"  Firma: {sig}")
                    if obj.__doc__:
                        first_line = obj.__doc__.split('\n')[0].strip()
                        print(f"  Doc: {first_line}")
                    print()
                except Exception:
                    print(f"✓ ft.{name}")
                    print()
    
    return dialog_controls


def inspect_alert_dialog():
    """Inspecciona AlertDialog en detalle."""
    print("\n🔬 Inspección detallada de ft.AlertDialog:\n")
    
    print(f"Clase: {ft.AlertDialog}")
    print(f"MRO: {[c.__name__ for c in ft.AlertDialog.__mro__]}")
    print(f"\nAtributos y métodos:")
    
    for attr in dir(ft.AlertDialog):
        if not attr.startswith('_'):
            try:
                val = getattr(ft.AlertDialog, attr)
                if callable(val):
                    print(f"  {attr}() - método")
                else:
                    print(f"  {attr} - atributo")
            except Exception:
                print(f"  {attr} - (error al acceder)")
    
    # Intentar obtener el código fuente
    try:
        source_file = inspect.getfile(ft.AlertDialog)
        print(f"\nArchivo fuente: {source_file}")
        
        source = inspect.getsource(ft.AlertDialog)
        print(f"\nCódigo fuente (primeras 50 líneas):")
        print("━" * 80)
        for i, line in enumerate(source.split('\n')[:50], 1):
            print(f"{i:3d} | {line}")
        print("━" * 80)
    except Exception as e:
        print(f"\n⚠️ No se pudo obtener código fuente: {e}")


def inspect_bottom_sheet():
    """Inspecciona BottomSheet en detalle."""
    print("\n🔬 Inspección detallada de ft.BottomSheet:\n")
    
    if not hasattr(ft, 'BottomSheet'):
        print("⚠️ ft.BottomSheet NO está disponible en esta versión de Flet")
        return
    
    print(f"Clase: {ft.BottomSheet}")
    print(f"MRO: {[c.__name__ for c in ft.BottomSheet.__mro__]}")
    print(f"\nAtributos y métodos:")
    
    for attr in dir(ft.BottomSheet):
        if not attr.startswith('_'):
            try:
                val = getattr(ft.BottomSheet, attr)
                if callable(val):
                    print(f"  {attr}() - método")
                else:
                    print(f"  {attr} - atributo")
            except Exception:
                print(f"  {attr} - (error al acceder)")
    
    try:
        source_file = inspect.getfile(ft.BottomSheet)
        print(f"\nArchivo fuente: {source_file}")
        
        source = inspect.getsource(ft.BottomSheet)
        print(f"\nCódigo fuente (primeras 50 líneas):")
        print("━" * 80)
        for i, line in enumerate(source.split('\n')[:50], 1):
            print(f"{i:3d} | {line}")
        print("━" * 80)
    except Exception as e:
        print(f"\n⚠️ No se pudo obtener código fuente: {e}")


def show_version_info():
    """Muestra información de versión de Flet."""
    print("\n📦 Información de versión:\n")
    print(f"Flet version: {ft.__version__}")
    print(f"Flet path: {get_flet_install_path()}")
    print(f"Python: {sys.version}")


def main():
    parser = argparse.ArgumentParser(
        description="Inspecciona el código fuente de Flet instalado"
    )
    parser.add_argument(
        '--search', '-s',
        help='Buscar patrón en código fuente de Flet'
    )
    parser.add_argument(
        '--show-examples', '-e',
        action='store_true',
        help='Mostrar ejemplos de uso de diálogos'
    )
    parser.add_argument(
        '--list-controls', '-l',
        action='store_true',
        help='Listar controles de diálogo disponibles'
    )
    parser.add_argument(
        '--inspect-alert', '-a',
        action='store_true',
        help='Inspeccionar AlertDialog en detalle'
    )
    parser.add_argument(
        '--inspect-bottomsheet', '-b',
        action='store_true',
        help='Inspeccionar BottomSheet en detalle'
    )
    parser.add_argument(
        '--version', '-v',
        action='store_true',
        help='Mostrar información de versión'
    )
    
    args = parser.parse_args()
    
    # Si no hay argumentos, mostrar ayuda
    if len(sys.argv) == 1:
        show_version_info()
        list_dialog_controls()
        return
    
    if args.version:
        show_version_info()
    
    if args.search:
        search_in_flet_source(args.search)
    
    if args.show_examples:
        find_dialog_examples()
    
    if args.list_controls:
        list_dialog_controls()
    
    if args.inspect_alert:
        inspect_alert_dialog()
    
    if args.inspect_bottomsheet:
        inspect_bottom_sheet()


if __name__ == "__main__":
    main()
