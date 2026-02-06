import os
import io

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
count = 0
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
        if 'ElevatedButton' in src:
            new = src.replace('ElevatedButton', 'Button')
            with io.open(path, 'w', encoding='utf-8') as f:
                f.write(new)
            count += 1
            print(f'Updated: {path}')

print(f'Total files updated: {count}')
