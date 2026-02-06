#!/usr/bin/env python
import flet as ft

tp = ft.TimePicker()
methods = [m for m in dir(tp) if not m.startswith('_') and callable(getattr(tp, m))]
print("Métodos disponibles:")
for m in methods[:30]:
    print(f"  - {m}")
