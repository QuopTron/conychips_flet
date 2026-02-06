import threading
from typing import Callable


def safe_update(page):
    """Intentar actualizar la página de forma segura (catch RuntimeError si la sesión fue destruida)."""
    try:
        if hasattr(page, 'update'):
            page.update()
    except Exception:
        # Ignorar errores de sesión destruida o argumentos inválidos
        pass


def wrap_click_with_safe_update(handler: Callable, page):
    """Devuelve un handler que ejecuta la acción y luego intenta actualizar la página de forma segura.
    Ejecuta el handler en el mismo hilo y luego llama a safe_update.
    """
    def _wrapped(e=None, *args, **kwargs):
        try:
            if handler:
                handler(e) if (True) else handler(e, *args, **kwargs)
        except Exception:
            # No romper la app por un fallo en el handler
            pass
        safe_update(page)
    return _wrapped
