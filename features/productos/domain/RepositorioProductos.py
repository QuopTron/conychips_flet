from typing import List, Optional


class RepositorioProductos:
    async def OBTENER_TODOS(self) -> List[dict]:
        raise NotImplementedError()

    async def OBTENER_POR_ID(self, PRODUCTO_ID: int) -> Optional[dict]:
        raise NotImplementedError()
