"""
📦 APIs REST para Gestión de Insumos
Endpoints CRUD para insumos, fórmulas y movimientos
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from core.base_datos.ConfiguracionBD import (
    MODELO_INSUMO, MODELO_FORMULA, MODELO_MOVIMIENTO_INSUMO,
    OBTENER_SESION
)
from core.Constantes import ROLES
from core.decoradores.DecoradorVistas import REQUIERE_ROL_API

api_insumos = Blueprint('api_insumos', __name__, url_prefix='/api')

# ==================== INSUMOS ====================

@api_insumos.route('/insumos', methods=['GET'])
@REQUIERE_ROL_API(ROLES.ADMIN)
def obtener_insumos():
    """Obtiene lista de insumos activos"""
    try:
        with OBTENER_SESION() as sesion:
            insumos = sesion.query(MODELO_INSUMO).filter_by(ACTIVO=True).all()
            
            datos = [
                {
                    'ID': i.ID,
                    'NOMBRE': i.NOMBRE,
                    'DESCRIPCION': i.DESCRIPCION,
                    'UNIDAD': i.UNIDAD,
                    'PRECIO_UNITARIO': i.PRECIO_UNITARIO,
                    'STOCK_ACTUAL': i.STOCK_ACTUAL,
                    'STOCK_MINIMO': i.STOCK_MINIMO,
                    'PROVEEDOR': i.PROVEEDOR,
                    'FECHA_CREACION': i.FECHA_CREACION.isoformat() if i.FECHA_CREACION else None,
                }
                for i in insumos
            ]
            
            return jsonify({
                'exito': True,
                'data': datos,
                'total': len(datos),
            }), 200
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': str(e),
        }), 500

@api_insumos.route('/insumos/<int:insumo_id>', methods=['GET'])
@REQUIERE_ROL_API(ROLES.ADMIN)
def obtener_insumo(insumo_id):
    """Obtiene un insumo específico"""
    try:
        with OBTENER_SESION() as sesion:
            insumo = sesion.query(MODELO_INSUMO).filter_by(ID=insumo_id).first()
            
            if not insumo:
                return jsonify({
                    'exito': False,
                    'error': 'Insumo no encontrado',
                }), 404
            
            return jsonify({
                'exito': True,
                'data': {
                    'ID': insumo.ID,
                    'NOMBRE': insumo.NOMBRE,
                    'DESCRIPCION': insumo.DESCRIPCION,
                    'UNIDAD': insumo.UNIDAD,
                    'PRECIO_UNITARIO': insumo.PRECIO_UNITARIO,
                    'STOCK_ACTUAL': insumo.STOCK_ACTUAL,
                    'STOCK_MINIMO': insumo.STOCK_MINIMO,
                    'PROVEEDOR': insumo.PROVEEDOR,
                },
            }), 200
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': str(e),
        }), 500

@api_insumos.route('/insumos', methods=['POST'])
@REQUIERE_ROL_API(ROLES.ADMIN)
def crear_insumo():
    """Crea nuevo insumo"""
    try:
        datos = request.get_json()
        
        # Validar campos requeridos
        if not datos.get('NOMBRE') or not datos.get('UNIDAD') or datos.get('PRECIO_UNITARIO') is None:
            return jsonify({
                'exito': False,
                'error': 'Nombre, Unidad y Precio son obligatorios',
            }), 400
        
        with OBTENER_SESION() as sesion:
            # Validar nombre único
            existe = sesion.query(MODELO_INSUMO).filter_by(NOMBRE=datos['NOMBRE']).first()
            if existe:
                return jsonify({
                    'exito': False,
                    'error': f'Insumo "{datos["NOMBRE"]}" ya existe',
                }), 400
            
            nuevo = MODELO_INSUMO(
                NOMBRE=datos['NOMBRE'],
                DESCRIPCION=datos.get('DESCRIPCION'),
                UNIDAD=datos['UNIDAD'],
                PRECIO_UNITARIO=int(float(datos['PRECIO_UNITARIO']) * 100),
                STOCK_MINIMO=int(datos.get('STOCK_MINIMO', 0)),
                PROVEEDOR=datos.get('PROVEEDOR'),
                ACTIVO=True,
            )
            sesion.add(nuevo)
            sesion.commit()
            
            return jsonify({
                'exito': True,
                'data': {'ID': nuevo.ID},
            }), 201
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': str(e),
        }), 500

@api_insumos.route('/insumos/<int:insumo_id>', methods=['PUT'])
@REQUIERE_ROL_API(ROLES.ADMIN)
def actualizar_insumo(insumo_id):
    """Actualiza un insumo"""
    try:
        datos = request.get_json()
        
        with OBTENER_SESION() as sesion:
            insumo = sesion.query(MODELO_INSUMO).filter_by(ID=insumo_id).first()
            if not insumo:
                return jsonify({
                    'exito': False,
                    'error': 'Insumo no encontrado',
                }), 404
            
            insumo.NOMBRE = datos.get('NOMBRE', insumo.NOMBRE)
            insumo.DESCRIPCION = datos.get('DESCRIPCION', insumo.DESCRIPCION)
            insumo.PRECIO_UNITARIO = int(float(datos['PRECIO_UNITARIO']) * 100) if datos.get('PRECIO_UNITARIO') else insumo.PRECIO_UNITARIO
            insumo.STOCK_MINIMO = int(datos.get('STOCK_MINIMO', insumo.STOCK_MINIMO))
            insumo.PROVEEDOR = datos.get('PROVEEDOR', insumo.PROVEEDOR)
            
            sesion.commit()
            
            return jsonify({
                'exito': True,
                'data': {'ID': insumo.ID},
            }), 200
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': str(e),
        }), 500

@api_insumos.route('/insumos/<int:insumo_id>', methods=['DELETE'])
@REQUIERE_ROL_API(ROLES.ADMIN)
def eliminar_insumo(insumo_id):
    """Elimina un insumo (soft delete)"""
    try:
        with OBTENER_SESION() as sesion:
            insumo = sesion.query(MODELO_INSUMO).filter_by(ID=insumo_id).first()
            if not insumo:
                return jsonify({
                    'exito': False,
                    'error': 'Insumo no encontrado',
                }), 404
            
            insumo.ACTIVO = False
            sesion.commit()
            
            return jsonify({
                'exito': True,
            }), 200
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': str(e),
        }), 500

# ==================== MOVIMIENTOS ====================

@api_insumos.route('/movimientos', methods=['GET'])
@REQUIERE_ROL_API(ROLES.ADMIN)
def obtener_movimientos():
    """Obtiene movimientos de insumos (últimos 30 días)"""
    try:
        from datetime import timedelta
        hace_30_dias = datetime.utcnow() - timedelta(days=30)
        
        with OBTENER_SESION() as sesion:
            movimientos = sesion.query(MODELO_MOVIMIENTO_INSUMO).filter(
                MODELO_MOVIMIENTO_INSUMO.FECHA >= hace_30_dias
            ).all()
            
            datos = [
                {
                    'ID': m.ID,
                    'INSUMO_ID': m.INSUMO_ID,
                    'INSUMO_NOMBRE': m.INSUMO.NOMBRE if m.INSUMO else '?',
                    'TIPO': m.TIPO,
                    'CANTIDAD': m.CANTIDAD,
                    'STOCK_ANTERIOR': m.STOCK_ANTERIOR,
                    'STOCK_NUEVO': m.STOCK_NUEVO,
                    'OBSERVACION': m.OBSERVACION,
                    'FECHA': m.FECHA.isoformat() if m.FECHA else None,
                }
                for m in movimientos
            ]
            
            return jsonify({
                'exito': True,
                'data': datos,
                'total': len(datos),
            }), 200
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': str(e),
        }), 500

@api_insumos.route('/reporte/diario', methods=['GET'])
@REQUIERE_ROL_API(ROLES.ADMIN)
def reporte_diario():
    """Reporte de consumo de insumos del día"""
    try:
        from datetime import date
        hoy = date.today()
        
        with OBTENER_SESION() as sesion:
            movimientos = sesion.query(MODELO_MOVIMIENTO_INSUMO).filter(
                MODELO_MOVIMIENTO_INSUMO.FECHA >= datetime.combine(hoy, datetime.min.time()),
                MODELO_MOVIMIENTO_INSUMO.FECHA <= datetime.combine(hoy, datetime.max.time()),
            ).all()
            
            # Agrupar por tipo de movimiento
            por_tipo = {}
            for m in movimientos:
                if m.TIPO not in por_tipo:
                    por_tipo[m.TIPO] = []
                por_tipo[m.TIPO].append({
                    'INSUMO': m.INSUMO.NOMBRE if m.INSUMO else '?',
                    'CANTIDAD': m.CANTIDAD,
                    'OBSERVACION': m.OBSERVACION,
                })
            
            return jsonify({
                'exito': True,
                'fecha': hoy.isoformat(),
                'data': por_tipo,
                'total_movimientos': len(movimientos),
            }), 200
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'error': str(e),
        }), 500
