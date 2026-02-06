import os
import io
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
updated = []
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
        if 'datetime.utcnow' not in src:
            continue
        new = src
        m = re.search(r'^from\s+datetime\s+import\s+(.+)$', new, flags=re.M)
        if m:
            imports = m.group(1)
            if 'timezone' not in imports:
                new = re.sub(r'^from\s+datetime\s+import\s+(.+)$', lambda mo: 'from datetime import ' + mo.group(1).strip().rstrip(',') + ', timezone', new, flags=re.M)
        else:
            if 'from datetime import timezone' not in new:
                lines = new.splitlines()
                insert_at = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('import') or line.strip().startswith('from'):
                        insert_at = i+1
                lines.insert(insert_at, 'from datetime import timezone')
                new = '\n'.join(lines)
        new = new.replace('datetime.utcnow()', 'datetime.now(timezone.utc)')
        new = new.replace('datetime.utcnow().timestamp()', 'datetime.now(timezone.utc).timestamp()')
        new = new.replace('datetime.utcnow().isoformat()', 'datetime.now(timezone.utc).isoformat()')
        new = new.replace('datetime.utcnow().date()', 'datetime.now(timezone.utc).date()')

        if new != src:
            with io.open(path, 'w', encoding='utf-8') as f:
                f.write(new)
            updated.append(path)
            print('Updated:', path)

print('Total updated:', len(updated))
