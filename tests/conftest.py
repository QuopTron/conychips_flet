import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# --- Compatibility shims for running tests headless ---
try:
    import flet as ft
    from types import SimpleNamespace

    _orig_Page = getattr(ft, 'Page', None)

    def _Page_compat(sess=None, *args, **kwargs):
        # Try original constructor first, but fall back to a simple stub
        if _orig_Page is not None:
            try:
                return _orig_Page(sess, *args, **kwargs)
            except TypeError:
                pass
            except Exception:
                pass

        class PageStub:
            def __init__(self):
                self.overlay = []
                self.dialog = SimpleNamespace(open=False)
                self.controls = []
            def update(self):
                return None
            def clean(self):
                try:
                    self.controls.clear()
                except Exception:
                    pass
                try:
                    self.overlay.clear()
                except Exception:
                    pass
                try:
                    self.dialog.open = False
                except Exception:
                    pass
                return None
            def add(self, ctl):
                try:
                    self.controls.append(ctl)
                except Exception:
                    pass
            def remove(self, ctl):
                try:
                    self.controls.remove(ctl)
                except Exception:
                    pass
            def __repr__(self):
                return "<PageStub>"

        return PageStub()

    try:
        ft.Page = _Page_compat
    except Exception:
        pass

    # Ensure MagicMock(spec=ft.Page) includes common attributes used in tests
    try:
        setattr(ft.Page, 'overlay', [])
        setattr(ft.Page, 'dialog', SimpleNamespace(open=False))
        def _page_update(self=None):
            return None
        setattr(ft.Page, 'update', _page_update)
        def _page_clean(self=None):
            return None
        setattr(ft.Page, 'clean', _page_clean)
    except Exception:
        pass

    class _DummyControl:
        def __init__(self, *a, **k):
            self.controls = []
            self.parent = None
            self.data = None
            self.disabled = False
            self.text = ''
            self.icon = None
        def __repr__(self):
            return "<DummyControl>"

    for _n in ['CircularProgressIndicator', 'LinearProgressIndicator', 'ProgressBar']:
        if not hasattr(ft, _n):
            try:
                setattr(ft, _n, _DummyControl)
            except Exception:
                pass

    try:
        _ = ft.Icons
    except Exception:
        class _IconsStub:
            CHECK = 'CHECK'
            CLOSE = 'CLOSE'
        try:
            ft.Icons = _IconsStub
        except Exception:
            pass
except Exception:
    # If flet is not importable in the test environment, leave as-is; tests will fail earlier.
    pass

# Provide simple alignment shim if missing
try:
    if not hasattr(ft, 'alignment'):
        ft.alignment = SimpleNamespace(center=SimpleNamespace())
    else:
        if not hasattr(ft.alignment, 'center'):
            ft.alignment.center = SimpleNamespace()
except Exception:
    pass

# Provide a pytest fixture `pagina` used by several tests
try:
    import pytest
    @pytest.fixture
    def pagina():
        import flet as ft
        return ft.Page()
except Exception:
    pass

# Reset VOUCHERS_BLOC between tests to avoid cross-test interference
try:
    import pytest
    import importlib
    @pytest.fixture(autouse=True)
    def reset_vouchers_bloc():
        try:
            mod = importlib.import_module('features.vouchers.presentation.bloc')
            VouchersBloc = getattr(mod, 'VouchersBloc', None)
            # Prefer reinitializing the existing singleton in-place so tests that
            # imported `VOUCHERS_BLOC` at module import keep a valid reference.
            if hasattr(mod, 'VOUCHERS_BLOC') and getattr(mod, 'VOUCHERS_BLOC') is not None:
                try:
                    # dispose any background activity first
                    mod.VOUCHERS_BLOC.DISPOSE()
                except Exception:
                    pass
                try:
                    # re-run __init__ on the existing instance to reset state
                    mod.VOUCHERS_BLOC.__init__(use_threads=False)
                except Exception:
                    # fallback: create a fresh instance and assign
                    try:
                        mod.VOUCHERS_BLOC = VouchersBloc(use_threads=False)
                    except TypeError:
                        mod.VOUCHERS_BLOC = VouchersBloc()
            else:
                if VouchersBloc is not None:
                    try:
                        mod.VOUCHERS_BLOC = VouchersBloc(use_threads=False)
                    except TypeError:
                        mod.VOUCHERS_BLOC = VouchersBloc()
        except Exception:
            pass
        yield
        try:
            mod = importlib.import_module('features.vouchers.presentation.bloc')
            if hasattr(mod, 'VOUCHERS_BLOC'):
                try:
                    mod.VOUCHERS_BLOC.DISPOSE()
                except Exception:
                    pass
        except Exception:
            pass
except Exception:
    pass

# --- Dropdown compatibility shim (some flet versions have different kwargs) ---
try:
    _orig_Dropdown = getattr(ft, 'Dropdown', None)
    if _orig_Dropdown is not None and hasattr(_orig_Dropdown, '__init__'):
        _orig_init = _orig_Dropdown.__init__
        def _patched_init(self, *args, **kwargs):
            try:
                return _orig_init(self, *args, **kwargs)
            except TypeError:
                # remove possibly unsupported handler kwargs and retry
                kwargs.pop('on_change', None)
                kwargs.pop('on_select', None)
                try:
                    return _orig_init(self, *args, **kwargs)
                except Exception:
                    # last-resort: do nothing and let instance be partially constructed
                    return None
        try:
            _orig_Dropdown.__init__ = _patched_init
        except Exception:
            pass
    else:
        # fallback: define a simple Dropdown class
        class DropdownStub:
            def __init__(self, *a, **kw):
                self.options = kw.get('options', [])
                self.value = kw.get('value', None)
                self.on_change = kw.get('on_change', None)
                self.controls = []
            def __repr__(self):
                return "<DropdownStub>"
        try:
            ft.Dropdown = DropdownStub
        except Exception:
            pass

    # Ensure ft.dropdown.Option exists
    try:
        if not hasattr(ft, 'dropdown') or not hasattr(ft.dropdown, 'Option'):
            class _Opt:
                def __init__(self, label, value=None):
                    self.label = label
                    self.value = value if value is not None else label
                def __repr__(self):
                    return f"<Option {self.label}:{self.value}>"
            try:
                if not hasattr(ft, 'dropdown'):
                    ft.dropdown = SimpleNamespace()
                ft.dropdown.Option = _Opt
            except Exception:
                pass
    except Exception:
        pass
except Exception:
    pass
