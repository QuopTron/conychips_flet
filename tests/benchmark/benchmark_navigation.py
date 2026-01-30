"""
Benchmark - Sistema de Navegación
Mide performance de componentes de navegación
"""
import time
import flet as ft
from features.admin.presentation.widgets.LayoutBase import LayoutBase
from features.admin.presentation.widgets.NavbarGlobal import NavbarGlobal
from features.admin.presentation.widgets.BottomNavigation import BottomNavigation
from features.autenticacion.domain.entities.Usuario import Usuario


class NavigationBenchmark:
    """Benchmarks de navegación"""
    
    def __init__(self):
        self.results = {}
    
    def benchmark_layout_base_creation(self, iterations=100):
        """Benchmark: Creación de LayoutBase"""
        page = ft.Page()
        usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test", ROLES=["ADMIN"])
        
        start = time.perf_counter()
        for _ in range(iterations):
            layout = LayoutBase(pagina=page, usuario=usuario)
        end = time.perf_counter()
        
        avg_time = (end - start) / iterations * 1000  # ms
        self.results['LayoutBase Creation'] = {
            'avg_ms': avg_time,
            'iterations': iterations,
            'total_ms': (end - start) * 1000
        }
        return avg_time
    
    def benchmark_construir_method(self, iterations=100):
        """Benchmark: Método construir()"""
        page = ft.Page()
        usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test", ROLES=["ADMIN"])
        
        contenido = ft.Container(
            content=ft.Column([
                ft.Text("Test"),
                ft.DataTable(columns=[])
            ])
        )
        
        start = time.perf_counter()
        for _ in range(iterations):
            layout = LayoutBase(pagina=page, usuario=usuario)
            layout.construir(contenido)
        end = time.perf_counter()
        
        avg_time = (end - start) / iterations * 1000
        self.results['construir() Method'] = {
            'avg_ms': avg_time,
            'iterations': iterations,
            'total_ms': (end - start) * 1000
        }
        return avg_time
    
    def benchmark_navbar_global_creation(self, iterations=100):
        """Benchmark: Creación de NavbarGlobal"""
        page = ft.Page()
        usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test", ROLES=["ADMIN"])
        
        start = time.perf_counter()
        for _ in range(iterations):
            navbar = NavbarGlobal(
                pagina=page,
                usuario=usuario,
                on_cambio_sucursales=None,
                on_cerrar_sesion=None
            )
        end = time.perf_counter()
        
        avg_time = (end - start) / iterations * 1000
        self.results['NavbarGlobal Creation'] = {
            'avg_ms': avg_time,
            'iterations': iterations,
            'total_ms': (end - start) * 1000
        }
        return avg_time
    
    def benchmark_bottom_navigation_creation(self, iterations=100):
        """Benchmark: Creación de BottomNavigation"""
        page = ft.Page()
        usuario = Usuario(ID=1, EMAIL="test@test.com", NOMBRE_USUARIO="test", ROLES=["SUPERADMIN"])
        
        start = time.perf_counter()
        for _ in range(iterations):
            bottom_nav = BottomNavigation(
                pagina=page,
                usuario=usuario,
                on_navigate=lambda x: None,
                selected_index=0
            )
        end = time.perf_counter()
        
        avg_time = (end - start) / iterations * 1000
        self.results['BottomNavigation Creation'] = {
            'avg_ms': avg_time,
            'iterations': iterations,
            'total_ms': (end - start) * 1000
        }
        return avg_time
    
    def run_all_benchmarks(self, iterations=100):
        """Ejecuta todos los benchmarks"""
        print(f"\n{'='*60}")
        print(f"🔥 BENCHMARK - Sistema de Navegación")
        print(f"{'='*60}\n")
        print(f"Iteraciones por test: {iterations}\n")
        
        # Layout Base
        time1 = self.benchmark_layout_base_creation(iterations)
        print(f"✓ LayoutBase Creation:        {time1:.4f} ms/op")
        
        # Construir
        time2 = self.benchmark_construir_method(iterations)
        print(f"✓ construir() Method:          {time2:.4f} ms/op")
        
        # NavbarGlobal
        time3 = self.benchmark_navbar_global_creation(iterations)
        print(f"✓ NavbarGlobal Creation:       {time3:.4f} ms/op")
        
        # BottomNavigation
        time4 = self.benchmark_bottom_navigation_creation(iterations)
        print(f"✓ BottomNavigation Creation:   {time4:.4f} ms/op")
        
        print(f"\n{'='*60}")
        print(f"Total tiempo: {sum([r['total_ms'] for r in self.results.values()]):.2f} ms")
        print(f"{'='*60}\n")
        
        return self.results
    
    def compare_versions(self, baseline_results, current_results):
        """Compara resultados entre versiones"""
        print(f"\n{'='*60}")
        print(f"📊 COMPARACIÓN DE VERSIONES")
        print(f"{'='*60}\n")
        
        for key in baseline_results.keys():
            if key in current_results:
                baseline = baseline_results[key]['avg_ms']
                current = current_results[key]['avg_ms']
                diff = ((current - baseline) / baseline) * 100
                
                symbol = "⬆️" if diff > 0 else "⬇️"
                color = "SLOWER" if diff > 0 else "FASTER"
                
                print(f"{key:30} {baseline:.4f} ms → {current:.4f} ms ({symbol} {abs(diff):.2f}% {color})")
        
        print(f"\n{'='*60}\n")


def run_benchmark():
    """Ejecuta benchmark completo"""
    bench = NavigationBenchmark()
    results = bench.run_all_benchmarks(iterations=50)
    return results


if __name__ == "__main__":
    run_benchmark()
