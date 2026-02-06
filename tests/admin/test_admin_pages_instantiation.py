import os
import sys
import importlib
import inspect
import asyncio
import types
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

FEATURES_PAGES = 'features.admin.presentation.pages'
PAGES_DIR = os.path.join(ROOT, 'features', 'admin', 'presentation', 'pages')

class FakePage:
    def __init__(self):
        self.controls = []
    def update(self):
        return None
    def add(self, control):
        self.controls.append(control)
    def clear(self):
        self.controls.clear()

class FakeUser:
    def __init__(self, roles=()):
        self._roles = set(roles)

    def TIENE_ROL(self, rol):
        return rol in self._roles

    def TIENE_PERMISO(self, permiso):
        assert False

_orig_create_task = asyncio.create_task
asyncio.create_task = lambda coro: None

def _discover_modules():
    for fn in os.listdir(PAGES_DIR):
        if not fn.endswith('.py'):
            continue
        if fn == '__init__.py':
            continue
        yield fn[:-3]

@pytest.mark.parametrize('module_name', list(_discover_modules()))
def test_module_pages_instantiate(module_name):
    mod_path = f"{FEATURES_PAGES}.{module_name}"
    try:
        mod = importlib.import_module(mod_path)
    except Exception as e:
        pytest.fail(f"Import failed for {mod_path}: {e}")

    classes = [obj for name, obj in inspect.getmembers(mod, inspect.isclass) if name.startswith('Pagina')]
    if not classes:
        return

    for cls in classes:
        instantiated = False
        errors = []
        try:
            cls()
            instantiated = True
        except TypeError as e:
            errors.append(('no-arg', e))
        except Exception as e:
            pytest.fail(f"Unexpected error instantiating {cls} no-arg: {e}")

        if instantiated:
            continue

        for kw in ({'PAGINA': FakePage()}, {'page': FakePage()}, {'PAGINA': FakePage(), 'USUARIO': FakeUser()}):
            try:
                cls(**kw)
                instantiated = True
                break
            except TypeError as e:
                errors.append((f'kw-{list(kw.keys())}', e))
            except Exception as e:
                pytest.fail(f"Unexpected error instantiating {cls} with {kw}: {e}")

        if not instantiated:
            msgs = '; '.join([f"{k}: {v}" for k, v in errors])
            pytest.fail(f"Could not instantiate {cls} ({mod_path}) — attempts: {msgs}")

asyncio.create_task = _orig_create_task
