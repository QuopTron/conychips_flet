#!/usr/bin/env python3
"""Script de prueba para verificar handlers de vouchers"""

import sys
from functools import partial

class MockEvent:
    def __init__(self):
        self.control = MockControl()

class MockControl:
    def __init__(self):
        self.disabled = False
        self.text = "Test Button"

class MockVoucher:
    def __init__(self, id, imagen_url="http://example.com/img.jpg"):
        self.id = id
        self.imagen_url = imagen_url

def test_partial_order():
    """Prueba el orden de parámetros con partial"""
    print("=" * 60)
    print("TEST: Orden de parámetros con functools.partial")
    print("=" * 60)
    
    # Simulación del método con parámetros (e, voucher)
    def handler_correcto(e, voucher):
        print(f"✓ Handler llamado correctamente")
        print(f"  - Evento recibido: {type(e).__name__}")
        print(f"  - Voucher ID: {voucher.id}")
        return True
    
    # Simulación del método con parámetros incorrectos (voucher, e)
    def handler_incorrecto(voucher, e):
        print(f"✗ Handler con parámetros invertidos")
        print(f"  - Voucher ID: {voucher.id}")
        print(f"  - Evento recibido: {type(e).__name__}")
        return True
    
    voucher = MockVoucher(123)
    event = MockEvent()
    
    print("\n1. Usando partial(handler_correcto, voucher) - evento pasa como segundo parámetro")
    try:
        fn = partial(handler_correcto, voucher)
        # Cuando Flet llama al handler, pasa el evento
        fn(event)  # partial ya tiene voucher, recibe event
        print("  → FUNCIONA: el evento se pasa correctamente al segundo parámetro\n")
    except Exception as e:
        print(f"  → ERROR: {e}\n")
    
    print("2. Probando con handler_incorrecto(voucher, e)")
    try:
        fn = partial(handler_incorrecto, voucher)
        fn(event)
        print("  → FUNCIONA pero el orden semántico está mal\n")
    except Exception as e:
        print(f"  → ERROR: {e}\n")
    
    print("3. La firma correcta debe ser: def handler(e, voucher)")
    print("   Y usar: partial(handler, voucher)")
    print("   Flet llama: handler(event) → se convierte en handler(voucher, event)")
    print("   PERO queremos: handler(event, voucher)")
    print("\n   SOLUCIÓN: Necesitamos wrapper function o lambda invertido\n")

def test_wrapper_solution():
    """Prueba la solución con wrapper function"""
    print("=" * 60)
    print("TEST: Solución con wrapper function")
    print("=" * 60)
    
    def handler(e, voucher):
        print(f"✓ Handler llamado con orden correcto")
        print(f"  - Evento: {type(e).__name__}")
        print(f"  - Voucher ID: {voucher.id}")
    
    voucher = MockVoucher(456)
    event = MockEvent()
    
    print("\nOpción A: Lambda (lo que teníamos antes)")
    lambda_fn = lambda e, v=voucher: handler(e, v)
    lambda_fn(event)
    
    print("\nOpción B: Nested function")
    def make_handler(voucher):
        def wrapper(e):
            handler(e, voucher)
        return wrapper
    
    nested_fn = make_handler(voucher)
    nested_fn(event)
    
    print("\nOpción C: Partial invertido (NO FUNCIONA directamente)")
    print("  partial(handler, voucher) → handler(voucher, event)")
    print("  Necesitamos partial que pase event PRIMERO\n")

if __name__ == "__main__":
    test_partial_order()
    print()
    test_wrapper_solution()
    
    print("\n" + "=" * 60)
    print("CONCLUSIÓN:")
    print("=" * 60)
    print("Para Flet, debemos usar:")
    print("  1. Lambda: lambda e, v=voucher: self._HANDLER(e, v)")
    print("  2. O crear método: def _HANDLER_CLICK(self, e):")
    print("                       voucher = e.control.data")
    print("                       self._HANDLER(e, voucher)")
    print("\nEl partial() NO funciona directamente porque Flet pasa")
    print("el evento como PRIMER argumento siempre.")
    print("=" * 60)
