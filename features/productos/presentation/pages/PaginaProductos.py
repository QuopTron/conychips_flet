import flet as ft
import asyncio
import os
import shutil
import time
import subprocess
from typing import Optional
from features.productos.data.RepositorioProductosImpl import RepositorioProductosImpl
from features.pedidos.data.RepositorioPedidosImpl import RepositorioPedidosImpl
from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION,
    MODELO_SUCURSAL,
    MODELO_EXTRA,
    MODELO_PRODUCTO,
)

class PaginaProductos(ft.Column):
    def __init__(self, PAGINA: ft.Page, USUARIO_ID: int):
        super().__init__()
        self._PAGINA = PAGINA
        self._USUARIO_ID = USUARIO_ID
        self._REPO_PROD = RepositorioProductosImpl()
        self._REPO_PED = RepositorioPedidosImpl()
        self._LISTA_CONTROLES = ft.Column()
        self._CARRITO = []
        self._SUCURSAL_SELECCIONADA = None
        self._CONSTRUIR()

    def _CONSTRUIR(self):
        HEADER = ft.Text("Productos disponibles", size=24, weight=ft.FontWeight.BOLD)
        self._DROPDOWN_SUCURSAL = ft.Dropdown(
            label="Sucursal", on_select=self._CAMBIAR_SUCURSAL, width=260
        )

        self._BUSCADOR = ft.TextField(
            label="Buscar productos...",
            width=300,
            on_change=lambda e: self._REFRESCAR(),
        )

        tipos = [
            ft.dropdown.Option(key="todos", text="Todos"),
            ft.dropdown.Option(key="gaseosa", text="Gaseosa"),
            ft.dropdown.Option(key="comida", text="Comida"),
            ft.dropdown.Option(key="producto", text="Producto"),
        ]
        self._DROPDOWN_TIPO = ft.Dropdown(
            label="Tipo",
            options=tipos,
            value="todos",
            on_select=self._CAMBIAR_TIPO,
            width=180,
        )

        self._TEXTO_CARRITO = ft.Text("Carrito vacío", size=16)
        self._BOTON_VER_CARRITO = ft.Button(
            "Ver Carrito", on_click=self._VER_CARRITO, disabled=True
        )

        self._LISTA_CONTROLES = ft.GridView(expand=True, max_extent=360, spacing=12)

        CONTROLES_SUPERIORES = ft.Row(
            [
                self._DROPDOWN_SUCURSAL,
                ft.Container(width=12),
                self._DROPDOWN_TIPO,
                ft.Container(width=12),
                self._BUSCADOR,
                ft.Container(expand=True),
                ft.Row([self._TEXTO_CARRITO, self._BOTON_VER_CARRITO]),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        HEADER,
                        ft.Container(
                            content=CONTROLES_SUPERIORES,
                            padding=ft.Padding.only(top=10, bottom=10),
                        ),
                        self._LISTA_CONTROLES,
                    ]
                ),
                padding=20,
                expand=True,
            )
        ]
        self.expand = True
        self._CARGAR_SUCURSALES()
        asyncio.create_task(self._INICIALIZAR_WEBSOCKET())

    async def _INICIALIZAR_WEBSOCKET(self):
        from core.websocket.ManejadorConexion import ManejadorConexion

        manejador = ManejadorConexion()
        while True:
            cliente = manejador.OBTENER_CONEXION(self._USUARIO_ID)
            if cliente:

                async def _on_msg(mensaje):
                    try:
                        tipo = mensaje.get("tipo")
                        if tipo in (
                            "pedido_confirmado",
                            "pedido_pagado",
                            "nuevo_pedido",
                        ):
                            if (
                                mensaje.get("sucursal_id")
                                == self._SUCURSAL_SELECCIONADA
                            ):
                                self._REFRESCAR()
                    except Exception:
                        pass

                cliente.REGISTRAR_CALLBACK_MENSAJE(_on_msg)
                break
            await asyncio.sleep(1)

    def _CARGAR_SUCURSALES(self):
        sesion = OBTENER_SESION()
        sucursales = sesion.query(MODELO_SUCURSAL).filter_by(ACTIVA=True).all()
        opciones = [
            ft.dropdown.Option(key=str(s.ID), text=s.NOMBRE) for s in sucursales
        ]
        self._DROPDOWN_SUCURSAL.options = opciones
        if opciones:
            self._DROPDOWN_SUCURSAL.value = opciones[0].key
            self._SUCURSAL_SELECCIONADA = int(opciones[0].key)
        self._REFRESCAR()

    def _CAMBIAR_SUCURSAL(self, e):
        self._SUCURSAL_SELECCIONADA = int(e.control.value) if e.control.value else None
        self._REFRESCAR()

    def _CAMBIAR_TIPO(self, e):
        self._TIPO_SELECCIONADO = e.control.value if e.control.value else "todos"
        self._REFRESCAR()

    def _REFRESCAR(self):
        import asyncio

        asyncio.create_task(self._CARGAR_PRODUCTOS())

    async def _CARGAR_PRODUCTOS(self):
        if not self._SUCURSAL_SELECCIONADA:
            return
        productos = await self._REPO_PROD.OBTENER_POR_SUCURSAL(
            self._SUCURSAL_SELECCIONADA
        )
        tipo_sel = getattr(self, "_TIPO_SELECCIONADO", "todos")
        if tipo_sel and tipo_sel != "todos":
            productos = [
                p for p in productos if (p.get("TIPO") or "gaseosa") == tipo_sel
            ]

        self._LISTA_CONTROLES.controls.clear()
        for p in productos:
            imagen = ft.Image(
                src=p.get("IMAGEN", "assets/placeholder.jpg"),
                width=140,
                height=100,
                fit="contain",
            )
            precio_text = ft.Text(
                f"{p['PRECIO']} Bs", size=18, weight=ft.FontWeight.BOLD
            )
            recomendado_badge = None
            if (p.get("TIPO") or "gaseosa") == "gaseosa":
                recomendado_badge = ft.Text(
                    "Recomendado", color=ft.Colors.GREEN_600, size=12
                )

            nombre_desc_children = [
                ft.Text(p["NOMBRE"], weight=ft.FontWeight.BOLD, size=18),
                ft.Text(p.get("DESCRIPCION", ""), size=15, color=ft.Colors.GREY_600),
            ]
            if recomendado_badge:
                nombre_desc_children.append(recomendado_badge)

            nombre_desc = ft.Column(nombre_desc_children, spacing=6)

            tipo_val = (p.get("TIPO") or "gaseosa").capitalize()
            tipo_chip = ft.Container(
                content=ft.Text(tipo_val, size=12, color=ft.Colors.WHITE),
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                bgcolor=ft.Colors.BLUE_600,
                border_radius=8,
            )

            imagen_container = ft.Container(
                content=imagen, height=140, bgcolor=ft.Colors.GREY_100, border_radius=8
            )

            precio_badge = ft.Container(
                content=precio_text,
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                bgcolor=ft.Colors.YELLOW_100,
                border_radius=8,
            )

            btn_anadir = ft.Button(
                "",
                icon=ft.icons.Icons.ADD_SHOPPING_CART_ROUNDED,
                on_click=lambda e, prod=p: self._ANADIR_CARRITO(prod),
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE,
                width=44,
                height=36,
            )
            btn_detalles = ft.Button(
                "",
                icon=ft.icons.Icons.INFO_OUTLINE,
                on_click=lambda e, prod=p: self._VER_DETALLES(prod),
                width=44,
                height=36,
            )

            tarjeta = ft.Container(
                content=ft.Column(
                    [
                        ft.Row([tipo_chip], alignment=ft.MainAxisAlignment.START),
                        imagen_container,
                        ft.Container(
                            content=nombre_desc,
                            padding=ft.Padding.only(top=8, bottom=6),
                        ),
                        ft.Row(
                            [
                                precio_badge,
                                ft.Container(expand=True),
                                btn_anadir,
                                ft.Container(width=8),
                                btn_detalles,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=6,
                ),
                padding=12,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                border=ft.Border.all(1, ft.Colors.GREY_200),
                width=300,
                height=320,
                shadow=ft.BoxShadow(
                    blur_radius=10, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)
                ),
                on_click=lambda e, prod=p: self._VER_DETALLES(prod),
            )
            self._LISTA_CONTROLES.controls.append(tarjeta)
        try:
            self._PAGINA.update()
        except Exception:
            try:
                self.update()
            except Exception:
                pass

    def _ANADIR_CARRITO(self, PRODUCTO):
        self._CARRITO.append({"producto": PRODUCTO, "cantidad": 1, "extras": []})
        self._ACTUALIZAR_CARRITO_UI()

    def _ACTUALIZAR_CARRITO_UI(self):
        total_items = sum(item["cantidad"] for item in self._CARRITO)
        self._TEXTO_CARRITO.value = f"Carrito: {total_items} items"
        self._BOTON_VER_CARRITO.disabled = total_items == 0
        try:
            self._PAGINA.update()
        except Exception:
            try:
                self.update()
            except Exception:
                pass

    def _VER_CARRITO(self, e):
        if not self._CARRITO:
            return
        contenido = ft.Column(spacing=12)
        total = 0
        for item in self._CARRITO:
            prod = item["producto"]
            cant = item["cantidad"]
            precio = prod["PRECIO"] * cant
            total += precio

            thumb = ft.Image(
                src=prod.get("IMAGEN", "assets/placeholder.jpg"),
                width=64,
                height=48,
                fit="contain",
            )
            lbl = ft.Column(
                [
                    ft.Text(prod["NOMBRE"], weight=ft.FontWeight.BOLD),
                    ft.Text(
                        f"{prod.get('DESCRIPCION','')}",
                        size=12,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                spacing=4,
            )

            btn_menos = ft.IconButton(
                icon=ft.icons.Icons.REMOVE,
                on_click=lambda e, pid=prod["ID"]: self._CAMBIAR_CANTIDAD(pid, -1),
            )
            txt_cant = ft.Container(
                content=ft.Text(str(cant)), width=40, alignment=ft.alignment(1, 1)
            )
            btn_mas = ft.IconButton(
                icon=ft.icons.Icons.ADD,
                on_click=lambda e, pid=prod["ID"]: self._CAMBIAR_CANTIDAD(pid, 1),
            )

            btn_quitar = ft.IconButton(
                icon=ft.icons.Icons.DELETE_OUTLINE,
                tooltip="Quitar",
                on_click=lambda e, pid=prod["ID"]: self._REMOVER_ITEM(pid),
            )

            fila = ft.Row(
                [
                    thumb,
                    ft.Container(
                        content=lbl, padding=ft.Padding.only(left=8), expand=True
                    ),
                    ft.Row([btn_menos, txt_cant, btn_mas]),
                    ft.Text(f"{precio} Bs", weight=ft.FontWeight.BOLD),
                    btn_quitar,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )

            contenido.controls.append(fila)

        contenido.controls.append(
            ft.Text(f"Total: {total} Bs", weight=ft.FontWeight.BOLD)
        )

        try:
            dlg = ft.AlertDialog(
                title=ft.Text("Carrito"),
                content=contenido,
                actions=[
                    ft.TextButton("Vaciar", on_click=self._VACIAR_CARRITO),
                    ft.Button(
                        "Pedir Todo",
                        on_click=lambda e: asyncio.create_task(self._PEDIR_TODO()),
                    ),
                ],
            )
            self._PAGINA.dialog = dlg
            dlg.open = True
            self._PAGINA.update()
        except Exception as ex:
            print("Error mostrando diálogo carrito:", ex)
            self._PAGINA.snack_bar = ft.SnackBar(ft.Text("Error mostrando carrito"))
            self._PAGINA.snack_bar.open = True
            try:
                self._PAGINA.update()
            except Exception:
                pass

    def _VACIAR_CARRITO(self, e):
        self._CARRITO.clear()
        self._ACTUALIZAR_CARRITO_UI()
        if hasattr(self._PAGINA, "dialog") and self._PAGINA.dialog:
            self._PAGINA.dialog.open = False
        if getattr(self, "page", None):
            self.update()

    def _CAMBIAR_CANTIDAD(self, PRODUCTO_ID, DELTA: int):
        for item in self._CARRITO:
            if item["producto"]["ID"] == PRODUCTO_ID:
                item["cantidad"] = max(1, item["cantidad"] + DELTA)
                break
        self._ACTUALIZAR_CARRITO_UI()
        if (
            hasattr(self._PAGINA, "dialog")
            and self._PAGINA.dialog
            and self._PAGINA.dialog.open
        ):
            self._PAGINA.dialog.open = False
            self._VER_CARRITO(None)

    def _REMOVER_ITEM(self, PRODUCTO_ID):
        self._CARRITO = [
            it for it in self._CARRITO if it["producto"]["ID"] != PRODUCTO_ID
        ]
        self._ACTUALIZAR_CARRITO_UI()
        if (
            hasattr(self._PAGINA, "dialog")
            and self._PAGINA.dialog
            and self._PAGINA.dialog.open
        ):
            self._PAGINA.dialog.open = False
            if self._CARRITO:
                self._VER_CARRITO(None)

    async def _PEDIR_TODO(self):
        created_ids = []
        for item in self._CARRITO:
            prod = item["producto"]
            cant = item["cantidad"]
            try:
                extras = item.get("extras") if item.get("extras") else None
                res = await self._REPO_PED.CREAR_PEDIDO(
                    self._USUARIO_ID,
                    prod["ID"],
                    cant,
                    self._SUCURSAL_SELECCIONADA,
                    EXTRAS=extras,
                )
                if res.get("EXITO"):
                    created_ids.append(res.get("PEDIDO_ID"))
            except Exception as ex:
                print(f"Error creando pedido para {prod['NOMBRE']}: {ex}")

        self._CARRITO.clear()
        self._ACTUALIZAR_CARRITO_UI()
        if hasattr(self._PAGINA, "dialog") and self._PAGINA.dialog:
            self._PAGINA.dialog.open = False

        if created_ids:
            contenido = ft.Column()
            for pid in created_ids:
                contenido.controls.append(ft.Text(f"Pedido creado: #{pid}"))

            dlg = ft.AlertDialog(
                title=ft.Text("Pedidos creados"),
                content=contenido,
                actions=[
                    ft.TextButton(
                        "Cerrar", on_click=lambda e: self._CERRAR_DIALOG(dlg)
                    ),
                    ft.Button(
                        "Simular pago con QR",
                        on_click=lambda e: asyncio.create_task(
                            self._SIMULAR_PAGO(created_ids)
                        ),
                    ),
                ],
            )
            self._PAGINA.dialog = dlg
            dlg.open = True
            self._PAGINA.update()
        else:
            self._PAGINA.snack_bar = ft.SnackBar(
                ft.Text("No se pudieron crear pedidos")
            )
            self._PAGINA.snack_bar.open = True

    def _VER_DETALLES(self, PRODUCTO):
        sesion = OBTENER_SESION()
        extras = sesion.query(MODELO_EXTRA).filter_by(ACTIVO=True).all()
        checkboxes = []
        for ext in extras:
            cb = ft.Checkbox(
                label=f"{ext.NOMBRE} (+{ext.PRECIO_ADICIONAL} Bs)", value=False
            )
            checkboxes.append(cb)
        btn_subir = ft.Button(
            "Subir imagen",
            on_click=lambda e, prod=PRODUCTO: asyncio.create_task(
                self._SUBIR_IMAGEN(prod)
            ),
        )

        try:
            dlg = ft.AlertDialog(
                title=ft.Text(PRODUCTO["NOMBRE"]),
                content=ft.Column(
                    [
                        ft.Text(PRODUCTO.get("DESCRIPCION", "")),
                        ft.Text(f"Precio: {PRODUCTO['PRECIO']} Bs"),
                        ft.Text("Extras opcionales:"),
                        ft.Column(checkboxes),
                    ]
                ),
                actions=[
                    ft.TextButton(
                        "Cerrar", on_click=lambda e: self._CERRAR_DIALOG(dlg)
                    ),
                    ft.Button(
                        "Añadir con Extras",
                        on_click=lambda e: self._ANADIR_CON_EXTRAS(
                            PRODUCTO, checkboxes, dlg
                        ),
                    ),
                    btn_subir,
                ],
            )
            self._PAGINA.dialog = dlg
            dlg.open = True
            self._PAGINA.update()
        except Exception as ex:
            print("Error mostrando detalles producto:", ex)
            self._PAGINA.snack_bar = ft.SnackBar(ft.Text("Error mostrando detalles"))
            self._PAGINA.snack_bar.open = True
            try:
                self._PAGINA.update()
            except Exception:
                pass

    def _ANADIR_CON_EXTRAS(self, PRODUCTO, CHECKBOXES, DLG):
        extras_seleccionados = [cb.label.split(" ")[0] for cb in CHECKBOXES if cb.value]
        self._CARRITO.append(
            {"producto": PRODUCTO, "cantidad": 1, "extras": extras_seleccionados}
        )
        self._ACTUALIZAR_CARRITO_UI()
        DLG.open = False
        try:
            self._PAGINA.update()
        except Exception:
            try:
                self.update()
            except Exception:
                pass

    def _CERRAR_DIALOG(self, DLG):
        DLG.open = False
        try:
            self._PAGINA.update()
        except Exception:
            try:
                self.update()
            except Exception:
                pass

    def _SELECCIONAR_IMAGEN(self):
        path = None
        try:
            from tkinter import Tk, filedialog

            root = Tk()
            root.withdraw()
            path = filedialog.askopenfilename(
                filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif")]
            )
            root.destroy()
        except Exception:
            path = None

        if not path:
            try:
                res = subprocess.run(
                    [
                        "zenity",
                        "--file-selection",
                        "--file-filter=*.png --file-filter=*.jpg --file-filter=*.jpeg --file-filter=*.gif",
                    ],
                    capture_output=True,
                    text=True,
                )
                if res.returncode == 0:
                    path = res.stdout.strip()
            except Exception:
                path = None

        if not path:
            return None

        try:
            dest_dir = os.path.join(os.getcwd(), "assets", "uploads")
            os.makedirs(dest_dir, exist_ok=True)
            filename = os.path.basename(path)
            dest = os.path.join(dest_dir, f"{int(time.time())}_{filename}")
            shutil.copyfile(path, dest)
            rel = os.path.relpath(dest, os.getcwd())
            return rel.replace("\\", "/")
        except Exception as ex:
            print("Error copiando imagen:", ex)
            return None

    async def _SUBIR_IMAGEN(self, PRODUCTO):
        loop = asyncio.get_running_loop()
        rel = await loop.run_in_executor(None, self._SELECCIONAR_IMAGEN)
        if rel:
            try:
                sesion = OBTENER_SESION()
                p = sesion.query(MODELO_PRODUCTO).filter_by(ID=PRODUCTO["ID"]).first()
                if p:
                    p.IMAGEN = rel
                    sesion.commit()
                self._PAGINA.snack_bar = ft.SnackBar(ft.Text("Imagen subida"))
                self._PAGINA.snack_bar.open = True
                self._REFRESCAR()
            except Exception as ex:
                print("Error guardando imagen en DB:", ex)
                self._PAGINA.snack_bar = ft.SnackBar(ft.Text("Error guardando imagen"))
                self._PAGINA.snack_bar.open = True
        else:
            self._PAGINA.snack_bar = ft.SnackBar(ft.Text("No se seleccionó imagen"))
            self._PAGINA.snack_bar.open = True
        try:
            self._PAGINA.update()
        except Exception:
            try:
                self.update()
            except Exception:
                pass

    async def _SIMULAR_PAGO(self, PEDIDO_IDS: list):
        resultados = []
        for pid in PEDIDO_IDS:
            try:
                await self._REPO_PED.CONFIRMAR_PAGO_QR(pid, 0, "SIMULATED_QR")
                resultados.append((pid, True))
            except Exception as ex:
                resultados.append((pid, False))

        exitos = [p for p, ok in resultados if ok]
        fallidos = [p for p, ok in resultados if not ok]

        mensaje = f"Pagos confirmados: {len(exitos)}"
        if fallidos:
            mensaje += f" - Fallidos: {', '.join(str(x) for x in fallidos)}"

        self._PAGINA.snack_bar = ft.SnackBar(ft.Text(mensaje))
        self._PAGINA.snack_bar.open = True
        if getattr(self._PAGINA, "page", None):
            self._PAGINA.update()
