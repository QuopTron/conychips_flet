import flet as ft


class COLORES:
    
    PRIMARIO = ft.Colors.BLUE_600
    PRIMARIO_CLARO = ft.Colors.BLUE_400
    PRIMARIO_OSCURO = ft.Colors.BLUE_800
    
    SECUNDARIO = ft.Colors.PURPLE_600
    SECUNDARIO_CLARO = ft.Colors.PURPLE_400
    SECUNDARIO_OSCURO = ft.Colors.PURPLE_800
    
    EXITO = ft.Colors.GREEN_600
    EXITO_CLARO = ft.Colors.GREEN_400
    EXITO_OSCURO = ft.Colors.GREEN_800
    
    ADVERTENCIA = ft.Colors.ORANGE_600
    ADVERTENCIA_CLARO = ft.Colors.ORANGE_400
    ADVERTENCIA_OSCURO = ft.Colors.ORANGE_800
    
    PELIGRO = ft.Colors.RED_600
    PELIGRO_CLARO = ft.Colors.RED_400
    PELIGRO_OSCURO = ft.Colors.RED_800
    
    INFO = ft.Colors.CYAN_600
    INFO_CLARO = ft.Colors.CYAN_400
    INFO_OSCURO = ft.Colors.CYAN_800
    
    GRIS = ft.Colors.GREY_600
    GRIS_CLARO = ft.Colors.GREY_400
    GRIS_OSCURO = ft.Colors.GREY_800
    
    FONDO = ft.Colors.GREY_50
    FONDO_BLANCO = ft.Colors.WHITE
    FONDO_OSCURO = ft.Colors.GREY_900
    FONDO_TARJETA = ft.Colors.WHITE
    
    TEXTO = ft.Colors.GREY_900
    TEXTO_SECUNDARIO = ft.Colors.GREY_600
    TEXTO_DESHABILITADO = ft.Colors.GREY_400
    TEXTO_BLANCO = ft.Colors.WHITE
    
    BORDE = ft.Colors.GREY_300
    BORDE_CLARO = ft.Colors.GREY_200
    BORDE_OSCURO = ft.Colors.GREY_400


class TAMANOS:
    
    TEXTO_XS = 10
    TEXTO_SM = 12
    TEXTO_MD = 14
    TEXTO_LG = 16
    TEXTO_XL = 18
    TEXTO_2XL = 20
    TEXTO_3XL = 24
    TEXTO_4XL = 32
    TEXTO_5XL = 40
    
    TITULO = 28
    
    ICONO_XS = 16
    ICONO_SM = 20
    ICONO_MD = 24
    ICONO_LG = 32
    ICONO_XL = 40
    ICONO_2XL = 48
    
    ESPACIADO_XS = 4
    ESPACIADO_SM = 8
    ESPACIADO_MD = 12
    ESPACIADO_LG = 16
    ESPACIADO_XL = 20
    ESPACIADO_2XL = 24
    ESPACIADO_3XL = 32
    
    PADDING_XS = 4
    PADDING_SM = 8
    PADDING_MD = 12
    PADDING_LG = 16
    PADDING_XL = 20
    PADDING_2XL = 24
    
    RADIO_XS = 4
    RADIO_SM = 8
    RADIO_MD = 12
    RADIO_LG = 16
    RADIO_XL = 20
    RADIO_FULL = 9999
    RADIO_BORDE = 8
    
    ANCHO_BOTON = 200
    ALTO_BOTON = 40
    ANCHO_INPUT = 300
    ALTO_INPUT = 40
    ANCHO_CARD = 350
    ALTO_CARD = 200


