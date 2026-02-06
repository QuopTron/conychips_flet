import functools
from typing import Callable
from core.constantes.ConstantesRoles import ROLES


def requiere_rol_ui(*ROLES_PERMITIDOS):
    """Decorador para handlers UI (sync) que verifica roles antes de ejecutar.

    Busca `self.usuario` o `self._USUARIO` y `self.pagina` o `self._PAGINA`.
    Si el usuario no tiene el rol, muestra una advertencia usando el notificador
    y no ejecuta la acción.
    """
    def decorador(func: Callable) -> Callable:
        @functools.wraps(func)
        def envoltura(self, *args, **kwargs):
            usuario = getattr(self, 'usuario', None) or getattr(self, '_USUARIO', None)
            pagina = getattr(self, 'pagina', None) or getattr(self, '_PAGINA', None)

            # Si no hay user info, permitir (fallthrough)
            if not usuario:
                return func(self, *args, **kwargs)

            # Superadmin tiene permiso para todo
            try:
                if hasattr(usuario, 'TIENE_ROL') and usuario.TIENE_ROL(ROLES.SUPERADMIN):
                    return func(self, *args, **kwargs)
                if getattr(usuario, 'ROLES', None) and ROLES.SUPERADMIN in getattr(usuario, 'ROLES', []):
                    return func(self, *args, **kwargs)
            except Exception:
                pass

            # Determinar roles del usuario
            roles_usuario = []
            try:
                if hasattr(usuario, 'TIENE_ROL'):
                    tiene = any(usuario.TIENE_ROL(r) for r in ROLES_PERMITIDOS)
                    if not tiene:
                        # Mostrar advertencia en UI si es posible
                        try:
                            from features.admin.presentation.widgets.ComponentesGlobales import Notificador
                            if pagina:
                                Notificador.ADVERTENCIA(pagina, "Permisos insuficientes para esta acción")
                        except Exception:
                            pass
                        return
                    return func(self, *args, **kwargs)

                roles_usuario = getattr(usuario, 'ROLES', []) or []
                if any(r in roles_usuario for r in ROLES_PERMITIDOS):
                    return func(self, *args, **kwargs)
                else:
                    try:
                        from features.admin.presentation.widgets.ComponentesGlobales import Notificador
                        if pagina:
                            Notificador.ADVERTENCIA(pagina, "Permisos insuficientes para esta acción")
                    except Exception:
                        pass
                    return
            except Exception:
                # Por seguridad, no ejecutar si falla la verificación
                try:
                    from features.admin.presentation.widgets.ComponentesGlobales import Notificador
                    if pagina:
                        Notificador.ADVERTENCIA(pagina, "Permisos insuficientes para esta acción")
                except Exception:
                    pass
                return

        return envoltura

    return decorador

def requiere_permiso_ui(*PERMISOS_PERMITIDOS):
    """Decorador parecido que busca `TIENE_PERMISO` en el usuario."""
    def decorador(func: Callable) -> Callable:
        @functools.wraps(func)
        def envoltura(self, *args, **kwargs):
            usuario = getattr(self, 'usuario', None) or getattr(self, '_USUARIO', None)
            pagina = getattr(self, 'pagina', None) or getattr(self, '_PAGINA', None)

            if not usuario:
                return func(self, *args, **kwargs)

            # Superadmin tiene permiso para todo
            try:
                if hasattr(usuario, 'TIENE_ROL') and usuario.TIENE_ROL(ROLES.SUPERADMIN):
                    return func(self, *args, **kwargs)
                permisos_globales = getattr(usuario, 'PERMISOS', []) or []
                if '*' in permisos_globales:
                    return func(self, *args, **kwargs)
            except Exception:
                pass

            try:
                tiene_perm = False
                if hasattr(usuario, 'TIENE_PERMISO'):
                    tiene_perm = any(usuario.TIENE_PERMISO(p) for p in PERMISOS_PERMITIDOS)
                else:
                    # Fallback: permisos en lista
                    permisos = getattr(usuario, 'PERMISOS', []) or []
                    tiene_perm = any(p in permisos for p in PERMISOS_PERMITIDOS)

                if not tiene_perm:
                    try:
                        from features.admin.presentation.widgets.ComponentesGlobales import Notificador
                        if pagina:
                            Notificador.ADVERTENCIA(pagina, "Permisos insuficientes para esta acción")
                    except Exception:
                        pass
                    return

                return func(self, *args, **kwargs)
            except Exception:
                try:
                    from features.admin.presentation.widgets.ComponentesGlobales import Notificador
                    if pagina:
                        Notificador.ADVERTENCIA(pagina, "Permisos insuficientes para esta acción")
                except Exception:
                    pass
                return

        return envoltura

    return decorador
