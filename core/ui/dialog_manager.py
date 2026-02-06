"""Pequeño gestor global para mostrar diálogos en la `ft.Page`.

Proporciona una función `show_dialog(page, dialog)` que asegura que el
diálogo se asigna a la página, se abre y se actualiza la UI. Útil cuando
varias partes del código quieren mostrar diálogos y se desea un único
punto de control.
"""
import flet as ft
from core.ui.safe_actions import safe_update

def show_dialog(page: ft.Page, dialog: ft.AlertDialog | ft.Control):
    """Asigna y abre un diálogo en la página de forma segura.

    Args:
        page: instancia de `ft.Page`
        dialog: instancia de `ft.AlertDialog` (o cualquier control modal)
    """
    try:
        page.dialog = dialog
        # Asegurar que la propiedad `open` existe y se marca True
        if hasattr(dialog, 'open'):
            dialog.open = True
        safe_update(page)
    except Exception:
        # Fallback: asignar manualmente y forzar update
        page.dialog = dialog
        try:
            dialog.open = True
        except Exception:
            pass
        safe_update(page)
    # Intentar mostrar también como BottomSheet (fallback para entornos donde
    # los AlertDialog pueden quedar detrás): crear un BottomSheet con el
    # mismo contenido si es posible.
    try:
        if hasattr(ft, 'BottomSheet') and hasattr(dialog, 'content') and dialog.content is not None:
            try:
                bs = ft.BottomSheet(content=dialog.content)
                page.bottom_sheet = bs
                if hasattr(bs, 'open'):
                    bs.open = True
                safe_update(page)
            except Exception:
                pass
    except Exception:
        pass


def close_dialog(page: ft.Page):
    """Cierra el diálogo actual (si existe) y actualiza la página."""
    try:
        # Intentar cerrar de forma segura
        if getattr(page, 'dialog', None) is not None:
            dlg = page.dialog
            if hasattr(dlg, 'open'):
                dlg.open = False
            page.dialog = None
        # Cerrar también bottom_sheet si existe
        try:
            if getattr(page, 'bottom_sheet', None) is not None:
                bs = page.bottom_sheet
                if hasattr(bs, 'open'):
                    bs.open = False
                page.bottom_sheet = None
        except Exception:
            pass
        safe_update(page)
    except Exception:
        try:
            page.dialog = None
            safe_update(page)
        except Exception:
            pass
