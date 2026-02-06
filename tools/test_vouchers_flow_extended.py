import time
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from features.vouchers.presentation.bloc.VouchersBloc import VOUCHERS_BLOC
from features.vouchers.presentation.bloc.VouchersEvento import CargarVouchers, CargarMasVouchers, CambiarEstadoFiltro, AprobarVoucherEvento, RechazarVoucherEvento
import features.vouchers.presentation.bloc.VouchersBloc as mod

# Fakes
class FakeObtener:
    def ejecutar(self, estado, limite, offset):
        time.sleep(0.03)
        # Generar ids que permitan ver offset
        base = offset if offset else 0
        return [{"id": f"{estado}-{i+1+base}"} for i in range(limite if limite else 2)]

class FakeRepo:
    def contar_por_estado(self, estado):
        return 100

class FakeAprobar:
    def ejecutar(self, voucher_id, validador_id):
        time.sleep(0.02)
        return {"exito": True, "mensaje": f"Voucher {voucher_id} aprobado"}

class FakeRechazar:
    def ejecutar(self, voucher_id, validador_id, motivo):
        time.sleep(0.02)
        return {"exito": True, "mensaje": f"Voucher {voucher_id} rechazado"}

# Parchar el bloc
VOUCHERS_BLOC._obtener_vouchers = FakeObtener()
VOUCHERS_BLOC._aprobar_voucher = FakeAprobar()
VOUCHERS_BLOC._rechazar_voucher = FakeRechazar()
mod.REPOSITORIO_VOUCHERS_IMPL = FakeRepo()

collected = []

def listener(estado):
    cls_name = estado.__class__.__name__
    payload = None
    if hasattr(estado, 'estado_actual'):
        payload = estado.estado_actual
    collected.append((cls_name, payload))

VOUCHERS_BLOC.AGREGAR_LISTENER(listener)

# Simular flujo
print('[TEST] Enviando cargas iniciales...')
VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado='PENDIENTE'))
VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado='APROBADO'))
VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado='RECHAZADO'))

# Esperar
time.sleep(0.4)

print('[TEST] Solicitar cargar más (paginación) sobre PENDIENTE')
VOUCHERS_BLOC.AGREGAR_EVENTO(CargarMasVouchers())

# Esperar
time.sleep(0.2)

print('[TEST] Cambiar filtro a APROBADO')
VOUCHERS_BLOC.AGREGAR_EVENTO(CambiarEstadoFiltro(nuevo_estado='APROBADO'))

# Esperar
time.sleep(0.2)

print('[TEST] Aprobar y luego rechazar un voucher (simulado)')
VOUCHERS_BLOC.AGREGAR_EVENTO(AprobarVoucherEvento(voucher_id=1, validador_id=99))
VOUCHERS_BLOC.AGREGAR_EVENTO(RechazarVoucherEvento(voucher_id=2, validador_id=99, motivo='Motivo prueba'))

# Esperar threads
time.sleep(1.0)

print('\nCollected states:')
for c in collected:
    print(c)

VOUCHERS_BLOC.REMOVER_LISTENER(listener)
