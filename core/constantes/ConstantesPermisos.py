PERMISOS_DISPONIBLES = [
    "usuarios.crear",
    "usuarios.editar",
    "usuarios.eliminar",
    "usuarios.ver",
    "usuarios.gestionar_roles",
    
    "roles.crear",
    "roles.editar",
    "roles.eliminar",
    "roles.ver",
    "roles.asignar_permisos",
    
    "productos.crear",
    "productos.editar",
    "productos.eliminar",
    "productos.ver",
    
    "pedidos.crear",
    "pedidos.ver",
    "pedidos.ver_todos",
    "pedidos.editar",
    "pedidos.confirmar",
    "pedidos.actualizar_estado",
    "pedidos.marcar_listo",
    "pedidos.preparar",
    "pedidos.entregar",
    "pedidos.notificar_atencion",
    
    "sucursales.crear",
    "sucursales.editar",
    "sucursales.eliminar",
    "sucursales.ver",
    
    "extras.crear",
    "extras.editar",
    "extras.eliminar",
    "extras.ver",
    
    "ofertas.crear",
    "ofertas.editar",
    "ofertas.eliminar",
    "ofertas.ver",
    
    "horarios.asignar",
    "horarios.editar",
    "horarios.ver",
    
    "caja.abrir",
    "caja.cerrar",
    "caja.ver",
    "caja.registrar_ingreso",
    "caja.registrar_egreso",
    "caja.ver_movimientos",
    
    "clientes.ver",
    "clientes.editar",
    "clientes.calificar",
    
    "reportes.crear",
    "reportes.ver",
    "reportes.editar",
    
    "stats.ver",
    "stats.financieros",
    
    "asistencia.ver",
    "asistencia.registrar",
    
    "perfil.editar",
    "perfil.ver",
    
    "insumos.crear",
    "insumos.editar",
    "insumos.eliminar",
    "insumos.ver",
    "insumos.refill",
    
    "proveedores.crear",
    "proveedores.editar",
    "proveedores.eliminar",
    "proveedores.ver",
    
    "auditoria.ver",
    
    "resenas.ver",
    "resenas.crear",
    "resenas.responder",
    
    "limpieza.reportes_crear",
    "limpieza.reportes_ver",
    "limpieza.fotos_subir",
    
    "cocina.pedidos_ver",
    "cocina.pedidos_preparar",
    "cocina.refill_solicitar",
    "cocina.extras_preparar",
    
    "atencion.servir",
    "atencion.caja_abrir",
    "atencion.ventas_registrar",
    
    "motorizado.pedidos_ver",
    "motorizado.ubicacion_actualizar",
    "motorizado.entrega_confirmar",
    "motorizado.chat",
    
    "voucher.subir",
    "voucher.validar",
    "voucher.ver",
    
    "notificaciones.enviar",
    "notificaciones.recibir",
    
    "chat.enviar",
    "chat.recibir",
    
    "gps.actualizar",
    "gps.ver",
]


PERMISOS_POR_ROL_DEFAULT = {
    "CLIENTE": [
        "pedidos.crear",
        "pedidos.ver",
        "perfil.editar",
        "perfil.ver",
        "voucher.subir",
        "resenas.crear",
        "clientes.calificar",
        "notificaciones.recibir",
        "chat.enviar",
        "chat.recibir",
    ],
    
    "MOTORIZADO": [
        "pedidos.ver",
        "pedidos.entregar",
        "motorizado.pedidos_ver",
        "motorizado.ubicacion_actualizar",
        "motorizado.entrega_confirmar",
        "motorizado.chat",
        "gps.actualizar",
        "notificaciones.recibir",
        "chat.enviar",
        "chat.recibir",
    ],
    
    "COCINERO": [
        "pedidos.ver",
        "pedidos.preparar",
        "pedidos.marcar_listo",
        "cocina.pedidos_ver",
        "cocina.pedidos_preparar",
        "cocina.refill_solicitar",
        "cocina.extras_preparar",
        "insumos.ver",
        "insumos.refill",
        "notificaciones.recibir",
        "notificaciones.enviar",
    ],
    
    "ATENCION": [
        "pedidos.ver",
        "pedidos.ver_todos",
        "pedidos.actualizar_estado",
        "pedidos.notificar_atencion",
        "atencion.servir",
        "atencion.caja_abrir",
        "atencion.ventas_registrar",
        "caja.abrir",
        "caja.cerrar",
        "caja.registrar_ingreso",
        "caja.ver_movimientos",
        "productos.ver",
        "extras.ver",
        "notificaciones.recibir",
        "notificaciones.enviar",
    ],
    
    "LIMPIEZA": [
        "limpieza.reportes_crear",
        "limpieza.reportes_ver",
        "limpieza.fotos_subir",
        "reportes.crear",
        "reportes.ver",
        "notificaciones.recibir",
    ],
    
    "ADMIN": [
        "productos.crear",
        "productos.editar",
        "productos.eliminar",
        "productos.ver",
        "pedidos.ver_todos",
        "caja.ver",
        "caja.registrar_egreso",
        "caja.ver_movimientos",
        "insumos.crear",
        "insumos.editar",
        "insumos.ver",
        "proveedores.crear",
        "proveedores.editar",
        "proveedores.ver",
        "stats.ver",
        "stats.financieros",
        "reportes.ver",
        "resenas.ver",
        "resenas.responder",
        "voucher.validar",
        "voucher.ver",
        "notificaciones.enviar",
        "notificaciones.recibir",
    ],
    
    "SUPERADMIN": ["*"],
}

