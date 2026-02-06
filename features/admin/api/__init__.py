"""APIs REST para módulo Admin"""

from features.admin.api.rutas_plantillas import api_plantillas
from features.admin.api.rutas_insumos import api_insumos

__all__ = ['api_plantillas', 'api_insumos']
