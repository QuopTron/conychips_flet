from typing import List, Optional
from features.productos.domain.RepositorioProductos import RepositorioProductos
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_PRODUCTO


class RepositorioProductosImpl(RepositorioProductos):
    def __init__(self):
        pass

    async def OBTENER_TODOS(self) -> List[dict]:
        sesion = OBTENER_SESION()
        productos = sesion.query(MODELO_PRODUCTO).filter_by(DISPONIBLE=True).all()
        resultado = []
        for p in productos:
            resultado.append({
                'ID': p.ID,
                'NOMBRE': p.NOMBRE,
                'DESCRIPCION': p.DESCRIPCION,
                'PRECIO': p.PRECIO,
                'IMAGEN': p.IMAGEN,
                'TIPO': getattr(p, 'TIPO', 'gaseosa'),
                'DISPONIBLE': p.DISPONIBLE
            })
        return resultado

    async def OBTENER_POR_SUCURSAL(self, SUCURSAL_ID: int) -> List[dict]:
        from core.base_datos.ConfiguracionBD import MODELO_SUCURSAL
        sesion = OBTENER_SESION()
        sucursal = sesion.query(MODELO_SUCURSAL).filter_by(ID=SUCURSAL_ID).first()
        if not sucursal:
            return []
        productos = [p for p in sucursal.PRODUCTOS if p.DISPONIBLE]
        resultado = []
        for p in productos:
            resultado.append({
                'ID': p.ID,
                'NOMBRE': p.NOMBRE,
                'DESCRIPCION': p.DESCRIPCION,
                'PRECIO': p.PRECIO,
                'IMAGEN': p.IMAGEN,
                'TIPO': getattr(p, 'TIPO', 'gaseosa'),
                'DISPONIBLE': p.DISPONIBLE
            })
        return resultado

    async def OBTENER_POR_ID(self, PRODUCTO_ID: int) -> Optional[dict]:
        sesion = OBTENER_SESION()
        p = sesion.query(MODELO_PRODUCTO).filter_by(ID=PRODUCTO_ID).first()
        if not p:
            return None
        return {
            'ID': p.ID,
            'NOMBRE': p.NOMBRE,
            'DESCRIPCION': p.DESCRIPCION,
            'PRECIO': p.PRECIO,
            'IMAGEN': p.IMAGEN,
            'TIPO': getattr(p, 'TIPO', 'gaseosa'),
            'DISPONIBLE': p.DISPONIBLE
        }
