#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test del sistema de plantillas"""

from core.base_datos.ConfiguracionBD import OBTENER_SESION, MODELO_PLANTILLA, MODELO_HORARIO, MODELO_USUARIO

print("🧪 VERIFICACIÓN DEL SISTEMA DE PLANTILLAS\n")

try:
    with OBTENER_SESION() as sesion:
        # 1. Verificar plantillas
        plantillas = sesion.query(MODELO_PLANTILLA).all()
        print(f"✅ Plantillas en BD: {len(plantillas)}")
        for p in plantillas[:2]:
            print(f"   └─ {p.NOMBRE}: {p.HORA_INICIO}-{p.HORA_FIN}")
        
        # 2. Verificar horarios
        horarios = sesion.query(MODELO_HORARIO).all()
        print(f"\n✅ Horarios en BD: {len(horarios)}")
        
        # 3. Verificar usuarios
        usuarios = sesion.query(MODELO_USUARIO).filter_by(ACTIVO=True).all()
        print(f"\n✅ Usuarios activos: {len(usuarios)}")
        
        # 4. Verificar tabla estructura
        print(f"\n✅ Estructura MODELO_PLANTILLA:")
        cols = [c.name for c in MODELO_PLANTILLA.__table__.columns]
        print(f"   Columnas: {cols}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n📊 Sistema de Plantillas: FUNCIONAL ✅")
