"""
Sistema de Consumo Automático de Insumos
- Deducir insumos cuando se vende un producto
- Crear movimientos de insumo de tipo PRODUCCION
- Generar alertas si stock baja del mínimo
"""

from core.base_datos.ConfiguracionBD import (
    OBTENER_SESION, 
    CERRAR_SESION,
    MODELO_INSUMO,
    MODELO_FORMULA,
    MODELO_MOVIMIENTO_INSUMO,
    MODELO_ALERTA_INSUMO,
    MODELO_PRODUCTO
)
from core.utilidades.ConversionesUnidades import convertir, normalizar_unidad
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ========================================
# DEDUCIR INSUMOS POR PRODUCTO VENDIDO
# ========================================

def DEDUCIR_INSUMOS_POR_VENTA(producto_id: int, cantidad_productos: int = 1):
    """
    Deduce automáticamente los insumos cuando se vende un producto
    
    Proceso:
    1. Obtiene la fórmula del producto (qué insumos lleva)
    2. Calcula total = insumo_por_unidad * cantidad_vendida
    3. Deduce del stock del insumo
    4. Crea movimiento de tipo PRODUCCION
    5. Genera alerta si stock baja del mínimo
    
    Ejemplo:
    - Se vende hamburguesa (cantidad=1)
    - Fórmula: 30gr carne, 10gr queso
    - Se deduce: 30gr de carne, 10gr de queso
    - Si quedó < stock_minimo → crear alerta
    
    Args:
        producto_id: ID del producto vendido
        cantidad_productos: Cantidad de productos vendidos (ej: 5 hamburguesas)
    
    Returns:
        dict con resultado de la deducción
    """
    try:
        with OBTENER_SESION() as sesion:
            # 1. Obtener producto
            producto = sesion.query(MODELO_PRODUCTO).filter_by(ID=producto_id).first()
            if not producto:
                logger.warning(f"Producto {producto_id} no encontrado")
                return {"exito": False, "error": "Producto no encontrado"}
            
            # 2. Obtener fórmulas del producto (cada fórmula es un insumo)
            formulas = sesion.query(MODELO_FORMULA).filter_by(
                PRODUCTO_ID=producto_id,
                ACTIVA=True
            ).all()
            
            if not formulas:
                logger.info(f"Producto {producto.NOMBRE} no tiene fórmulas definidas")
                return {
                    "exito": True,
                    "mensaje": "Producto sin fórmulas, no se deducen insumos",
                    "insumos_deducidos": []
                }
            
            # 3. Deducir cada insumo
            insumos_deducidos = []
            alertas_generadas = []
            
            for formula in formulas:
                insumo = formula.INSUMO
                
                if not insumo:
                    logger.warning(f"Fórmula apunta a insumo no existente")
                    continue
                
                # Cantidad total a deducir = cantidad_por_unidad * cantidad_productos_vendidos
                cantidad_a_deducir = formula.CANTIDAD * cantidad_productos
                
                # Convertir a la unidad del insumo si es necesario
                if formula.UNIDAD != insumo.UNIDAD:
                    try:
                        cantidad_a_deducir = convertir(
                            cantidad_a_deducir,
                            formula.UNIDAD,
                            insumo.UNIDAD
                        )
                        logger.info(f"Conversión: {formula.CANTIDAD} {formula.UNIDAD} → {cantidad_a_deducir} {insumo.UNIDAD}")
                    except Exception as e:
                        logger.error(f"Error en conversión de unidades: {e}")
                        cantidad_a_deducir = formula.CANTIDAD * cantidad_productos
                
                # Stock anterior
                stock_anterior = insumo.STOCK_ACTUAL
                
                # Nuevo stock
                stock_nuevo = stock_anterior - cantidad_a_deducir
                
                # Validar stock suficiente
                if stock_nuevo < 0:
                    logger.warning(
                        f"Stock insuficiente para {insumo.NOMBRE}: "
                        f"disponible {stock_anterior}, se necesita {cantidad_a_deducir}"
                    )
                    insumos_deducidos.append({
                        "insumo_id": insumo.ID,
                        "insumo_nombre": insumo.NOMBRE,
                        "estado": "ERROR",
                        "motivo": "Stock insuficiente",
                        "stock_anterior": stock_anterior,
                        "cantidad_solicitada": cantidad_a_deducir,
                        "unidad": insumo.UNIDAD
                    })
                    continue
                
                # Actualizar stock
                insumo.STOCK_ACTUAL = stock_nuevo
                
                # Crear movimiento de insumo tipo PRODUCCION
                movimiento = MODELO_MOVIMIENTO_INSUMO(
                    INSUMO_ID=insumo.ID,
                    TIPO="PRODUCCION",
                    CANTIDAD=-cantidad_a_deducir,  # Negativo porque es salida
                    STOCK_ANTERIOR=stock_anterior,
                    STOCK_NUEVO=stock_nuevo,
                    OBSERVACION=f"Venta de {cantidad_productos}x {producto.NOMBRE}",
                    FECHA=datetime.utcnow()
                )
                sesion.add(movimiento)
                sesion.flush()  # ← AGREGAR FLUSH
                
                logger.info(
                    f"Deducido {cantidad_a_deducir} {insumo.UNIDAD} de {insumo.NOMBRE} "
                    f"({stock_anterior} → {stock_nuevo})"
                )
                
                insumos_deducidos.append({
                    "insumo_id": insumo.ID,
                    "insumo_nombre": insumo.NOMBRE,
                    "estado": "OK",
                    "stock_anterior": stock_anterior,
                    "cantidad_deducida": cantidad_a_deducir,
                    "stock_nuevo": stock_nuevo,
                    "unidad": insumo.UNIDAD
                })
                
                # 5. Verificar si stock baja del mínimo
                if stock_nuevo < insumo.STOCK_MINIMO:
                    # Crear alerta directamente aquí
                    try:
                        alerta_existente = sesion.query(MODELO_ALERTA_INSUMO).filter(
                            MODELO_ALERTA_INSUMO.INSUMO_ID == insumo.ID,
                            MODELO_ALERTA_INSUMO.RESUELTA == False
                        ).first()
                        
                        if not alerta_existente:
                            alerta = MODELO_ALERTA_INSUMO(
                                INSUMO_ID=insumo.ID,
                                TIPO="STOCK_BAJO",
                                MENSAJE=f"Stock bajo: {stock_nuevo} < {insumo.STOCK_MINIMO} {insumo.UNIDAD}",
                                LEIDA=False,
                                RESUELTA=False,
                                FECHA_CREACION=datetime.utcnow()
                            )
                            sesion.add(alerta)
                            sesion.flush()
                            
                            alertas_generadas.append({
                                "insumo_id": insumo.ID,
                                "insumo_nombre": insumo.NOMBRE,
                                "stock_actual": stock_nuevo,
                                "stock_minimo": insumo.STOCK_MINIMO,
                                "alerta_id": alerta.ID
                            })
                            logger.info(f"Alerta de stock bajo creada para {insumo.NOMBRE}")
                    except Exception as e:
                        logger.error(f"Error al crear alerta: {e}")
            
            # Commit de todos los cambios
            sesion.commit()
            
            return {
                "exito": True,
                "mensaje": f"Insumos deducidos para {cantidad_productos}x {producto.NOMBRE}",
                "producto": {
                    "id": producto.ID,
                    "nombre": producto.NOMBRE
                },
                "insumos_deducidos": insumos_deducidos,
                "alertas_generadas": alertas_generadas
            }
            
    except Exception as e:
        logger.error(f"Error al deducir insumos: {e}", exc_info=True)
        return {
            "exito": False,
            "error": str(e)
        }
    finally:
        CERRAR_SESION()

