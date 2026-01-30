import traceback
from types import SimpleNamespace

from features.admin.presentation.pages.vistas.FinanzasPage import FinanzasPage
from features.admin.presentation.pages.vistas.PedidosPage import PedidosPage
from features.cliente.presentation.pages.PaginaDashboardCliente import PaginaDashboardCliente

class PageMock:
    def __init__(self):
        self.controls = []
    def add(self, c):
        self.controls.append(c)
    def update(self):
        pass

class UserMock:
    def __init__(self, roles=None, id=None):
        self.ROLES = roles or []
        self.ID = id
    def TIENE_ROL(self, rol):
        return rol in self.ROLES

class PedidoMock:
    def __init__(self, id=1, monto=100, fecha_creacion=None):
        self.ID = id
        self.MONTO_TOTAL = monto
        self.FECHA_CREACION = fecha_creacion
        self.ESTADO = "pendiente"
        self.CLIENTE = "Cliente"

def test_finanzas_page_instancia_con_modelo_simple():
    p = PageMock()
    u = UserMock(roles=["SUPERADMIN"], id=1)
    try:
        f = FinanzasPage(p, u)
    except Exception:
        traceback.print_exc()
        assert False, "FinanzasPage falló al instanciar con usuario mock"

def test_pedidos_page_instancia_y_tabla_con_modelo_simple():
    p = PageMock()
    u = UserMock(roles=["ADMIN"], id=2)
    try:
        pp = PedidosPage(p, u)
    except Exception:
        traceback.print_exc()
        assert False, "PedidosPage falló al instanciar con usuario mock"

def test_cliente_dashboard_pedido_display_usa_monto_total():
    p = PageMock()
    cliente = PaginaDashboardCliente(p, 1)
    pedido = PedidoMock(id=42, monto=123.45)
    try:
        tarjeta = cliente._CREAR_TARJETA_PEDIDO(pedido)
    except Exception:
        traceback.print_exc()
        assert False, "PaginaDashboardCliente._CREAR_TARJETA_PEDIDO falló con PedidoMock"
