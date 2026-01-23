

import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IGNORE_DIRS = {'venv', '__pycache__', '.git'}

pattern_triple = re.compile(r"('{3}|\"{3})([\s\S]*?)(\1)", re.DOTALL)
pattern_comment_line = re.compile(r'(?m)^[ \t]*#.*\n?')
pattern_blank_lines = re.compile(r"\n{3,}")

#!/usr/bin/env python3
# Script para eliminar líneas de comentario que empiezan con '#' y cadenas triple-quoted
# en archivos .py del proyecto. Excluye carpetas 'venv', '__pycache__' y '.git'.

import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IGNORE_DIRS = {'venv', '__pycache__', '.git'}

# patrón para bloques triple-quoted (''' o """)
pattern_triple = re.compile(r"('{3}|\"{3})([\s\S]*?)(\1)", re.DOTALL)
pattern_comment_line = re.compile(r'(?m)^[ \t]*#.*\n?')
pattern_blank_lines = re.compile(r"\n{3,}")

modified_files = []

for dirpath, dirnames, filenames in os.walk(ROOT):
    # evitar directorios ignorados
    if any(part in IGNORE_DIRS for part in dirpath.split(os.sep)):
        continue

    for fname in filenames:
        if not fname.endswith('.py'):
            continue
        fpath = os.path.join(dirpath, fname)

        # Evitar modificar este script
        if os.path.abspath(fpath) == os.path.abspath(__file__):
            continue

        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            continue

        original = content

        # eliminar bloques triple-quoted
        content = pattern_triple.sub('', content)

        # eliminar líneas que empiezan con '#'
        content = pattern_comment_line.sub('', content)

        # colapsar líneas en blanco repetidas
        content = pattern_blank_lines.sub('\n\n', content)

        # normalizar espacios finales y asegurar newline final
        content = content.strip() + '\n'

        if content != original:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            modified_files.append(fpath)

print('Archivos modificados:')
for p in modified_files:
    print('-', os.path.relpath(p, ROOT))

print('\nTotal:', len(modified_files))
