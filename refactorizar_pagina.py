#!/usr/bin/env python3
"""
Script para refactorizar páginas admin automáticamente
Uso: python refactorizar_pagina.py <archivo_pagina>
"""

import sys
import os
import re
from pathlib import Path


TEMPLATE_PAGINA = '''"""
{titulo} - REFACTORIZADA con BLoC + Componentes Globales
"""
import flet as ft
from core.base_datos.ConfiguracionBD import {modelo}
from core.Constantes import COLORES, TAMANOS, ICONOS{roles_import}
{decorador_import}from features.admin.presentation.bloc.{bloc}Bloc import (
    {bloc_upper}_BLOC,
    Cargar{plural},
    Guardar{entidad},
    Eliminar{entidad},
    {plural}Cargados,
    {entidad}Error,
    {entidad}Guardado
)
from features.admin.presentation.widgets.ComponentesGlobales import (
    Notificador,
    FormularioCRUD,
    BotonesNavegacion
)

{decorador}
class {clase}({base_clase}):
    """Gestión de {entidad_lower}s con BLoC Pattern"""
    
    def __init__(self, {init_params}):
        super().__init__({super_params})
        self._PAGINA = PAGINA
        self._USUARIO = USUARIO
        self._LISTA = ft.Column(spacing=10)
        
        # Registrar listener BLoC
        {bloc_upper}_BLOC.AGREGAR_LISTENER(self._ON_ESTADO_CAMBIO)
        
        self._CONSTRUIR()
        
        # Cargar datos vía BLoC
        {bloc_upper}_BLOC.AGREGAR_EVENTO(Cargar{plural}())
    
    def _ON_ESTADO_CAMBIO(self, estado):
        """Maneja cambios de estado del BLoC"""
        if isinstance(estado, {plural}Cargados):
            self._ACTUALIZAR_LISTA(estado.{entidad_lower}s)
        elif isinstance(estado, {entidad}Error):
            Notificador.ERROR(self, estado.mensaje)
        elif isinstance(estado, {entidad}Guardado):
            self._CERRAR_DIALOGO()
            Notificador.EXITO(self, estado.mensaje)
    
    def _CONSTRUIR(self):
        """Construye UI con componentes globales"""
        header = ft.Row(
            controls=[
                ft.Icon(ft.Icons.{icono}, size=TAMANOS.ICONO_LG, color=COLORES.PRIMARIO),
                ft.Text("{titulo}", size=TAMANOS.TEXTO_3XL, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                BotonesNavegacion.BOTON_MENU(self._IR_MENU),
                BotonesNavegacion.BOTON_SALIR(self._SALIR),
                BotonesNavegacion.BOTON_NUEVO(self._NUEVO, "{entidad}"),
            ],
            spacing=TAMANOS.ESPACIADO_MD,
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[header, self._LISTA],
                    spacing=TAMANOS.ESPACIADO_LG,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=TAMANOS.PADDING_XL,
                expand=True,
                bgcolor=COLORES.FONDO
            )
        ]
        self.expand = True
    
    def _ACTUALIZAR_LISTA(self, items):
        """Actualiza UI con datos del BLoC"""
        self._LISTA.controls.clear()
        
        for item in items:
            self._LISTA.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(str(item.{campo_principal}), weight=ft.FontWeight.W_500),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Editar",
                                icon_color=COLORES.INFO,
                                on_click=lambda e, i=item: self._EDITAR(i)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Eliminar",
                                icon_color=COLORES.PELIGRO,
                                on_click=lambda e, i=item: self._ELIMINAR(i)
                            ),
                        ],
                    ),
                    padding=TAMANOS.PADDING_MD,
                    bgcolor=COLORES.FONDO_BLANCO,
                    border_radius=TAMANOS.RADIO_SM,
                    border=ft.border.all(1, COLORES.BORDE),
                )
            )
        
        if getattr(self, "_PAGINA", None):
            self._PAGINA.update()
    
    def _NUEVO(self, e):
        self._ABRIR_FORM()
    
    def _EDITAR(self, item):
        self._ABRIR_FORM(item)
    
    def _ELIMINAR(self, item):
        """Elimina vía BLoC"""
        {bloc_upper}_BLOC.AGREGAR_EVENTO(Eliminar{entidad}({entidad_lower}_id=item.ID))
    
    def _ABRIR_FORM(self, item=None):
        """Formulario con componentes globales"""
        # TODO: Personalizar campos según el modelo
        campo_nombre = FormularioCRUD.CREAR_CAMPO(
            "Nombre",
            item.NOMBRE if item else "",
            icono=ft.Icons.{icono}
        )
        
        def guardar(e):
            if not campo_nombre.value:
                Notificador.ADVERTENCIA(self, "Completa los campos obligatorios")
                return
            
            datos = {{"NOMBRE": campo_nombre.value.strip()}}
            if item:
                datos["ID"] = item.ID
            
            {bloc_upper}_BLOC.AGREGAR_EVENTO(Guardar{entidad}(datos=datos))
        
        dialogo = FormularioCRUD.CONSTRUIR_DIALOGO(
            titulo="✏️ Editar {entidad}" if item else "➕ Nuevo {entidad}",
            campos=[campo_nombre],
            on_guardar=guardar,
            on_cancelar=lambda e: self._CERRAR_DIALOGO(),
            es_edicion=item is not None
        )
        
        self._PAGINA.dialog = dialogo
        dialogo.open = True
        self._PAGINA.update()
    
    def _CERRAR_DIALOGO(self):
        if self._PAGINA.dialog:
            self._PAGINA.dialog.open = False
            self._PAGINA.update()
    
    def _IR_MENU(self, e):
        from features.admin.presentation.pages.PaginaAdmin import PaginaAdmin
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaAdmin(self._PAGINA, self._USUARIO))
        self._PAGINA.update()
    
    def _SALIR(self, e):
        from features.autenticacion.presentation.pages.PaginaLogin import PaginaLogin
        self._PAGINA.controls.clear()
        self._PAGINA.controls.append(PaginaLogin(self._PAGINA))
        self._PAGINA.update()
    
    def __del__(self):
        """Limpieza"""
        try:
            {bloc_upper}_BLOC.REMOVER_LISTENER(self._ON_ESTADO_CAMBIO)
        except:
            pass
'''


