import flet as ft
print([i for i in dir(ft.Icons) if not i.startswith("_")])
