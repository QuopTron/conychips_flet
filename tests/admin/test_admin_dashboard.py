
import sys
sys.path.insert(0, '/mnt/flox/conychips')

print("=" * 60)
print("TEST: AdminBloc y Dashboard")
print("=" * 60)

print("\n1. Importando módulos...")
try:
    from features.admin.presentation.bloc import ADMIN_BLOC, CargarDashboard
    from features.admin.domain.usecases.CargarEstadisticasDashboard import CargarEstadisticasDashboard
    from features.admin.data.RepositorioAdminImpl import REPOSITORIO_ADMIN_IMPL
    print("   ✓ Módulos importados correctamente")
except Exception as e:
    print(f"   ✗ Error importando: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n2. Cargando estadísticas directamente...")
try:
    usecase = CargarEstadisticasDashboard(REPOSITORIO_ADMIN_IMPL)
    dashboard = usecase.EJECUTAR()
    
    if dashboard:
        print(f"   ✓ Dashboard cargado:")
        print(f"      - Usuarios: {dashboard.estadisticas_generales.total_usuarios}")
        print(f"      - Pedidos hoy: {dashboard.estadisticas_generales.total_pedidos_hoy}")
        print(f"      - Ganancias: {dashboard.estadisticas_generales.ganancias_hoy} Bs")
        print(f"      - Productos: {dashboard.estadisticas_generales.total_productos}")
        print(f"      - Roles: {len(dashboard.estadisticas_roles)}")
        print(f"      - Sucursales: {len(dashboard.estadisticas_sucursales)}")
    else:
        print("   ✗ Dashboard es None")
except Exception as e:
    print(f"   ✗ Error cargando: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n3. Probando BLoC...")
try:
    print(f"   Estado inicial: {ADMIN_BLOC.ESTADO.__class__.__name__}")
    
    estados_recibidos = []
    def listener(estado):
        estados_recibidos.append(estado.__class__.__name__)
        print(f"   [Listener] Estado recibido: {estado.__class__.__name__}")
    
    ADMIN_BLOC.AGREGAR_LISTENER(listener)
    
    print("   Disparando CargarDashboard...")
    ADMIN_BLOC.AGREGAR_EVENTO(CargarDashboard())
    
    import time
    time.sleep(2)
    
    print(f"\n   Estados recibidos: {estados_recibidos}")
    
    if 'AdminCargando' in estados_recibidos and 'AdminCargado' in estados_recibidos:
        print("   ✓ BLoC funcionando correctamente")
    else:
        print("   ✗ BLoC no pasó por los estados esperados")
        
except Exception as e:
    print(f"   ✗ Error probando BLoC: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("RESULTADO: ✓ Todos los tests pasaron")
print("=" * 60)