# ========================================
# VERIFICAR STOCK DE INSUMO
# ========================================

def VERIFICAR_STOCK_INSUMO(insumo_id: int) -> dict:
    """
    Verifica el estado actual de stock de un insumo
    Retorna si está bajo el mínimo
    """
    try:
        with OBTENER_SESION() as sesion:
            insumo = sesion.query(MODELO_INSUMO).filter_by(ID=insumo_id).first()
            
            if not insumo:
                return {
                    "exito": False,
                    "error": "Insumo no encontrado"
                }
            
            stock_bajo = insumo.STOCK_ACTUAL < insumo.STOCK_MINIMO
            
            # Obtener alerta si existe
            alerta = sesion.query(MODELO_ALERTA_INSUMO).filter(
                MODELO_ALERTA_INSUMO.INSUMO_ID == insumo_id,
                MODELO_ALERTA_INSUMO.RESUELTA == False
            ).first()
            
            return {
                "exito": True,
                "insumo": {
                    "id": insumo.ID,
                    "nombre": insumo.NOMBRE,
                    "stock_actual": insumo.STOCK_ACTUAL,
                    "stock_minimo": insumo.STOCK_MINIMO,
                    "stock_bajo": stock_bajo,
                    "diferencia": insumo.STOCK_ACTUAL - insumo.STOCK_MINIMO,
                    "unidad": insumo.UNIDAD
                },
                "alerta_abierta": alerta is not None,
                "alerta_id": alerta.ID if alerta else None
            }
            
    except Exception as e:
        logger.error(f"Error al verificar stock: {e}")
        return {
            "exito": False,
            "error": str(e)
        }
    finally:
        CERRAR_SESION()

# ========================================
# OBTENER INSUMOS CON STOCK BAJO
# ========================================

def OBTENER_INSUMOS_STOCK_BAJO():
    """
    Retorna todos los insumos con stock por debajo del mínimo
    Útil para dashboard
    """
    try:
        with OBTENER_SESION() as sesion:
            insumos = sesion.query(MODELO_INSUMO).filter(
                MODELO_INSUMO.STOCK_ACTUAL < MODELO_INSUMO.STOCK_MINIMO
            ).all()
            
            datos = []
            for insumo in insumos:
                # Verificar si tiene alerta abierta
                alerta = sesion.query(MODELO_ALERTA_INSUMO).filter(
                    MODELO_ALERTA_INSUMO.INSUMO_ID == insumo.ID,
                    MODELO_ALERTA_INSUMO.RESUELTA == False
                ).first()
                
                datos.append({
                    "id": insumo.ID,
                    "nombre": insumo.NOMBRE,
                    "stock_actual": insumo.STOCK_ACTUAL,
                    "stock_minimo": insumo.STOCK_MINIMO,
                    "diferencia": insumo.STOCK_ACTUAL - insumo.STOCK_MINIMO,
                    "unidad": insumo.UNIDAD,
                    "tiene_alerta": alerta is not None,
                    "alerta_id": alerta.ID if alerta else None,
                    "frecuencia_compra": insumo.FRECUENCIA_COMPRA if hasattr(insumo, 'FRECUENCIA_COMPRA') else None,
                    "proxima_compra": insumo.FECHA_PROXIMA_COMPRA.isoformat() if hasattr(insumo, 'FECHA_PROXIMA_COMPRA') and insumo.FECHA_PROXIMA_COMPRA else None
                })
            
            return {
                "exito": True,
                "total": len(datos),
                "insumos": datos
            }
            
    except Exception as e:
        logger.error(f"Error al obtener insumos con stock bajo: {e}")
        return {
            "exito": False,
            "error": str(e)
        }
    finally:
        CERRAR_SESION()
