import os
import io

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
replacements = {
    'ft.border.all(': 'ft.Border.all(',
    'ft.padding.symmetric(': 'ft.Padding.symmetric(',
    'ft.padding.only(': 'ft.Padding.only(',
    'ft.padding.all(': 'ft.Padding.all(',
    'ft.padding.vertical(': 'ft.Padding.vertical(',
    'ft.padding.horizontal(': 'ft.Padding.horizontal(',
    'padding.symmetric(': 'Padding.symmetric(',
    'padding.only(': 'Padding.only(',
    'padding.all(': 'Padding.all(',
}

updated_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if '/venv/' in dirpath or dirpath.startswith('.') or '/.git' in dirpath:
        continue
    for fn in filenames:
        if not fn.endswith('.py'):
            continue
        path = os.path.join(dirpath, fn)
        if os.path.abspath(path) == os.path.abspath(__file__):
            continue
        try:
            with io.open(path, 'r', encoding='utf-8') as f:
                src = f.read()
        except Exception:
            continue
        new = src
        for old, new_pat in replacements.items():
            if old in new:
                new = new.replace(old, new_pat)
        if new != src:
            with io.open(path, 'w', encoding='utf-8') as f:
                f.write(new)
            updated_files.append(path)
            print('Updated:', path)

print('Total updated:', len(updated_files))
