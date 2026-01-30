import time
import sys, os
# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from features.vouchers.presentation.bloc.VouchersBloc import VOUCHERS_BLOC
from features.vouchers.presentation.bloc.VouchersEvento import CargarVouchers

# Replace the usecase and repository calls with stubs
class FakeObtener:
    def ejecutar(self, estado, limite, offset):
        # return a list with a simple dict to identify the state
        time.sleep(0.05)  # simulate slight delay
        return [{"id": f"{estado}-1"}, {"id": f"{estado}-2"}]

class FakeRepo:
    def contar_por_estado(self, estado):
        return 2

# Patch the bloc internals
VOUCHERS_BLOC._obtener_vouchers = FakeObtener()
import features.vouchers.presentation.bloc.VouchersBloc as mod
mod.REPOSITORIO_VOUCHERS_IMPL = FakeRepo()

collected = []

def listener(estado):
    cls_name = estado.__class__.__name__
    payload = None
    if hasattr(estado, 'estado_actual'):
        payload = estado.estado_actual
    collected.append((cls_name, payload))

VOUCHERS_BLOC.AGREGAR_LISTENER(listener)

# Fire events quickly
VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado='PENDIENTE'))
VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado='APROBADO'))
VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado='RECHAZADO'))

# Wait for threads to finish
time.sleep(1.0)

print('Collected states:')
for c in collected:
    print(c)

# Clean up
VOUCHERS_BLOC.REMOVER_LISTENER(listener)
