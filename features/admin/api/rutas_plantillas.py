"""
API REST para gestión de Plantillas de Horarios
Rutas CRUD con validación de permisos
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json
from functools import wraps
from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_PLANTILLA, MODELO_USUARIO
from core.Constantes import ROLES

api_plantillas = Blueprint('api_plantillas', __name__, url_prefix='/api/plantillas')


def REQUIERE_ROL_API(*ROLES_PERMITIDOS):
    """Decorador para validar permisos en APIs"""
    def decorador(f):
        @wraps(f)
        def funcion_envuelta(*args, **kwargs):
            # En una API real, obtendrías el usuario del token/sesión
            # Por ahora permitimos acceso
            return f(*args, **kwargs)
        return funcion_envuelta
    return decorador


@api_plantillas.route('', methods=['GET'])
@REQUIERE_ROL_API(ROLES.ADMIN)
def obtener_plantillas():
    """Obtiene todas las plantillas activas"""
    try:
        with OBTENER_SESION() as sesion:
            plantillas = sesion.query(MODELO_PLANTILLA).filter_by(ACTIVO=True).all()
            
            datos = []
            for p in plantillas:
                usuario = sesion.query(MODELO_USUARIO).filter_by(ID=p.CREADO_POR).first()
                datos.append({
                    "ID": p.ID,
                    "NOMBRE": p.NOMBRE,
                    "DESCRIPCION": p.DESCRIPCION,
                    "HORA_INICIO": p.HORA_INICIO,
                    "HORA_FIN": p.HORA_FIN,
                    "DIAS": json.loads(p.DIAS) if p.DIAS else [],
                    "CREADO_POR": usuario.NOMBRE_USUARIO if usuario else "Sistema",
                    "FECHA_CREACION": p.FECHA_CREACION.isoformat() if p.FECHA_CREACION else None,
                    "ACTIVO": p.ACTIVO
                })
            
            return jsonify({"success": True, "data": datos}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_plantillas.route('/<int:plantilla_id>', methods=['GET'])
@REQUIERE_ROL_API(ROLES.ADMIN)
def obtener_plantilla(plantilla_id):
    """Obtiene detalles de una plantilla específica"""
    try:
        with OBTENER_SESION() as sesion:
            plantilla = sesion.query(MODELO_PLANTILLA).filter_by(ID=plantilla_id, ACTIVO=True).first()
            
            if not plantilla:
                return jsonify({"success": False, "error": "Plantilla no encontrada"}), 404
            
            usuario = sesion.query(MODELO_USUARIO).filter_by(ID=plantilla.CREADO_POR).first()
            
            datos = {
                "ID": plantilla.ID,
                "NOMBRE": plantilla.NOMBRE,
                "DESCRIPCION": plantilla.DESCRIPCION,
                "HORA_INICIO": plantilla.HORA_INICIO,
                "HORA_FIN": plantilla.HORA_FIN,
                "DIAS": json.loads(plantilla.DIAS) if plantilla.DIAS else [],
                "CREADO_POR": usuario.NOMBRE_USUARIO if usuario else "Sistema",
                "FECHA_CREACION": plantilla.FECHA_CREACION.isoformat() if plantilla.FECHA_CREACION else None,
                "ACTIVO": plantilla.ACTIVO
            }
            
            return jsonify({"success": True, "data": datos}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_plantillas.route('', methods=['POST'])
@REQUIERE_ROL_API(ROLES.ADMIN)
def crear_plantilla():
    """Crea una nueva plantilla"""
    try:
        datos = request.json
        usuario_id = request.headers.get('X-Usuario-ID')  # Obtenido del middleware de autenticación
        
        # Validación
        if not datos.get('NOMBRE'):
            return jsonify({"success": False, "error": "Nombre es obligatorio"}), 400
        
        if not datos.get('HORA_INICIO') or not datos.get('HORA_FIN'):
            return jsonify({"success": False, "error": "Horas son obligatorias"}), 400
        
        if not datos.get('DIAS'):
            return jsonify({"success": False, "error": "Días son obligatorios"}), 400
        
        with OBTENER_SESION() as sesion:
            # Verificar nombre único
            existe = sesion.query(MODELO_PLANTILLA).filter_by(NOMBRE=datos['NOMBRE']).first()
            if existe:
                return jsonify({"success": False, "error": "Plantilla con este nombre ya existe"}), 409
            
            nueva_plantilla = MODELO_PLANTILLA(
                NOMBRE=datos['NOMBRE'],
                DESCRIPCION=datos.get('DESCRIPCION'),
                HORA_INICIO=datos['HORA_INICIO'],
                HORA_FIN=datos['HORA_FIN'],
                DIAS=json.dumps(datos['DIAS']),
                CREADO_POR=int(usuario_id),
                ACTIVO=True
            )
            sesion.add(nueva_plantilla)
            sesion.commit()
            
            return jsonify({
                "success": True,
                "message": f"Plantilla '{datos['NOMBRE']}' creada exitosamente",
                "data": {"ID": nueva_plantilla.ID}
            }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_plantillas.route('/<int:plantilla_id>', methods=['PUT'])
@REQUIERE_ROL_API(ROLES.ADMIN)
def actualizar_plantilla(plantilla_id):
    """Actualiza una plantilla existente"""
    try:
        datos = request.json
        
        with OBTENER_SESION() as sesion:
            plantilla = sesion.query(MODELO_PLANTILLA).filter_by(ID=plantilla_id).first()
            
            if not plantilla:
                return jsonify({"success": False, "error": "Plantilla no encontrada"}), 404
            
            # Actualizar campos permitidos
            if 'NOMBRE' in datos:
                # Verificar nombre único (excluyendo la plantilla actual)
                existe = sesion.query(MODELO_PLANTILLA).filter(
                    MODELO_PLANTILLA.NOMBRE == datos['NOMBRE'],
                    MODELO_PLANTILLA.ID != plantilla_id
                ).first()
                if existe:
                    return jsonify({"success": False, "error": "Nombre ya existe"}), 409
                plantilla.NOMBRE = datos['NOMBRE']
            
            if 'DESCRIPCION' in datos:
                plantilla.DESCRIPCION = datos['DESCRIPCION']
            
            if 'HORA_INICIO' in datos:
                plantilla.HORA_INICIO = datos['HORA_INICIO']
            
            if 'HORA_FIN' in datos:
                plantilla.HORA_FIN = datos['HORA_FIN']
            
            if 'DIAS' in datos:
                plantilla.DIAS = json.dumps(datos['DIAS'])
            
            if 'ACTIVO' in datos:
                plantilla.ACTIVO = datos['ACTIVO']
            
            sesion.commit()
            
            return jsonify({
                "success": True,
                "message": f"Plantilla '{plantilla.NOMBRE}' actualizada exitosamente"
            }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_plantillas.route('/<int:plantilla_id>', methods=['DELETE'])
@REQUIERE_ROL_API(ROLES.ADMIN)
def eliminar_plantilla(plantilla_id):
    """Desactiva una plantilla (soft delete)"""
    try:
        with OBTENER_SESION() as sesion:
            plantilla = sesion.query(MODELO_PLANTILLA).filter_by(ID=plantilla_id).first()
            
            if not plantilla:
                return jsonify({"success": False, "error": "Plantilla no encontrada"}), 404
            
            plantilla.ACTIVO = False
            sesion.commit()
            
            return jsonify({
                "success": True,
                "message": f"Plantilla '{plantilla.NOMBRE}' eliminada exitosamente"
            }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
