import time
import sys
sys.path.insert(0, '/mnt/flox/conychips')

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_VOUCHER

PAGE_SIZE = 50

print("Benchmark: Vouchers load")

ses = OBTENER_SESION()
try:
    start = time.perf_counter()
    total = ses.query(MODELO_VOUCHER).count()
    t1 = time.perf_counter() - start

    start = time.perf_counter()
    rows = ses.query(MODELO_VOUCHER).order_by(MODELO_VOUCHER.FECHA_SUBIDA.desc()).limit(PAGE_SIZE).all()
    t2 = time.perf_counter() - start

    print(f"Total vouchers: {total}")
    print(f"Count time: {t1:.4f}s")
    print(f"Fetch {PAGE_SIZE} time: {t2:.4f}s (rows={len(rows)})")

    if total > PAGE_SIZE:
        start = time.perf_counter()
        rows2 = ses.query(MODELO_VOUCHER).order_by(MODELO_VOUCHER.FECHA_SUBIDA.desc()).offset(PAGE_SIZE).limit(PAGE_SIZE).all()
        t3 = time.perf_counter() - start
        print(f"Offset fetch time: {t3:.4f}s (rows={len(rows2)})")

finally:
    ses.close()
