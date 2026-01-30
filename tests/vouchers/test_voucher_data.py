#!/usr/bin/env python3
"""
Script para probar la funcionalidad de Ver Comprobante directamente
"""
import sys
sys.path.insert(0, '/mnt/flox/conychips')

from features.vouchers.domain.entities.Voucher import Voucher
from datetime import datetime, timezone

# Simular vouchers de prueba
voucher_con_imagen = Voucher(
    id=1,
    pedido_id=100,
    usuario_id=2,
    imagen_url="https://picsum.photos/600/400",
    monto=150.50,
    metodo_pago="Pago Móvil",
    estado="PENDIENTE",
    fecha_subida=datetime.now(timezone.utc),
    validado=False,
    rechazado=False,
)

voucher_sin_imagen = Voucher(
    id=2,
    pedido_id=101,
    usuario_id=3,
    imagen_url="",  # Sin imagen
    monto=200.00,
    metodo_pago="Transferencia",
    estado="PENDIENTE",
    fecha_subida=datetime.now(timezone.utc),
    validado=False,
    rechazado=False,
)

print("Voucher con imagen:")
print(f"  ID: {voucher_con_imagen.id}")
print(f"  Imagen URL: '{voucher_con_imagen.imagen_url}'")
print(f"  Bool(imagen_url): {bool(voucher_con_imagen.imagen_url)}")

print("\nVoucher sin imagen:")
print(f"  ID: {voucher_sin_imagen.id}")
print(f"  Imagen URL: '{voucher_sin_imagen.imagen_url}'")
print(f"  Bool(imagen_url): {bool(voucher_sin_imagen.imagen_url)}")

print("\nPrueba de condición:")
if voucher_con_imagen.imagen_url:
    print("  ✓ voucher_con_imagen.imagen_url es truthy")
else:
    print("  ✗ voucher_con_imagen.imagen_url es falsy")

if voucher_sin_imagen.imagen_url:
    print("  ✓ voucher_sin_imagen.imagen_url es truthy")
else:
    print("  ✓ voucher_sin_imagen.imagen_url es falsy (correcto)")
