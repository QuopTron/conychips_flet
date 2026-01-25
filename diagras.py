#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENERADOR COMPLETO DE DIAGRAMAS UML - SISTEMA CONY CHIPS
Puntos 4.6 a 4.9 - Diagramas UML Completos
"""

import os
import graphviz
from graphviz import Digraph

def default_graph_attrs(rankdir='TB', splines='ortho'):
    """Estilos globales para los diagramas para mejorar la legibilidad."""
    return {
        'rankdir': rankdir,
        'splines': splines,
        'nodesep': '1.0',  # Aumentado para más espacio horizontal
        'ranksep': '1.5',  # Aumentado para más espacio vertical
        'fontname': 'Arial',
        'fontsize': '16', # Tamaño de letra más grande para etiquetas
        'node': {
            'fontname': 'Arial',
            'fontsize': '14', # Letra en nodos
            'shape': 'record' # Usar 'record' para formas rectangulares
        },
        'edge': {
            'fontname': 'Arial',
            'fontsize': '12'  # Letra en flechas
        }
    }

# Configurar directorios de salida
def crear_directorios():
    """Crea la estructura de directorios para los diagramas"""
    directorios = [
        'diagramas/4.6_objetos',
        'diagramas/4.7_casos_uso',
        'diagramas/4.8_clases',
        'diagramas/4.9_componentes_despliegue'
    ]
    for dir_path in directorios:
        os.makedirs(dir_path, exist_ok=True)

# ============================================================================
# PUNTO 4.6 - DIAGRAMAS DE OBJETOS (con actores stickman)
# ============================================================================

def crear_actor_stickman(dot, node_id, label):
    """Crea un nodo con forma de stickman para actores"""
    dot.node(node_id, f'''<
    <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">
     <TR><TD ALIGN="CENTER">
      <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">
       <TR><TD ALIGN="CENTER"></TD></TR>
       <TR><TD ALIGN="CENTER">|</TD></TR>
       <TR><TD ALIGN="CENTER">/&nbsp;\\</TD></TR>
      </TABLE>
     </TD></TR>
     <TR><TD ALIGN="CENTER"><B>{label}</B></TD></TR>
    </TABLE>>''', shape='plaintext')

def generar_4_6_diagramas_objetos():
    """Genera todos los diagramas de objetos del punto 4.6"""
    print("=== Generando Diagramas de Objetos (4.6) ===")
   
    # Diagrama 4.6.1 - Registro de Clientes
    dot = Digraph('registro_clientes', format='png')
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.8')
   
    # Actor Cliente
    crear_actor_stickman(dot, 'actor_cliente', 'Cliente')
   
    # Objeto Cliente
    dot.node('obj_cliente', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightcoral"><B>:Cliente</B></TD></TR>
     <TR><TD ALIGN="LEFT">nombre</TD><TD>"Carlos Vargas"</TD></TR>
     <TR><TD ALIGN="LEFT">whatsapp</TD><TD>"591-74567890"</TD></TR>
     <TR><TD ALIGN="LEFT">direccion</TD><TD>"Av. Beni #123"</TD></TR>
     <TR><TD ALIGN="LEFT">historial</TD><TD>"Cliente frecuente"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    # Objeto Formulario
    dot.node('obj_formulario', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>:FormularioRegistro</B></TD></TR>
     <TR><TD ALIGN="LEFT">tipo</TD><TD>"Registro Cliente"</TD></TR>
     <TR><TD ALIGN="LEFT">campos</TD><TD>[nombre, telefono, direccion]</TD></TR>
     <TR><TD ALIGN="LEFT">estado</TD><TD>"Completado"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    # Objeto Sistema
    dot.node('obj_sistema', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightgreen"><B>:SistemaConyChips</B></TD></TR>
     <TR><TD ALIGN="LEFT">modulo</TD><TD>"Registro Clientes"</TD></TR>
     <TR><TD ALIGN="LEFT">version</TD><TD>"2.0"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    # Relaciones
    dot.edge('actor_cliente', 'obj_cliente', label='<<representa>>', style='dashed')
    dot.edge('obj_cliente', 'obj_formulario', label='<<completa>>')
    dot.edge('obj_formulario', 'obj_sistema', label='<<envía a>>')
   
    dot.render('diagramas/4.6_objetos/01_registro_clientes', view=False, cleanup=True)
   
    # Diagrama 4.6.2 - Registro de Personal
    dot = Digraph('registro_personal', format='png')
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.8')
   
    crear_actor_stickman(dot, 'actor_admin', 'Administrador')
   
    dot.node('obj_personal', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightcoral"><B>:Personal</B></TD></TR>
     <TR><TD ALIGN="LEFT">nombre</TD><TD>"María López"</TD></TR>
     <TR><TD ALIGN="LEFT">cargo</TD><TD>"Atención al Cliente"</TD></TR>
     <TR><TD ALIGN="LEFT">telefono</TD><TD>"591-71234567"</TD></TR>
     <TR><TD ALIGN="LEFT">ci</TD><TD>"1234567 LP"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('obj_registro', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>:RegistroPersonal</B></TD></TR>
     <TR><TD ALIGN="LEFT">fecha</TD><TD>"2025-01-23"</TD></TR>
     <TR><TD ALIGN="LEFT">hora</TD><TD>"08:30"</TD></TR>
     <TR><TD ALIGN="LEFT">responsable</TD><TD>"admin"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.edge('actor_admin', 'obj_personal', label='<<registra>>')
    dot.edge('obj_personal', 'obj_registro', label='<<genera>>')
   
    dot.render('diagramas/4.6_objetos/02_registro_personal', view=False, cleanup=True)
   
    # Diagrama 4.6.3 - Solicitud de Pedido
    dot = Digraph('solicitud_pedido', format='png')
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.8')
   
    crear_actor_stickman(dot, 'actor_cliente2', 'Cliente')
   
    dot.node('obj_pedido_solicitud', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightcoral"><B>:Pedido</B></TD></TR>
     <TR><TD ALIGN="LEFT">productos</TD><TD>"Papas fritas, Hamburguesa"</TD></TR>
     <TR><TD ALIGN="LEFT">cantidad</TD><TD>2</TD></TR>
     <TR><TD ALIGN="LEFT">extras</TD><TD>"Extra queso"</TD></TR>
     <TR><TD ALIGN="LEFT">ubicacion</TD><TD>"Zona Sur"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('obj_whatsapp', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>:WhatsApp</B></TD></TR>
     <TR><TD ALIGN="LEFT">numero</TD><TD>"591-74567890"</TD></TR>
     <TR><TD ALIGN="LEFT">mensaje</TD><TD>"Pedido recibido"</TD></TR>
     <TR><TD ALIGN="LEFT">timestamp</TD><TD>"14:30:15"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('obj_ia', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightgreen"><B>:IAProcesamiento</B></TD></TR>
     <TR><TD ALIGN="LEFT">modelo</TD><TD>"GPT-4"</TD></TR>
     <TR><TD ALIGN="LEFT">accion</TD><TD>"Procesar pedido"</TD></TR>
     <TR><TD ALIGN="LEFT">confianza</TD><TD>0.95</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.edge('actor_cliente2', 'obj_pedido_solicitud', label='<<solicita>>')
    dot.edge('obj_pedido_solicitud', 'obj_whatsapp', label='<<envía por>>')
    dot.edge('obj_whatsapp', 'obj_ia', label='<<procesa>>')
   
    dot.render('diagramas/4.6_objetos/03_solicitud_pedido', view=False, cleanup=True)
   
    # Diagrama 4.6.4 - Registrar Pedido
    dot = Digraph('registrar_pedido', format='png')
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.8')
   
    crear_actor_stickman(dot, 'actor_atencion', 'Personal Atención')
   
    dot.node('obj_pedido_registro', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightcoral"><B>:Pedido</B></TD></TR>
     <TR><TD ALIGN="LEFT">numero</TD><TD>"PED-2025-001"</TD></TR>
     <TR><TD ALIGN="LEFT">cliente</TD><TD>"Carlos Vargas"</TD></TR>
     <TR><TD ALIGN="LEFT">estado</TD><TD>"Registrado"</TD></TR>
     <TR><TD ALIGN="LEFT">hora</TD><TD>"14:35"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('obj_sistema_pedidos', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>:SistemaPedidos</B></TD></TR>
     <TR><TD ALIGN="LEFT">accion</TD><TD>"Registrar pedido"</TD></TR>
     <TR><TD ALIGN="LEFT">validacion</TD><TD>"Exitosa"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('obj_bd_pedidos', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightgreen"><B>:BDPedidos</B></TD></TR>
     <TR><TD ALIGN="LEFT">id</TD><TD>1001</TD></TR>
     <TR><TD ALIGN="LEFT">fechaRegistro</TD><TD>"2025-01-23"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.edge('actor_atencion', 'obj_pedido_registro', label='<<ingresa>>')
    dot.edge('obj_pedido_registro', 'obj_sistema_pedidos', label='<<valida>>')
    dot.edge('obj_sistema_pedidos', 'obj_bd_pedidos', label='<<almacena en>>')
   
    dot.render('diagramas/4.6_objetos/04_registrar_pedido', view=False, cleanup=True)
   
    # Diagrama 4.6.5 - Ejecución del Pedido
    dot = Digraph('ejecucion_pedido', format='png')
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.8')
   
    crear_actor_stickman(dot, 'actor_cocina', 'Personal Cocina')
   
    dot.node('obj_pedido_ejecucion', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightcoral"><B>:PedidoActivo</B></TD></TR>
     <TR><TD ALIGN="LEFT">numero</TD><TD>"PED-2025-001"</TD></TR>
     <TR><TD ALIGN="LEFT">estado</TD><TD>"En preparación"</TD></TR>
     <TR><TD ALIGN="LEFT">tiempoEstimado</TD><TD>"20 min"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('obj_proceso_preparacion', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>:ProcesoPreparacion</B></TD></TR>
     <TR><TD ALIGN="LEFT">pasos</TD><TD>["Cocinar", "Armar", "Empacar"]</TD></TR>
     <TR><TD ALIGN="LEFT">inicio</TD><TD>"14:40"</TD></TR>
     <TR><TD ALIGN="LEFT">fin</TD><TD>"14:55"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('obj_pedido_listo', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightgreen"><B>:PedidoListo</B></TD></TR>
     <TR><TD ALIGN="LEFT">numero</TD><TD>"PED-2025-001"</TD></TR>
     <TR><TD ALIGN="LEFT">estado</TD><TD>"Completado"</TD></TR>
     <TR><TD ALIGN="LEFT">horaListo</TD><TD>"14:55"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.edge('actor_cocina', 'obj_pedido_ejecucion', label='<<recibe>>')
    dot.edge('obj_pedido_ejecucion', 'obj_proceso_preparacion', label='<<prepara>>')
    dot.edge('obj_proceso_preparacion', 'obj_pedido_listo', label='<<completa>>')
   
    dot.render('diagramas/4.6_objetos/05_ejecucion_pedido', view=False, cleanup=True)
   
    # Diagrama 4.6.6 - Notificación de Pago
    dot = Digraph('notificacion_pago', format='png')
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.8')
   
    dot.node('obj_sistema_notif', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightcoral"><B>:SistemaNotificaciones</B></TD></TR>
     <TR><TD ALIGN="LEFT">evento</TD><TD>"Pago pendiente"</TD></TR>
     <TR><TD ALIGN="LEFT">prioridad</TD><TD>"Alta"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('obj_datos_pago', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>:DatosPago</B></TD></TR>
     <TR><TD ALIGN="LEFT">pedido</TD><TD>"PED-2025-001"</TD></TR>
     <TR><TD ALIGN="LEFT">monto</TD><TD>85.50 Bs</TD></TR>
     <TR><TD ALIGN="LEFT">metodo</TD><TD>"Transferencia"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    crear_actor_stickman(dot, 'actor_cliente3', 'Cliente')
   
    dot.node('obj_confirmacion', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightgreen"><B>:ConfirmacionPago</B></TD></TR>
     <TR><TD ALIGN="LEFT">estado</TD><TD>"Confirmado"</TD></TR>
     <TR><TD ALIGN="LEFT">horaConfirmacion</TD><TD>"15:05"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.edge('obj_sistema_notif', 'obj_datos_pago', label='<<genera>>')
    dot.edge('obj_datos_pago', 'actor_cliente3', label='<<envía a>>')
    dot.edge('actor_cliente3', 'obj_confirmacion', label='<<confirma>>')
   
    dot.render('diagramas/4.6_objetos/06_notificacion_pago', view=False, cleanup=True)
   
    # Diagrama 4.6.7 - Registro de Pago
    dot = Digraph('registro_pago', format='png')
    dot.attr(rankdir='LR', nodesep='0.5', ranksep='0.8')
   
    crear_actor_stickman(dot, 'actor_cliente4', 'Cliente')
   
    dot.node('obj_comprobante', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightcoral"><B>:ComprobantePago</B></TD></TR>
     <TR><TD ALIGN="LEFT">numero</TD><TD>"COMP-001"</TD></TR>
     <TR><TD ALIGN="LEFT">banco</TD><TD>"Banco Union"</TD></TR>
     <TR><TD ALIGN="LEFT">monto</TD><TD>85.50 Bs</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('obj_whatsapp_pago', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>:WhatsApp</B></TD></TR>
     <TR><TD ALIGN="LEFT">archivo</TD><TD>"comprobante.jpg"</TD></TR>
     <TR><TD ALIGN="LEFT">fechaEnvio</TD><TD>"15:10"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('obj_sistema_registro', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightgreen"><B>:SistemaRegistro</B></TD></TR>
     <TR><TD ALIGN="LEFT">accion</TD><TD>"Validar pago"</TD></TR>
     <TR><TD ALIGN="LEFT">resultado</TD><TD>"Válido"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.edge('actor_cliente4', 'obj_comprobante', label='<<envía>>')
    dot.edge('obj_comprobante', 'obj_whatsapp_pago', label='<<por>>')
    dot.edge('obj_whatsapp_pago', 'obj_sistema_registro', label='<<registra en>>')
   
    dot.render('diagramas/4.6_objetos/07_registro_pago', view=False, cleanup=True)
   
    # Diagrama 4.6.8 - Notificación al Cliente
    dot = Digraph('notificacion_cliente', format='png')
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.8')
   
    dot.node('obj_pedido_notif', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightcoral"><B>:Pedido</B></TD></TR>
     <TR><TD ALIGN="LEFT">numero</TD><TD>"PED-2025-005"</TD></TR>
     <TR><TD ALIGN="LEFT">estado</TD><TD>"Listo"</TD></TR>
     <TR><TD ALIGN="LEFT">cambioEstado</TD><TD>"15:20"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('obj_notificacion', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightgreen"><B>:Notificación</B></TD></TR>
     <TR><TD ALIGN="LEFT">tipo</TD><TD>"Cambio Estado"</TD></TR>
     <TR><TD ALIGN="LEFT">mensaje</TD><TD>"Su pedido está listo"</TD></TR>
     <TR><TD ALIGN="LEFT">fechaHora</TD><TD>"2025-01-23 15:20"</TD></TR>
     <TR><TD ALIGN="LEFT">prioridad</TD><TD>"Alta"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('obj_canal', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>:CanalWhatsApp</B></TD></TR>
     <TR><TD ALIGN="LEFT">numero</TD><TD>"591-74567890"</TD></TR>
     <TR><TD ALIGN="LEFT">estado</TD><TD>"Entregado"</TD></TR>
     <TR><TD ALIGN="LEFT">leído</TD><TD>true</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    crear_actor_stickman(dot, 'actor_cliente5', 'Cliente')
   
    dot.node('obj_cliente_notif', '''
    <TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
     <TR><TD COLSPAN="2" BGCOLOR="lightcoral"><B>:Cliente</B></TD></TR>
     <TR><TD ALIGN="LEFT">nombre</TD><TD>"Carlos Vargas"</TD></TR>
     <TR><TD ALIGN="LEFT">whatsapp</TD><TD>"591-74567890"</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.edge('obj_pedido_notif', 'obj_notificacion', label='<<genera>>')
    dot.edge('obj_notificacion', 'obj_canal', label='<<usa>>')
    dot.edge('obj_canal', 'obj_cliente_notif', label='<<envía a>>')
    dot.edge('obj_cliente_notif', 'actor_cliente5', label='<<representa>>', style='dashed')
   
    dot.render('diagramas/4.6_objetos/08_notificacion_cliente', view=False, cleanup=True)
   
    print(" 4.6 - 8 Diagramas de Objetos generados")

# ============================================================================
# PUNTO 4.7 - DIAGRAMAS DE CASOS DE USO DEL SISTEMA
# ============================================================================

def generar_4_7_casos_uso():
    """Genera diagramas de casos de uso UML"""
    print("=== Generando Diagramas de Casos de Uso (4.7) ===")
   
    # Diagrama 4.7.1 - Casos de Uso General del Sistema
    dot = Digraph('casos_uso_general', format='png')
    dot.attr(rankdir='TB', nodesep='0.8', ranksep='1.0')
   
    # Actores
    dot.node('actor_admin', '‍\nAdministrador', shape='ellipse', style='filled', fillcolor='lightblue')
    dot.node('actor_atencion', '‍\nPersonal Atención', shape='ellipse', style='filled', fillcolor='lightblue')
    dot.node('actor_cocina', '‍\nPersonal Cocina', shape='ellipse', style='filled', fillcolor='lightblue')
    dot.node('actor_cliente', '\nCliente', shape='ellipse', style='filled', fillcolor='lightblue')
   
    # Sistema
    dot.node('sistema', 'Sistema Cony Chips', shape='box', style='filled', fillcolor='lightyellow')
   
    # Casos de uso
    with dot.subgraph(name='cluster_sistema') as c:
        c.attr(label='Casos de Uso', style='rounded,filled', fillcolor='lightgrey')
       
        # Gestión de Clientes
        c.node('cu_gestion_clientes', 'Gestión de\nClientes', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_registro_cliente', 'Registrar Cliente', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_actualizar_cliente', 'Actualizar Datos', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_consultar_cliente', 'Consultar Cliente', shape='ellipse', style='filled', fillcolor='white')
       
        # Gestión de Pedidos
        c.node('cu_gestion_pedidos', 'Gestión de\nPedidos', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_registrar_pedido', 'Registrar Pedido', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_seguir_pedido', 'Seguir Pedido', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_cancelar_pedido', 'Cancelar Pedido', shape='ellipse', style='filled', fillcolor='white')
       
        # Gestión de Productos
        c.node('cu_gestion_productos', 'Gestión de\nProductos', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_agregar_producto', 'Agregar Producto', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_modificar_producto', 'Modificar Producto', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_consultar_stock', 'Consultar Stock', shape='ellipse', style='filled', fillcolor='white')
       
        # Notificaciones
        c.node('cu_notificaciones', 'Gestión de\nNotificaciones', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_notificar_pago', 'Notificar Pago', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_notificar_estado', 'Notificar Estado', shape='ellipse', style='filled', fillcolor='white')
       
        # IA y WhatsApp
        c.node('cu_ia_whatsapp', 'IA WhatsApp', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_procesar_mensaje', 'Procesar Mensaje', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_generar_respuesta', 'Generar Respuesta', shape='ellipse', style='filled', fillcolor='white')
   
    # Relaciones de asociación
    dot.edge('actor_admin', 'cu_gestion_clientes')
    dot.edge('actor_admin', 'cu_gestion_productos')
    dot.edge('actor_atencion', 'cu_registrar_pedido')
    dot.edge('actor_atencion', 'cu_registro_cliente')
    dot.edge('actor_cocina', 'cu_gestion_pedidos')
    dot.edge('actor_cliente', 'cu_seguir_pedido')
    dot.edge('actor_cliente', 'cu_notificar_estado')
    dot.edge('actor_cliente', 'cu_procesar_mensaje')
   
    # Relaciones de inclusión/extensión
    dot.edge('cu_gestion_clientes', 'cu_registro_cliente', label='<<include>>', style='dashed')
    dot.edge('cu_gestion_clientes', 'cu_actualizar_cliente', label='<<include>>', style='dashed')
    dot.edge('cu_gestion_pedidos', 'cu_registrar_pedido', label='<<include>>', style='dashed')
    dot.edge('cu_gestion_productos', 'cu_agregar_producto', label='<<include>>', style='dashed')
    dot.edge('cu_notificaciones', 'cu_notificar_estado', label='<<include>>', style='dashed')
    dot.edge('cu_ia_whatsapp', 'cu_procesar_mensaje', label='<<include>>', style='dashed')
   
    dot.render('diagramas/4.7_casos_uso/01_casos_uso_general', view=False, cleanup=True)
   
    # Diagrama 4.7.2 - Casos de Uso para Administrador
    dot = Digraph('casos_uso_admin', format='png')
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.8')
   
    dot.node('admin', '‍\nAdministrador', shape='ellipse', style='filled', fillcolor='lightblue')
   
    # Casos de uso específicos
    with dot.subgraph(name='cluster_admin') as c:
        c.attr(label='Funcionalidades de Administración', style='rounded,filled', fillcolor='lightgrey')
        c.node('cu_gerenciar_personal', 'Gerenciar\nPersonal', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_generar_reportes', 'Generar\nReportes', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_configurar_sistema', 'Configurar\nSistema', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_monitorear_ventas', 'Monitorear\nVentas', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_ver_dashboard', 'Ver\nDashboard', shape='ellipse', style='filled', fillcolor='white')
   
    dot.edge('admin', 'cu_gerenciar_personal')
    dot.edge('admin', 'cu_generar_reportes')
    dot.edge('admin', 'cu_configurar_sistema')
    dot.edge('admin', 'cu_monitorear_ventas')
    dot.edge('admin', 'cu_ver_dashboard')
   
    dot.render('diagramas/4.7_casos_uso/02_casos_uso_admin', view=False, cleanup=True)
   
    # Diagrama 4.7.3 - Casos de Uso para Cliente
    dot = Digraph('casos_uso_cliente', format='png')
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.8')
   
    dot.node('cliente', '\nCliente', shape='ellipse', style='filled', fillcolor='lightblue')
    dot.node('whatsapp', '\nWhatsApp', shape='ellipse', style='filled', fillcolor='lightgreen')
   
    with dot.subgraph(name='cluster_cliente') as c:
        c.attr(label='Funcionalidades para Cliente', style='rounded,filled', fillcolor='lightgrey')
        c.node('cu_realizar_pedido', 'Realizar\nPedido', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_pagar_pedido', 'Pagar\nPedido', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_seguir_entrega', 'Seguir\nEntrega', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_chatear_ia', 'Chatear con IA', shape='ellipse', style='filled', fillcolor='white')
        c.node('cu_calificar_servicio', 'Calificar\nServicio', shape='ellipse', style='filled', fillcolor='white')
   
    dot.edge('cliente', 'whatsapp')
    dot.edge('whatsapp', 'cu_realizar_pedido')
    dot.edge('whatsapp', 'cu_pagar_pedido')
    dot.edge('cliente', 'cu_seguir_entrega')
    dot.edge('whatsapp', 'cu_chatear_ia')
    dot.edge('cliente', 'cu_calificar_servicio')
   
    dot.render('diagramas/4.7_casos_uso/03_casos_uso_cliente', view=False, cleanup=True)
   
    print(" 4.7 - 3 Diagramas de Casos de Uso generados")

# ============================================================================
# PUNTO 4.8 - DIAGRAMAS DE CLASES DEL SISTEMA
# ============================================================================

def generar_4_8_diagramas_clases():
    """Genera diagramas de clases UML"""
    print("=== Generando Diagramas de Clases (4.8) ===")
   
    # Diagrama 4.8.1 - Diagrama de Clases Principal
    dot = Digraph('clases_principal', format='png')
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='1.0')
   
    # Paquete Gestión de Clientes
    with dot.subgraph(name='cluster_clientes') as c:
        c.attr(label='Gestión de Clientes', style='rounded,filled', fillcolor='lightblue')
       
        c.node('Cliente', '''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
         <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>Cliente</B></TD></TR>
         <TR><TD ALIGN="LEFT">- id: int</TD></TR>
         <TR><TD ALIGN="LEFT">- nombre: string</TD></TR>
         <TR><TD ALIGN="LEFT">- telefono: string</TD></TR>
         <TR><TD ALIGN="LEFT">- direccion: string</TD></TR>
         <TR><TD ALIGN="LEFT">- whatsapp: string</TD></TR>
         <HR/>
         <TR><TD ALIGN="LEFT">+ registrar(): void</TD></TR>
         <TR><TD ALIGN="LEFT">+ actualizar(): void</TD></TR>
         <TR><TD ALIGN="LEFT">+ consultar(): Cliente</TD></TR>
        </TABLE>>''', shape='plaintext')
       
        c.node('HistorialCliente', '''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
         <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>HistorialCliente</B></TD></TR>
         <TR><TD ALIGN="LEFT">- clienteId: int</TD></TR>
         <TR><TD ALIGN="LEFT">- pedidos: List&lt;Pedido&gt;</TD></TR>
         <TR><TD ALIGN="LEFT">- fechaRegistro: Date</TD></TR>
         <HR/>
         <TR><TD ALIGN="LEFT">+ obtenerPedidos(): List</TD></TR>
         <TR><TD ALIGN="LEFT">+ calcularFrecuencia(): int</TD></TR>
        </TABLE>>''', shape='plaintext')
   
    # Paquete Gestión de Pedidos
    with dot.subgraph(name='cluster_pedidos') as c:
        c.attr(label='Gestión de Pedidos', style='rounded,filled', fillcolor='lightgreen')
       
        c.node('Pedido', '''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
         <TR><TD COLSPAN="2" BGCOLOR="lightgreen"><B>Pedido</B></TD></TR>
         <TR><TD ALIGN="LEFT">- id: int</TD></TR>
         <TR><TD ALIGN="LEFT">- clienteId: int</TD></TR>
         <TR><TD ALIGN="LEFT">- estado: string</TD></TR>
         <TR><TD ALIGN="LEFT">- fechaHora: DateTime</TD></TR>
         <TR><TD ALIGN="LEFT">- total: float</TD></TR>
         <HR/>
         <TR><TD ALIGN="LEFT">+ crear(): void</TD></TR>
         <TR><TD ALIGN="LEFT">+ actualizarEstado(): void</TD></TR>
         <TR><TD ALIGN="LEFT">+ calcularTotal(): float</TD></TR>
        </TABLE>>''', shape='plaintext')
       
        c.node('ItemPedido', '''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
         <TR><TD COLSPAN="2" BGCOLOR="lightgreen"><B>ItemPedido</B></TD></TR>
         <TR><TD ALIGN="LEFT">- productoId: int</TD></TR>
         <TR><TD ALIGN="LEFT">- cantidad: int</TD></TR>
         <TR><TD ALIGN="LEFT">- precio: float</TD></TR>
         <HR/>
         <TR><TD ALIGN="LEFT">+ calcularSubtotal(): float</TD></TR>
        </TABLE>>''', shape='plaintext')
   
    # Paquete Gestión de Productos
    with dot.subgraph(name='cluster_productos') as c:
        c.attr(label='Gestión de Productos', style='rounded,filled', fillcolor='lightyellow')
       
        c.node('Producto', '''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
         <TR><TD COLSPAN="2" BGCOLOR="lightyellow"><B>Producto</B></TD></TR>
         <TR><TD ALIGN="LEFT">- id: int</TD></TR>
         <TR><TD ALIGN="LEFT">- nombre: string</TD></TR>
         <TR><TD ALIGN="LEFT">- descripcion: string</TD></TR>
         <TR><TD ALIGN="LEFT">- precio: float</TD></TR>
         <TR><TD ALIGN="LEFT">- stock: int</TD></TR>
         <HR/>
         <TR><TD ALIGN="LEFT">+ agregar(): void</TD></TR>
         <TR><TD ALIGN="LEFT">+ actualizar(): void</TD></TR>
         <TR><TD ALIGN="LEFT">+ verificarStock(): boolean</TD></TR>
        </TABLE>>''', shape='plaintext')
       
        c.node('Categoria', '''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
         <TR><TD COLSPAN="2" BGCOLOR="lightyellow"><B>Categoria</B></TD></TR>
         <TR><TD ALIGN="LEFT">- id: int</TD></TR>
         <TR><TD ALIGN="LEFT">- nombre: string</TD></TR>
         <HR/>
         <TR><TD ALIGN="LEFT">+ agregarProducto(): void</TD></TR>
        </TABLE>>''', shape='plaintext')
   
    # Paquete Notificaciones
    with dot.subgraph(name='cluster_notificaciones') as c:
        c.attr(label='Sistema de Notificaciones', style='rounded,filled', fillcolor='lightpink')
       
        c.node('Notificacion', '''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
         <TR><TD COLSPAN="2" BGCOLOR="lightpink"><B>Notificacion</B></TD></TR>
         <TR><TD ALIGN="LEFT">- id: int</TD></TR>
         <TR><TD ALIGN="LEFT">- tipo: string</TD></TR>
         <TR><TD ALIGN="LEFT">- mensaje: string</TD></TR>
         <TR><TD ALIGN="LEFT">- destinatario: string</TD></TR>
         <HR/>
         <TR><TD ALIGN="LEFT">+ enviar(): boolean</TD></TR>
         <TR><TD ALIGN="LEFT">+ programar(): void</TD></TR>
        </TABLE>>''', shape='plaintext')
       
        c.node('CanalWhatsApp', '''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
         <TR><TD COLSPAN="2" BGCOLOR="lightpink"><B>CanalWhatsApp</B></TD></TR>
         <TR><TD ALIGN="LEFT">- numeroDestino: string</TD></TR>
         <TR><TD ALIGN="LEFT">- apiKey: string</TD></TR>
         <HR/>
         <TR><TD ALIGN="LEFT">+ enviarMensaje(): void</TD></TR>
         <TR><TD ALIGN="LEFT">+ verificarEstado(): string</TD></TR>
        </TABLE>>''', shape='plaintext')
   
    # Paquete IA y Procesamiento
    with dot.subgraph(name='cluster_ia') as c:
        c.attr(label='IA y Procesamiento', style='rounded,filled', fillcolor='lightgrey')
       
        c.node('IAProcesamiento', '''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
         <TR><TD COLSPAN="2" BGCOLOR="lightgrey"><B>IAProcesamiento</B></TD></TR>
         <TR><TD ALIGN="LEFT">- modelo: string</TD></TR>
         <TR><TD ALIGN="LEFT">- token: string</TD></TR>
         <HR/>
         <TR><TD ALIGN="LEFT">+ procesarMensaje(): string</TD></TR>
         <TR><TD ALIGN="LEFT">+ generarRespuesta(): string</TD></TR>
         <TR><TD ALIGN="LEFT">+ analizarIntencion(): string</TD></TR>
        </TABLE>>''', shape='plaintext')
       
        c.node('MensajeWhatsApp', '''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
         <TR><TD COLSPAN="2" BGCOLOR="lightgrey"><B>MensajeWhatsApp</B></TD></TR>
         <TR><TD ALIGN="LEFT">- remitente: string</TD></TR>
         <TR><TD ALIGN="LEFT">- contenido: string</TD></TR>
         <TR><TD ALIGN="LEFT">- timestamp: DateTime</TD></TR>
         <HR/>
         <TR><TD ALIGN="LEFT">+ clasificar(): string</TD></TR>
        </TABLE>>''', shape='plaintext')
   
    # Relaciones
    dot.edge('Cliente', 'Pedido', label='1..*', dir='both', arrowtail='diamond')
    dot.edge('Pedido', 'ItemPedido', label='1..*', dir='both', arrowtail='diamond')
    dot.edge('ItemPedido', 'Producto', label='1', dir='both')
    dot.edge('Producto', 'Categoria', label='*', dir='both')
    dot.edge('Notificacion', 'CanalWhatsApp', label='usa', dir='both')
    dot.edge('IAProcesamiento', 'MensajeWhatsApp', label='procesa', dir='both')
   
    dot.render('diagramas/4.8_clases/01_diagrama_clases_principal', view=False, cleanup=True)
   
    # Diagrama 4.8.2 - Clases de Gestión de Pedidos Detallado
    dot = Digraph('clases_pedidos_detalle', format='png')
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.8')
   
    dot.node('PedidoClase', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
     <TR><TD COLSPAN="2" BGCOLOR="lightgreen"><B>Pedido</B></TD></TR>
     <TR><TD ALIGN="LEFT">- id: int</TD></TR>
     <TR><TD ALIGN="LEFT">- cliente: Cliente</TD></TR>
     <TR><TD ALIGN="LEFT">- items: List&lt;ItemPedido&gt;</TD></TR>
     <TR><TD ALIGN="LEFT">- estado: EstadoPedido</TD></TR>
     <TR><TD ALIGN="LEFT">- fechaCreacion: DateTime</TD></TR>
     <TR><TD ALIGN="LEFT">- total: decimal</TD></TR>
     <HR/>
     <TR><TD ALIGN="LEFT">+ agregarItem(): void</TD></TR>
     <TR><TD ALIGN="LEFT">+ calcularTotal(): decimal</TD></TR>
     <TR><TD ALIGN="LEFT">+ cambiarEstado(): void</TD></TR>
     <TR><TD ALIGN="LEFT">+ generarFactura(): Factura</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('EstadoPedido', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
     <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>EstadoPedido</B></TD></TR>
     <TR><TD ALIGN="LEFT"><<enumeration>></TD></TR>
     <TR><TD ALIGN="LEFT">RECIBIDO</TD></TR>
     <TR><TD ALIGN="LEFT">EN_PREPARACION</TD></TR>
     <TR><TD ALIGN="LEFT">LISTO</TD></TR>
     <TR><TD ALIGN="LEFT">EN_CAMINO</TD></TR>
     <TR><TD ALIGN="LEFT">ENTREGADO</TD></TR>
     <TR><TD ALIGN="LEFT">CANCELADO</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('Factura', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
     <TR><TD COLSPAN="2" BGCOLOR="lightyellow"><B>Factura</B></TD></TR>
     <TR><TD ALIGN="LEFT">- numero: string</TD></TR>
     <TR><TD ALIGN="LEFT">- fecha: Date</TD></TR>
     <TR><TD ALIGN="LEFT">- subtotal: decimal</TD></TR>
     <TR><TD ALIGN="LEFT">- impuestos: decimal</TD></TR>
     <TR><TD ALIGN="LEFT">- total: decimal</TD></TR>
     <HR/>
     <TR><TD ALIGN="LEFT">+ generarPDF(): byte[]</TD></TR>
     <TR><TD ALIGN="LEFT">+ enviarWhatsApp(): boolean</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.edge('PedidoClase', 'EstadoPedido', label='tiene', dir='both')
    dot.edge('PedidoClase', 'Factura', label='genera', dir='both')
   
    dot.render('diagramas/4.8_clases/02_clases_pedidos_detalle', view=False, cleanup=True)
   
    # Diagrama 4.8.3 - Clases de IA y WhatsApp
    dot = Digraph('clases_ia_whatsapp', format='png')
    dot.attr(rankdir='LR', nodesep='0.5', ranksep='0.8')
   
    dot.node('ChatbotIA', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
     <TR><TD COLSPAN="2" BGCOLOR="lightgrey"><B>ChatbotIA</B></TD></TR>
     <TR><TD ALIGN="LEFT">- apiKey: string</TD></TR>
     <TR><TD ALIGN="LEFT">- modelo: string</TD></TR>
     <TR><TD ALIGN="LEFT">- historial: List&lt;Mensaje&gt;</TD></TR>
     <HR/>
     <TR><TD ALIGN="LEFT">+ procesarEntrada(): string</TD></TR>
     <TR><TD ALIGN="LEFT">+ generarRespuesta(): string</TD></TR>
     <TR><TD ALIGN="LEFT">+ aprenderDeInteraccion(): void</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('WhatsAppService', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
     <TR><TD COLSPAN="2" BGCOLOR="lightgreen"><B>WhatsAppService</B></TD></TR>
     <TR><TD ALIGN="LEFT">- phoneNumberId: string</TD></TR>
     <TR><TD ALIGN="LEFT">- accessToken: string</TD></TR>
     <HR/>
     <TR><TD ALIGN="LEFT">+ enviarMensaje(): Response</TD></TR>
     <TR><TD ALIGN="LEFT">+ recibirMensaje(): Mensaje</TD></TR>
     <TR><TD ALIGN="LEFT">+ verificarEntrega(): boolean</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('MensajeClase', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
     <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>Mensaje</B></TD></TR>
     <TR><TD ALIGN="LEFT">- from: string</TD></TR>
     <TR><TD ALIGN="LEFT">- text: string</TD></TR>
     <TR><TD ALIGN="LEFT">- timestamp: DateTime</TD></TR>
     <TR><TD ALIGN="LEFT">- type: string</TD></TR>
     <HR/>
     <TR><TD ALIGN="LEFT">+ esPedido(): boolean</TD></TR>
     <TR><TD ALIGN="LEFT">+ esConsulta(): boolean</TD></TR>
     <TR><TD ALIGN="LEFT">+ esPago(): boolean</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.edge('WhatsAppService', 'MensajeClase', label='recibe/envía', dir='both')
    dot.edge('ChatbotIA', 'MensajeClase', label='procesa', dir='both')
   
    dot.render('diagramas/4.8_clases/03_clases_ia_whatsapp', view=False, cleanup=True)
   
    print(" 4.8 - 3 Diagramas de Clases generados")

# ============================================================================
# PUNTO 4.9 - DIAGRAMAS DE COMPONENTES Y DESPLIEGUE
# ============================================================================

def generar_4_9_componentes_despliegue():
    """Genera diagramas de componentes y despliegue"""
    print("=== Generando Diagramas de Componentes y Despliegue (4.9) ===")
   
    # Diagrama 4.9.1 - Diagrama de Componentes
    dot = Digraph('componentes_sistema', format='png')
    dot.attr(rankdir='TB', nodesep='0.8', ranksep='1.0')
   
    # Componente principal
    dot.node('sistema_principal', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
     <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>Sistema Cony Chips</B></TD></TR>
     <TR><TD ALIGN="LEFT"><<component>></TD></TR>
     <TR><TD ALIGN="LEFT">Versión: 2.0</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    # Subcomponentes
    with dot.subgraph(name='cluster_componentes') as c:
        c.attr(label='Componentes del Sistema', style='rounded,filled', fillcolor='lightgrey')
       
        c.node('comp_gestion', '''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
         <TR><TD COLSPAN="2" BGCOLOR="lightgreen"><B>Módulo Gestión</B></TD></TR>
         <TR><TD ALIGN="LEFT"><<component>></TD></TR>
         <TR><TD PORT="p1">Clientes</TD></TR>
         <TR><TD PORT="p2">Pedidos</TD></TR>
         <TR><TD PORT="p3">Productos</TD></TR>
        </TABLE>>''', shape='plaintext')
       
        c.node('comp_notificaciones', '''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
         <TR><TD COLSPAN="2" BGCOLOR="lightyellow"><B>Módulo Notificaciones</B></TD></TR>
         <TR><TD ALIGN="LEFT"><<component>></TD></TR>
         <TR><TD PORT="p1">WhatsApp API</TD></TR>
         <TR><TD PORT="p2">Email Service</TD></TR>
        </TABLE>>''', shape='plaintext')
       
        c.node('comp_ia', '''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
         <TR><TD COLSPAN="2" BGCOLOR="lightpink"><B>Módulo IA</B></TD></TR>
         <TR><TD ALIGN="LEFT"><<component>></TD></TR>
         <TR><TD PORT="p1">Chatbot</TD></TR>
         <TR><TD PORT="p2">Procesamiento NLP</TD></TR>
        </TABLE>>''', shape='plaintext')
       
        c.node('comp_database', '''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
         <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>Base de Datos</B></TD></TR>
         <TR><TD ALIGN="LEFT"><<component>></TD></TR>
         <TR><TD PORT="p1">MySQL</TD></TR>
         <TR><TD PORT="p2">Redis Cache</TD></TR>
        </TABLE>>''', shape='plaintext')
   
    # Interfaces
    dot.node('interfaz_web', '\nInterfaz Web', shape='component', style='filled', fillcolor='white')
    dot.node('interfaz_movil', '\nApp Móvil', shape='component', style='filled', fillcolor='white')
    dot.node('api_whatsapp', '\nAPI WhatsApp', shape='component', style='filled', fillcolor='white')
   
    # Dependencias
    dot.edge('interfaz_web', 'comp_gestion', label='usa')
    dot.edge('interfaz_movil', 'comp_gestion', label='usa')
    dot.edge('api_whatsapp', 'comp_notificaciones', label='consume')
    dot.edge('comp_gestion', 'comp_database', label='almacena en')
    dot.edge('comp_notificaciones', 'api_whatsapp', label='envía por')
    dot.edge('comp_ia', 'comp_gestion', label='procesa datos de')
   
    dot.render('diagramas/4.9_componentes_despliegue/01_diagrama_componentes', view=False, cleanup=True)
   
    # Diagrama 4.9.2 - Diagrama de Despliegue
    dot = Digraph('despliegue_sistema', format='png')
    dot.attr(rankdir='TB', nodesep='0.8', ranksep='1.0')
   
    # Nodos de despliegue
    dot.node('servidor_web', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
     <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>Servidor Web</B></TD></TR>
     <TR><TD ALIGN="LEFT"><<deployment>></TD></TR>
     <TR><TD ALIGN="LEFT">Ubuntu 22.04</TD></TR>
     <TR><TD ALIGN="LEFT">Apache/Nginx</TD></TR>
     <TR><TD ALIGN="LEFT">PHP 8.2</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('servidor_db', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
     <TR><TD COLSPAN="2" BGCOLOR="lightgreen"><B>Servidor Base de Datos</B></TD></TR>
     <TR><TD ALIGN="LEFT"><<deployment>></TD></TR>
     <TR><TD ALIGN="LEFT">MySQL 8.0</TD></TR>
     <TR><TD ALIGN="LEFT">Redis 7.0</TD></TR>
     <TR><TD ALIGN="LEFT">Backup automático</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('servidor_ia', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
     <TR><TD COLSPAN="2" BGCOLOR="lightyellow"><B>Servidor IA/API</B></TD></TR>
     <TR><TD ALIGN="LEFT"><<deployment>></TD></TR>
     <TR><TD ALIGN="LEFT">Python 3.10</TD></TR>
     <TR><TD ALIGN="LEFT">FastAPI</TD></TR>
     <TR><TD ALIGN="LEFT">TensorFlow</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    # Dispositivos cliente
    dot.node('cliente_pc', '\nComputadora\nCliente/Admin', shape='box3d', style='filled', fillcolor='white')
    dot.node('cliente_movil', '\nTeléfono Móvil\nCliente', shape='box3d', style='filled', fillcolor='white')
    dot.node('whatsapp_cloud', '\nMeta WhatsApp\nCloud API', shape='cylinder', style='filled', fillcolor='lightgrey')
   
    # Artifacts (componentes desplegados)
    dot.node('app_web', '\nAplicación Web\n(React)', shape='folder', style='filled', fillcolor='white')
    dot.node('api_rest', '\nAPI REST\n(Node.js)', shape='folder', style='filled', fillcolor='white')
    dot.node('servicio_ia', '🤖\nServicio IA\n(Python)', shape='folder', style='filled', fillcolor='white')
    dot.node('db_mysql', '\nMySQL\nBase de Datos', shape='cylinder', style='filled', fillcolor='white')
   
    # Conexiones de red
    dot.edge('cliente_pc', 'servidor_web', label='HTTP/HTTPS\n(443)')
    dot.edge('cliente_movil', 'servidor_web', label='HTTP/HTTPS\n(443)')
    dot.edge('servidor_web', 'servidor_db', label='MySQL\n(3306)')
    dot.edge('servidor_web', 'servidor_ia', label='API REST\n(8000)')
    dot.edge('servidor_ia', 'whatsapp_cloud', label='Webhook\nHTTPS')
   
    # Despliegue de artifacts
    dot.edge('servidor_web', 'app_web', label='hosts', style='dashed')
    dot.edge('servidor_web', 'api_rest', label='hosts', style='dashed')
    dot.edge('servidor_ia', 'servicio_ia', label='hosts', style='dashed')
    dot.edge('servidor_db', 'db_mysql', label='hosts', style='dashed')
   
    dot.render('diagramas/4.9_componentes_despliegue/02_diagrama_despliegue', view=False, cleanup=True)
   
    # Diagrama 4.9.3 - Arquitectura de Comunicación
    dot = Digraph('arquitectura_comunicacion', format='png')
    dot.attr(rankdir='LR', nodesep='0.8', ranksep='1.0')
   
    # Componentes de comunicación
    dot.node('frontend', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
     <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>Frontend</B></TD></TR>
     <TR><TD ALIGN="LEFT">React.js</TD></TR>
     <TR><TD ALIGN="LEFT">Bootstrap</TD></TR>
     <TR><TD ALIGN="LEFT">WebSocket</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('backend', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
     <TR><TD COLSPAN="2" BGCOLOR="lightgreen"><B>Backend API</B></TD></TR>
     <TR><TD ALIGN="LEFT">Node.js/Express</TD></TR>
     <TR><TD ALIGN="LEFT">JWT Auth</TD></TR>
     <TR><TD ALIGN="LEFT">REST API</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('whatsapp_service', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
     <TR><TD COLSPAN="2" BGCOLOR="lightyellow"><B>WhatsApp Service</B></TD></TR>
     <TR><TD ALIGN="LEFT">Webhook Handler</TD></TR>
     <TR><TD ALIGN="LEFT">Message Queue</TD></TR>
     <TR><TD ALIGN="LEFT">Template Manager</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('ia_service', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
     <TR><TD COLSPAN="2" BGCOLOR="lightpink"><B>IA Service</B></TD></TR>
     <TR><TD ALIGN="LEFT">NLP Processing</TD></TR>
     <TR><TD ALIGN="LEFT">Intent Recognition</TD></TR>
     <TR><TD ALIGN="LEFT">Response Generation</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    dot.node('database', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
     <TR><TD COLSPAN="2" BGCOLOR="lightgrey"><B>Database Layer</B></TD></TR>
     <TR><TD ALIGN="LEFT">MySQL</TD></TR>
     <TR><TD ALIGN="LEFT">Redis Cache</TD></TR>
     <TR><TD ALIGN="LEFT">ORM (Sequelize)</TD></TR>
    </TABLE>>''', shape='plaintext')
   
    # Protocolos de comunicación
    dot.edge('frontend', 'backend', label='REST API\nJSON/HTTPS')
    dot.edge('backend', 'database', label='SQL/ORM')
    dot.edge('whatsapp_service', 'backend', label='Webhook\nEvents')
    dot.edge('whatsapp_service', 'ia_service', label='Message\nProcessing')
    dot.edge('ia_service', 'backend', label='Data\nAccess')
    dot.edge('ia_service', 'database', label='Read/Write')
   
    dot.render('diagramas/4.9_componentes_despliegue/03_arquitectura_comunicacion', view=False, cleanup=True)
   
    print(" 4.9 - 3 Diagramas de Componentes y Despliegue generados")

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal que genera todos los diagramas"""
    print("=== GENERADOR DE DIAGRAMAS UML - SISTEMA CONY CHIPS ===")
    print("Desarrollado por: [Tu Nombre]")
    print("Versión: 2.0")
    print("=" * 60)
   
    # Crear directorios
    crear_directorios()
   
    # Generar todos los diagramas
    generar_4_6_diagramas_objetos()
    generar_4_7_casos_uso()
    generar_4_8_diagramas_clases()
    generar_4_9_componentes_despliegue()
   
    print("\n" + "=" * 60)
    print(" GENERACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print("\nArchivos generados en:")
    print("  - diagramas/4.6_objetos/")
    print("  - diagramas/4.7_casos_uso/")
    print("  - diagramas/4.8_clases/")
    print("  - diagramas/4.9_componentes_despliegue/")
    print("\nTotal de diagramas generados: 17")
    print("\nInstrucciones para visualizar:")
    print("1. Asegúrate de tener Graphviz instalado")
    print("2. Los archivos .png están listos para usar")
    print("3. Los archivos .gv pueden ser editados")

# ============================================================================
# EJECUCIÓN
# ============================================================================

if __name__ == "__main__":
    main()