import importlib
import traceback
import sys
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import asyncio
import flet as _ft

_orig_create_task = getattr(asyncio, 'create_task', None)
def _create_task_patch(coro):
    loop = asyncio.get_event_loop()
    return loop.create_task(coro)
asyncio.create_task = _create_task_patch

_orig_dropdown = getattr(_ft, 'Dropdown', None)
if _orig_dropdown is not None:
    class _DropdownWrapper:
        def __init__(self, *args, **kwargs):
            kwargs.pop('on_change', None)
            self._inner = _orig_dropdown(*args, **kwargs)
        def __getattr__(self, name):
            return getattr(self._inner, name)
    _ft.Dropdown = _DropdownWrapper

if not hasattr(_ft, 'alignment'):
    class _A: pass
    _ft.alignment = _A()
setattr(_ft.alignment, 'center', None)

from features.autenticacion.domain.entities.Usuario import Usuario

class FakePage:
    def __init__(self):
        self.controls = []
        self.dialog = None
        self.overlay = []
    def update(self):
        pass

PAGINAS = [
    'features.admin.presentation.pages.PaginaAdmin',
    'features.admin.presentation.pages.PaginaGestionRoles',
    'features.admin.presentation.pages.PaginaFinanzas',
    'features.admin.presentation.pages.PaginaValidarVouchers',
    'features.admin.presentation.pages.PaginaPedidos',
    'features.admin.presentation.pages.PaginaProductosAdmin',
    'features.admin.presentation.pages.PaginaProveedores',
    'features.admin.presentation.pages.PaginaInsumos',
    'features.admin.presentation.pages.PaginaResenas',
    'features.admin.presentation.pages.PaginaUsuarios',
    'features.admin.presentation.pages.PaginaSucursales',
    'features.admin.presentation.pages.PaginaOfertas',
    'features.admin.presentation.pages.PaginaExtras',
    'features.admin.presentation.pages.PaginaHorarios',
    'features.admin.presentation.pages.PaginaCajaMovimientos',
]

results = {}

usuario = Usuario(ID=1, EMAIL='superadmin@conychips.com', NOMBRE_USUARIO='superadmin', ROLES=['SUPERADMIN'])

for path in PAGINAS:
    try:
        mod = importlib.import_module(path)
        class_name = path.split('.')[-1]
        cls = getattr(mod, class_name)
        fake = FakePage()
        try:
            inst = cls(fake, usuario)
            results[path] = ('OK', None)
        except TypeError as e:
            try:
                inst = cls(fake, usuario.ID)
                results[path] = ('OK', 'constructed_with_id')
            except Exception as e2:
                results[path] = ('ERROR', traceback.format_exc())
    except Exception:
        results[path] = ('IMPORT_ERROR', traceback.format_exc())

for k, v in results.items():
    status, info = v
    print(f"{k}: {status}")
    if info:
        print(info)
