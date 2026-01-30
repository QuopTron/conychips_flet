class ERRORES_AUTENTICACION:
    
    CREDENCIALES_INVALIDAS = "Las credenciales ingresadas son incorrectas"
    EMAIL_INVALIDO = "El formato del correo electrónico es inválido"
    CONTRASENA_DEBIL = "La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número"
    USUARIO_NO_ENCONTRADO = "No se encontró ningún usuario con este correo"
    USUARIO_YA_EXISTE = "Ya existe un usuario registrado con este correo"
    USUARIO_INACTIVO = "Esta cuenta ha sido deshabilitada"
    USUARIO_NO_VERIFICADO = "Debes verificar tu cuenta antes de iniciar sesión"
    
    TOKEN_INVALIDO = "El token proporcionado es inválido"
    TOKEN_EXPIRADO = "El token ha expirado"
    TOKEN_NO_ENCONTRADO = "No se encontró el token"
    
    SESION_EXPIRADA = "Tu sesión ha expirado, por favor inicia sesión nuevamente"
    SESION_INVALIDA = "La sesión es inválida"
    
    PERMISOS_INSUFICIENTES = "No tienes permisos para realizar esta acción"
    ROL_REQUERIDO = "Se requiere un rol específico para acceder a este recurso"
    
    DISPOSITIVO_NO_AUTORIZADO = "Este dispositivo no está autorizado"
    HUELLA_INVALIDA = "La huella del dispositivo es inválida"

class ERRORES_VALIDACION:
    
    CAMPO_REQUERIDO = "Este campo es obligatorio"
    CAMPO_VACIO = "Este campo no puede estar vacío"
    CAMPO_INVALIDO = "El valor ingresado es inválido"
    
    LONGITUD_MINIMA = "Debe tener al menos {min} caracteres"
    LONGITUD_MAXIMA = "No puede exceder los {max} caracteres"
    LONGITUD_EXACTA = "Debe tener exactamente {length} caracteres"
    
    FORMATO_INVALIDO = "El formato del campo es incorrecto"
    TIPO_INVALIDO = "El tipo de dato es incorrecto"
    
    VALOR_MINIMO = "El valor mínimo es {min}"
    VALOR_MAXIMO = "El valor máximo es {max}"
    RANGO_INVALIDO = "El valor debe estar entre {min} y {max}"
    
    FECHA_INVALIDA = "La fecha ingresada es inválida"
    FECHA_FUTURA = "La fecha no puede ser futura"
    FECHA_PASADA = "La fecha no puede ser pasada"
    
    NUMERO_INVALIDO = "Debe ser un número válido"
    NUMERO_POSITIVO = "El número debe ser positivo"
    NUMERO_NEGATIVO = "El número debe ser negativo"
    
    URL_INVALIDA = "La URL ingresada es inválida"
    TELEFONO_INVALIDO = "El número de teléfono es inválido"

class ERRORES_BASE_DATOS:
    
    CONEXION_FALLIDA = "No se pudo conectar a la base de datos"
    OPERACION_FALLIDA = "La operación en la base de datos falló"
    REGISTRO_NO_ENCONTRADO = "No se encontró el registro solicitado"
    REGISTRO_DUPLICADO = "Ya existe un registro con estos datos"
    CONSTRAINT_VIOLADO = "Se violó una restricción de la base de datos"
    RELACION_INVALIDA = "La relación entre entidades es inválida"
    TRANSACCION_FALLIDA = "La transacción falló y fue revertida"

class ERRORES_WEBSOCKET:
    
    CONEXION_FALLIDA = "No se pudo establecer conexión con el servidor"
    CONEXION_PERDIDA = "Se perdió la conexión con el servidor"
    RECONEXION_FALLIDA = "No se pudo reconectar al servidor"
    TIMEOUT = "La operación excedió el tiempo de espera"
    MENSAJE_INVALIDO = "El mensaje recibido es inválido"
    ENVIO_FALLIDO = "No se pudo enviar el mensaje"

class ERRORES_GENERALES:
    
    ERROR_DESCONOCIDO = "Ocurrió un error inesperado"
    OPERACION_NO_PERMITIDA = "Esta operación no está permitida"
    RECURSO_NO_ENCONTRADO = "El recurso solicitado no fue encontrado"
    ACCESO_DENEGADO = "Acceso denegado"
    SERVICIO_NO_DISPONIBLE = "El servicio no está disponible en este momento"
    LIMITE_EXCEDIDO = "Se excedió el límite permitido"
    CONFIGURACION_INVALIDA = "La configuración es inválida"

class MENSAJES_EXITO:
    
    OPERACION_EXITOSA = "Operación completada exitosamente"
    GUARDADO_EXITOSO = "Los datos se guardaron correctamente"
    ACTUALIZADO_EXITOSO = "Los datos se actualizaron correctamente"
    ELIMINADO_EXITOSO = "El registro se eliminó correctamente"
    CREADO_EXITOSO = "El registro se creó correctamente"
    
    SESION_INICIADA = "Bienvenido, has iniciado sesión correctamente"
    SESION_CERRADA = "Has cerrado sesión correctamente"
    
    EMAIL_ENVIADO = "El correo electrónico se envió correctamente"
    CONTRASENA_ACTUALIZADA = "Tu contraseña se actualizó correctamente"
    PERFIL_ACTUALIZADO = "Tu perfil se actualizó correctamente"
    
    CONEXION_EXITOSA = "Conexión establecida correctamente"
    SINCRONIZACION_EXITOSA = "Sincronización completada"

class MENSAJES_CONFIRMACION:
    
    CONFIRMAR_ELIMINAR = "¿Estás seguro que deseas eliminar este registro?"
    CONFIRMAR_GUARDAR = "¿Deseas guardar los cambios realizados?"
    CONFIRMAR_CANCELAR = "¿Deseas cancelar? Se perderán los cambios no guardados"
    CONFIRMAR_SALIR = "¿Estás seguro que deseas salir?"
    CONFIRMAR_CERRAR_SESION = "¿Deseas cerrar sesión?"
    
    SI = "Sí"
    NO = "No"
    ACEPTAR = "Aceptar"
    CANCELAR = "Cancelar"
