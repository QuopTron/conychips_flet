"""Script simple para verificar vouchers en BD"""
import sys
import os

# Deshabilitar imports de Flet
os.environ['SKIP_FLET_IMPORTS'] = '1'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Conectar directamente a PostgreSQL
engine = create_engine('postgresql://postgres:postgres@localhost:5432/conychips')
Session = sessionmaker(bind=engine)
session = Session()

# Consulta directa
result = session.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN estado = 'PENDIENTE' THEN 1 ELSE 0 END) as pendientes,
        SUM(CASE WHEN estado = 'APROBADO' THEN 1 ELSE 0 END) as aprobados,
        SUM(CASE WHEN estado = 'RECHAZADO' THEN 1 ELSE 0 END) as rechazados
    FROM vouchers
""").fetchone()

print('📊 VOUCHERS EN BASE DE DATOS:')
print(f'  • Total: {result[0]}')
print(f'  • Pendientes: {result[1]}')
print(f'  • Aprobados: {result[2]}')
print(f'  • Rechazados: {result[3]}')
print()

if result[0] == 0:
    print('⚠️  NO HAY VOUCHERS')
    print('   Para crear datos de prueba ejecuta: python crear_datos_prueba.py')
else:
    # Mostrar algunos ejemplos
    ejemplos = session.execute("""
        SELECT id, estado, monto, pedido_id
        FROM vouchers
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()
    
    print('📄 Últimos 5 vouchers:')
    for v in ejemplos:
        print(f'   • ID {v[0]}: {v[1]} - S/ {v[2]:.2f} - Pedido #{v[3]}')

session.close()