class ICONOS:
    
    USUARIO = ft.Icons.PERSON
    USUARIOS = ft.Icons.PEOPLE
    EMAIL = ft.Icons.EMAIL
    CONTRASENA = ft.Icons.LOCK
    
    INICIO = ft.Icons.HOME
    DASHBOARD = ft.Icons.DASHBOARD_ROUNDED
    MENU = ft.Icons.MENU
    
    AGREGAR = ft.Icons.ADD
    EDITAR = ft.Icons.EDIT
    ELIMINAR = ft.Icons.DELETE
    GUARDAR = ft.Icons.SAVE
    CANCELAR = ft.Icons.CANCEL
    
    BUSCAR = ft.Icons.SEARCH
    FILTRAR = ft.Icons.FILTER_ALT
    ORDENAR = ft.Icons.SORT
    
    EXITO = ft.Icons.CHECK_CIRCLE
    ERROR = ft.Icons.ERROR
    ADVERTENCIA = ft.Icons.WARNING
    INFO = ft.Icons.INFO
    
    CERRAR_SESION = ft.Icons.LOGOUT_ROUNDED
    INICIAR_SESION = ft.Icons.LOGIN_ROUNDED
    
    PRODUCTOS = ft.Icons.INVENTORY
    PEDIDOS = ft.Icons.SHOPPING_CART
    CLIENTES = ft.Icons.PEOPLE_ALT
    
    ADMIN = ft.Icons.ADMIN_PANEL_SETTINGS
    ROLES = ft.Icons.SHIELD
    PERMISOS = ft.Icons.BADGE
    
    COCINA = ft.Icons.RESTAURANT
    ATENCION = ft.Icons.SUPPORT_AGENT
    LIMPIEZA = ft.Icons.CLEANING_SERVICES
    
    CAJA = ft.Icons.ATTACH_MONEY
    AUDITORIA = ft.Icons.HISTORY
    RESENAS = ft.Icons.STAR
    INSUMOS = ft.Icons.INVENTORY_2
    PROVEEDORES = ft.Icons.LOCAL_SHIPPING
    
    CONFIGURACION = ft.Icons.SETTINGS
    NOTIFICACIONES = ft.Icons.NOTIFICATIONS
    AYUDA = ft.Icons.HELP
    
    ARRIBA = ft.Icons.ARROW_UPWARD
    ABAJO = ft.Icons.ARROW_DOWNWARD
    IZQUIERDA = ft.Icons.ARROW_BACK
    DERECHA = ft.Icons.ARROW_FORWARD
    
    CARGAR = ft.Icons.REFRESH
    EXPANDIR = ft.Icons.EXPAND_MORE
    CONTRAER = ft.Icons.EXPAND_LESS
    
    VISIBLE = ft.Icons.VISIBILITY
    OCULTO = ft.Icons.VISIBILITY_OFF
    
    CALENDARIO = ft.Icons.CALENDAR_TODAY
    RELOJ = ft.Icons.ACCESS_TIME
    UBICACION = ft.Icons.LOCATION_ON
    TELEFONO = ft.Icons.PHONE
    
    DESCARGAR = ft.Icons.DOWNLOAD
    SUBIR = ft.Icons.UPLOAD
    IMPRIMIR = ft.Icons.PRINT
    COMPARTIR = ft.Icons.SHARE
    
    VOUCHER = ft.Icons.RECEIPT
    INGRESO = ft.Icons.ARROW_CIRCLE_UP
    EGRESO = ft.Icons.ARROW_CIRCLE_DOWN
    DINERO = ft.Icons.ATTACH_MONEY
    IMAGEN = ft.Icons.IMAGE
    CHAT = ft.Icons.CHAT
    ENVIAR = ft.Icons.SEND
    CONFIRMAR = ft.Icons.CHECK_CIRCLE
    VER = ft.Icons.VISIBILITY
    ALERTA = ft.Icons.NOTIFICATION_IMPORTANT
    FAVORITO = ft.Icons.FAVORITE
    CARRITO = ft.Icons.SHOPPING_BAG
    PEDIDO = ft.Icons.RECEIPT_LONG
    HISTORIAL = ft.Icons.HISTORY
    ESTADISTICAS = ft.Icons.ANALYTICS
    INVENTARIO = ft.Icons.WAREHOUSE


class ANIMACIONES:
    
    DURACION_RAPIDA = 150
    DURACION_NORMAL = 300
    DURACION_LENTA = 500
    
    CURVA_ENTRADA = "easeIn"
    CURVA_SALIDA = "easeOut"
    CURVA_AMBAS = "easeInOut"
    CURVA_LINEAR = "linear"
