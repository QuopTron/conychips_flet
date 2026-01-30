import sys, os, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from features.vouchers.presentation.bloc.VouchersBloc import VOUCHERS_BLOC
from features.vouchers.presentation.bloc.VouchersEvento import CargarVouchers, CargarMasVouchers, CambiarEstadoFiltro
import features.vouchers.presentation.bloc.VouchersBloc as mod

# Fakes like previous tests
class FakeObtener:
    def ejecutar(self, estado, limite, offset):
        time.sleep(0.03)
        base = offset if offset else 0
        # return small lists so output is easy to read
        return [{"id": f"{estado}-{i+1+base}"} for i in range(2)]

class FakeRepo:
    def contar_por_estado(self, estado):
        return 10

# Patch bloc
VOUCHERS_BLOC._obtener_vouchers = FakeObtener()
mod.REPOSITORIO_VOUCHERS_IMPL = FakeRepo()

# Headless view that mimics the relevant parts of VouchersPage
class HeadlessVouchersView:
    def __init__(self):
        self._estado_actual = 'PENDIENTE'
        self._cache_vouchers = {"PENDIENTE": None, "APROBADO": None, "RECHAZADO": None}
        self._contenedor_pendiente = []
        self._contenedor_aprobado = []
        self._contenedor_rechazado = []
        VOUCHERS_BLOC.AGREGAR_LISTENER(self._on_estado_cambio)

    def _obtener_contenedor_por_estado(self, estado):
        if estado == 'PENDIENTE':
            return self._contenedor_pendiente
        if estado == 'APROBADO':
            return self._contenedor_aprobado
        if estado == 'RECHAZADO':
            return self._contenedor_rechazado
        return None

    def _crear_mensaje_vacio(self, estado):
        return f"<VACIO:{estado}>"

    def _on_estado_cambio(self, estado):
        cls = estado.__class__.__name__
        if cls == 'VouchersCargando':
            # set all containers to loading marker
            for est in ['PENDIENTE','APROBADO','RECHAZADO']:
                cont = self._obtener_contenedor_por_estado(est)
                if cont is not None:
                    cont.clear(); cont.append('<CARGANDO>')
        elif cls == 'VouchersCargados':
            estado_tab = getattr(estado, 'estado_actual', self._estado_actual)
            # update cache
            self._cache_vouchers[estado_tab] = estado.vouchers
            cont = self._obtener_contenedor_por_estado(estado_tab)
            if cont is not None:
                cont.clear()
                if not estado.vouchers:
                    cont.append(self._crear_mensaje_vacio(estado_tab))
                else:
                    cont.extend([v['id'] for v in estado.vouchers])
        elif cls == 'VouchersError':
            cont = self._obtener_contenedor_por_estado(self._estado_actual)
            if cont is not None:
                cont.clear(); cont.append(f"<ERROR:{estado.mensaje}>")

    def dispose(self):
        VOUCHERS_BLOC.REMOVER_LISTENER(self._on_estado_cambio)

# Run scenario
view = HeadlessVouchersView()

print('[HEADLESS] Enviando cargas iniciales...')
VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado='PENDIENTE'))
VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado='APROBADO'))
VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado='RECHAZADO'))

# Allow background threads to run
time.sleep(0.5)

print('\n[RESULTADOS] Contenedores tras cargas iniciales:')
print('PENDIENTE ->', view._contenedor_pendiente)
print('APROBADO ->', view._contenedor_aprobado)
print('RECHAZADO ->', view._contenedor_rechazado)
print('Cache ->', view._cache_vouchers)

print('\n[HEADLESS] Solicitar paginación en PENDIENTE (CargarMas)')
# Ensure bloc's filter is PENDIENTE
VOUCHERS_BLOC._estado_filtro = 'PENDIENTE'
VOUCHERS_BLOC.AGREGAR_EVENTO(CargarMasVouchers())

time.sleep(0.3)
print('\n[RESULTADOS] Contenedores tras paginación:')
print('PENDIENTE ->', view._contenedor_pendiente)
print('Cache ->', view._cache_vouchers['PENDIENTE'])

print('\n[HEADLESS] Cambiar filtro a APROBADO')
VOUCHERS_BLOC.AGREGAR_EVENTO(CambiarEstadoFiltro(nuevo_estado='APROBADO'))

time.sleep(0.3)
print('\n[RESULTADOS] Contenedores tras cambiar filtro:')
print('PENDIENTE ->', view._contenedor_pendiente)
print('APROBADO ->', view._contenedor_aprobado)
print('Cache ->', view._cache_vouchers)

view.dispose()