# Mapeo de páginas a configuraciones
CONFIGURACIONES = {
    "PaginaExtras.py": {
        "modelo": "MODELO_EXTRA",
        "bloc": "Extras",
        "entidad": "Extra",
        "plural": "Extrases",
        "campo_principal": "NOMBRE",
        "icono": "ADD_CIRCLE",
        "titulo": "Gestión de Extras",
        "roles": ", ROLES",
        "decorador": "@REQUIERE_ROL(ROLES.SUPERADMIN, ROLES.ADMIN)",
        "base_clase": "ft.Column",
        "init_params": "PAGINA: ft.Page, USUARIO",
        "super_params": ""
    },
    "PaginaProveedores.py": {
        "modelo": "MODELO_PROVEEDOR",
        "bloc": "Proveedores",
        "entidad": "Proveedor",
        "plural": "Proveedoreses",
        "campo_principal": "NOMBRE",
        "icono": "BUSINESS",
        "titulo": "Gestión de Proveedores",
        "roles": ", ROLES",
        "decorador": "@REQUIERE_ROL(ROLES.SUPERADMIN)",
        "base_clase": "ft.Column",
        "init_params": "PAGINA: ft.Page, USUARIO",
        "super_params": ""
    },
}


def generar_codigo(config):
    """Genera código refactorizado"""
    return TEMPLATE_PAGINA.format(
        titulo=config["titulo"],
        modelo=config["modelo"],
        roles_import=config["roles"],
        decorador_import="from core.decoradores.DecoradorVistas import REQUIERE_ROL\n" if config["decorador"] else "",
        bloc=config["bloc"],
        bloc_upper=config["bloc"].upper(),
        plural=config["plural"],
        entidad=config["entidad"],
        entidad_lower=config["entidad"].lower(),
        decorador=config["decorador"] + "\n" if config["decorador"] else "",
        clase=Path(sys.argv[1]).stem,
        base_clase=config["base_clase"],
        init_params=config["init_params"],
        super_params=config["super_params"],
        icono=config["icono"],
        campo_principal=config["campo_principal"]
    )


def main():
    if len(sys.argv) < 2:
        print("❌ Uso: python refactorizar_pagina.py <archivo.py>")
        sys.exit(1)
    
    archivo = sys.argv[1]
    nombre = os.path.basename(archivo)
    
    if nombre not in CONFIGURACIONES:
        print(f"❌ No hay configuración para {nombre}")
        print(f"Archivos disponibles: {list(CONFIGURACIONES.keys())}")
        sys.exit(1)
    
    config = CONFIGURACIONES[nombre]
    codigo = generar_codigo(config)
    
    ruta_destino = Path(__file__).parent / "features" / "admin" / "presentation" / "pages" / nombre
    
    # Backup
    if ruta_destino.exists():
        backup = ruta_destino.with_suffix('.py.backup')
        with open(ruta_destino, 'r') as f:
            with open(backup, 'w') as fb:
                fb.write(f.read())
        print(f"✅ Backup creado: {backup}")
    
    # Escribir refactorización
    with open(ruta_destino, 'w', encoding='utf-8') as f:
        f.write(codigo)
    
    print(f"✅ Refactorizado: {ruta_destino}")
    print(f"\n📝 Revisar TODOs en el archivo para completar campos específicos")


if __name__ == "__main__":
    main()
