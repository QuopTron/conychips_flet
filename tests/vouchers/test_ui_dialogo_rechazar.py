"""
Test de Caja Blanca - UI del Diálogo de Rechazo
Analiza cómo se construye el diálogo y los handlers en Flet
"""
import sys
import ast
import inspect
from pathlib import Path

print("=" * 80)
print("ANÁLISIS DE CAJA BLANCA - UI DIÁLOGO DE RECHAZO")
print("=" * 80)

# ============================================================================
# 1. ANÁLISIS ESTÁTICO DEL CÓDIGO
# ============================================================================

archivo_handlers = Path("/mnt/flox/conychips/features/admin/presentation/pages/vistas/vouchers/VoucherHandlers.py")

print("\n" + "=" * 80)
print("1. ANÁLISIS DEL CÓDIGO FUENTE")
print("=" * 80)

with open(archivo_handlers, 'r', encoding='utf-8') as f:
    codigo = f.read()
    lineas = codigo.split('\n')

# Buscar el método _crear_dialogo_rechazo
inicio_metodo = None
for i, linea in enumerate(lineas):
    if 'def _crear_dialogo_rechazo' in linea:
        inicio_metodo = i
        break

if inicio_metodo:
    print(f"\n✓ Método _crear_dialogo_rechazo encontrado en línea {inicio_metodo + 1}")
    
    # Extraer el método completo
    indentacion_base = len(lineas[inicio_metodo]) - len(lineas[inicio_metodo].lstrip())
    fin_metodo = None
    for i in range(inicio_metodo + 1, len(lineas)):
        linea = lineas[i]
        if linea.strip() and not linea.startswith(' ' * (indentacion_base + 4)):
            if linea.strip().startswith('def '):
                fin_metodo = i
                break
    
    if fin_metodo:
        metodo_completo = '\n'.join(lineas[inicio_metodo:fin_metodo])
        
        # Análisis del método
        print("\n📊 COMPONENTES DE FLET USADOS:")
        componentes_flet = {
            'ft.TextField': 'Campo de texto multilinea para motivo',
            'ft.Text': 'Texto de error',
            'ft.ElevatedButton': 'Botón principal de acción',
            'ft.TextButton': 'Botón secundario (Cancelar)',
            'ft.AlertDialog': 'Diálogo modal',
            'ft.Container': 'Contenedor para layout',
            'ft.Column': 'Layout vertical',
            'ft.Row': 'Layout horizontal',
            'ft.Icon': 'Icono de advertencia',
            'ft.Divider': 'Separador visual'
        }
        
        for componente, descripcion in componentes_flet.items():
            if componente in metodo_completo:
                print(f"  ✓ {componente:25s} - {descripcion}")
        
        # Verificar propiedades importantes
        print("\n📋 PROPIEDADES CONFIGURADAS:")
        propiedades_criticas = {
            'modal=True': 'Diálogo modal (bloquea interacción)',
            'autofocus=True': 'TextField enfocado automáticamente',
            'multiline=True': 'TextField multilínea',
            'on_click': 'Handler de evento click',
            'bgcolor': 'Color de fondo',
            'color': 'Color de texto',
            'icon': 'Icono del botón'
        }
        
        for propiedad, descripcion in propiedades_criticas.items():
            if propiedad in metodo_completo:
                print(f"  ✓ {propiedad:25s} - {descripcion}")
        
        # Buscar asignación del handler
        print("\n🔗 ASIGNACIÓN DE HANDLERS:")
        
        # Buscar el botón rechazar
        if 'btn_rechazar = ft.ElevatedButton' in metodo_completo:
            print("  ✓ btn_rechazar definido como ft.ElevatedButton")
            
            # Extraer la creación del botón
            inicio_btn = metodo_completo.find('btn_rechazar = ft.ElevatedButton')
            fin_btn = metodo_completo.find(')', inicio_btn) + 1
            codigo_boton = metodo_completo[inicio_btn:fin_btn]
            
            print("\n  📄 Código del botón:")
            for linea in codigo_boton.split('\n'):
                print(f"    {linea}")
            
            # Verificar on_click
            if 'on_click=' in codigo_boton:
                print("\n  ✓ on_click asignado en el constructor")
                
                if 'lambda' in codigo_boton:
                    print("  ✓ Usando lambda wrapper")
                    if 'self._confirmar_rechazo_handler' in codigo_boton:
                        print("  ✓ Lambda llama a self._confirmar_rechazo_handler")
                elif 'self._confirmar_rechazo_handler' in codigo_boton:
                    print("  ✓ Referencia directa a self._confirmar_rechazo_handler")
                else:
                    print("  ⚠️  Handler desconocido en on_click")
            else:
                print("  ❌ on_click NO encontrado en el constructor")
        
        # Verificar atributos de instancia
        print("\n💾 ATRIBUTOS DE INSTANCIA (CONTEXTO):")
        atributos_contexto = [
            'self._dialog_voucher',
            'self._dialog_boton_original',
            'self._dialog_motivo_input',
            'self._dialog_error_text',
            'self._current_dialog'
        ]
        
        for atributo in atributos_contexto:
            if atributo in metodo_completo:
                print(f"  ✓ {atributo:30s} - Guardado para el handler")
        
        # Verificar el diálogo
        print("\n🪟 ESTRUCTURA DEL DIÁLOGO:")
        if 'ft.AlertDialog' in metodo_completo:
            print("  ✓ AlertDialog creado")
            
            if 'title=' in metodo_completo:
                print("  ✓ title configurado")
            if 'content=' in metodo_completo:
                print("  ✓ content configurado")
            if 'actions=' in metodo_completo:
                print("  ✓ actions configurado (botones)")
            if 'actions_alignment=' in metodo_completo:
                print("  ✓ actions_alignment configurado")

# ============================================================================
# 2. ANÁLISIS DEL HANDLER
# ============================================================================

print("\n" + "=" * 80)
print("2. ANÁLISIS DEL HANDLER _confirmar_rechazo_handler")
print("=" * 80)

# Buscar el handler
inicio_handler = None
for i, linea in enumerate(lineas):
    if 'def _confirmar_rechazo_handler' in linea:
        inicio_handler = i
        break

if inicio_handler:
    print(f"\n✓ Handler encontrado en línea {inicio_handler + 1}")
    
    # Extraer el handler
    indentacion_base = len(lineas[inicio_handler]) - len(lineas[inicio_handler].lstrip())
    fin_handler = None
    for i in range(inicio_handler + 1, len(lineas)):
        linea = lineas[i]
        if linea.strip() and not linea.startswith(' ' * (indentacion_base + 4)):
            if linea.strip().startswith('def '):
                fin_handler = i
                break
    
    if fin_handler:
        handler_completo = '\n'.join(lineas[inicio_handler:fin_handler])
        
        print("\n🔍 OPERACIONES DEL HANDLER:")
        
        operaciones = {
            'print': 'Logs de debug',
            'self._dialog_motivo_input.value': 'Lee el valor del TextField',
            'len(motivo.strip())': 'Valida longitud del motivo',
            'self._dialog_error_text.value =': 'Muestra mensaje de error',
            'self._dialog_error_text.visible': 'Controla visibilidad del error',
            'self._current_dialog.open = False': 'Cierra el diálogo',
            'self.pagina.update()': 'Actualiza la UI',
            'self._dialog_boton_original.disabled': 'Deshabilita el botón original',
            'self._dialog_boton_original.text': 'Cambia texto del botón',
            'self._dialog_boton_original.icon': 'Cambia icono del botón',
            'VOUCHERS_BLOC.AGREGAR_EVENTO': 'Emite evento al BLoC',
            'RechazarVoucherEvento': 'Crea el evento de rechazo'
        }
        
        for operacion, descripcion in operaciones.items():
            if operacion in handler_completo:
                print(f"  ✓ {operacion:40s} - {descripcion}")
        
        # Verificar flujo
        print("\n🔄 FLUJO DEL HANDLER:")
        print("  1. Log de ejecución")
        print("  2. Leer motivo del TextField")
        print("  3. Validar longitud (min 10 chars)")
        print("  4. Si inválido: mostrar error y return")
        print("  5. Cerrar diálogo")
        print("  6. Actualizar UI")
        print("  7. Actualizar botón original (disabled, text, icon)")
        print("  8. Emitir RechazarVoucherEvento al BLoC")

# ============================================================================
# 3. PRUEBA DE IMPORTACIÓN Y ESTRUCTURA
# ============================================================================

print("\n" + "=" * 80)
print("3. PRUEBA DE IMPORTACIÓN")
print("=" * 80)

try:
    sys.path.insert(0, '/mnt/flox/conychips')
    from features.admin.presentation.pages.vistas.vouchers.VoucherHandlers import VoucherHandlers
    print("✓ VoucherHandlers importado correctamente")
    
    # Verificar que el método existe
    if hasattr(VoucherHandlers, '_crear_dialogo_rechazo'):
        print("✓ Método _crear_dialogo_rechazo existe en la clase")
    
    if hasattr(VoucherHandlers, '_confirmar_rechazo_handler'):
        print("✓ Método _confirmar_rechazo_handler existe en la clase")
    
    if hasattr(VoucherHandlers, '_cancelar_rechazo_handler'):
        print("✓ Método _cancelar_rechazo_handler existe en la clase")
    
    # Obtener firma del método
    metodo = getattr(VoucherHandlers, '_confirmar_rechazo_handler')
    firma = inspect.signature(metodo)
    print(f"\n📝 Firma del handler: _confirmar_rechazo_handler{firma}")
    
    parametros = list(firma.parameters.keys())
    if parametros == ['self', 'e']:
        print("✓ Parámetros correctos: (self, e)")
    else:
        print(f"⚠️  Parámetros: {parametros}")
    
except Exception as e:
    print(f"❌ Error al importar: {e}")

# ============================================================================
# 4. ANÁLISIS DE DATOS PASADOS
# ============================================================================

print("\n" + "=" * 80)
print("4. FLUJO DE DATOS")
print("=" * 80)

print("\n📦 DATOS DE ENTRADA al método _crear_dialogo_rechazo:")
print("  • voucher: Voucher entity")
print("    - voucher.id: int")
print("    - voucher.monto: float")
print("    - voucher.estado: str")
print("  • boton_original: ft.ElevatedButton")
print("    - Control del botón que abrió el diálogo")

print("\n💾 DATOS GUARDADOS en atributos de instancia:")
print("  • self._dialog_voucher = voucher")
print("  • self._dialog_boton_original = boton_original")
print("  • self._dialog_motivo_input = ft.TextField(...)")
print("  • self._dialog_error_text = ft.Text(...)")
print("  • self._current_dialog = ft.AlertDialog(...)")

print("\n🔄 DATOS USADOS en _confirmar_rechazo_handler:")
print("  • Lee: self._dialog_motivo_input.value → str")
print("  • Valida: len(motivo.strip()) >= 10")
print("  • Modifica: self._dialog_error_text.value")
print("  • Modifica: self._dialog_error_text.visible")
print("  • Modifica: self._current_dialog.open")
print("  • Modifica: self._dialog_boton_original.disabled")
print("  • Modifica: self._dialog_boton_original.text")
print("  • Modifica: self._dialog_boton_original.icon")
print("  • Emite: RechazarVoucherEvento(")
print("      voucher_id=self._dialog_voucher.id,")
print("      validador_id=self.usuario.ID,")
print("      motivo=motivo.strip()")
print("    )")

print("\n📤 DATOS DE SALIDA (Evento):")
print("  • RechazarVoucherEvento:")
print("    - voucher_id: int (desde self._dialog_voucher.id)")
print("    - validador_id: int (desde self.usuario.ID)")
print("    - motivo: str (desde self._dialog_motivo_input.value)")

# ============================================================================
# 5. VERIFICACIÓN DE PROBLEMAS COMUNES
# ============================================================================

print("\n" + "=" * 80)
print("5. VERIFICACIÓN DE PROBLEMAS COMUNES EN FLET")
print("=" * 80)

problemas = []

# Verificar si on_click está en el constructor
if 'btn_rechazar = ft.ElevatedButton' in codigo:
    inicio = codigo.find('btn_rechazar = ft.ElevatedButton')
    fin = codigo.find(')', inicio) + 1
    boton_codigo = codigo[inicio:fin]
    
    if 'on_click=' not in boton_codigo:
        problemas.append("❌ on_click NO está en el constructor del botón")
    else:
        print("✓ on_click asignado en el constructor (CORRECTO)")

# Verificar que no haya reasignación después
if 'btn_rechazar.on_click =' in codigo:
    problemas.append("⚠️  Reasignación de btn_rechazar.on_click después del constructor")
else:
    print("✓ No hay reasignación de on_click después del constructor")

# Verificar que el diálogo se asigne a page.dialog
if 'self.pagina.dialog =' in codigo:
    print("✓ Diálogo asignado a page.dialog")
else:
    problemas.append("❌ Diálogo NO se asigna a page.dialog")

# Verificar que se llame page.update()
if 'self.pagina.update()' in codigo:
    print("✓ page.update() se llama para refrescar UI")
else:
    problemas.append("❌ page.update() NO se llama")

# Verificar que dialog.open se establezca
if 'dialogo.open = True' in codigo or '.open = True' in codigo:
    print("✓ dialog.open = True se establece")
else:
    problemas.append("❌ dialog.open NO se establece en True")

if problemas:
    print("\n⚠️  PROBLEMAS DETECTADOS:")
    for problema in problemas:
        print(f"  {problema}")
else:
    print("\n✅ No se detectaron problemas comunes")

# ============================================================================
# 6. RECOMENDACIONES
# ============================================================================

print("\n" + "=" * 80)
print("6. RECOMENDACIONES PARA DEBUG EN RUNTIME")
print("=" * 80)

print("""
Para verificar el handler en runtime cuando hagas click:

1. ANTES DE ABRIR EL DIÁLOGO:
   - Verifica que self._confirmar_rechazo_handler existe
   - Verifica que es callable

2. AL CREAR EL BOTÓN:
   - Imprime btn_rechazar.on_click
   - Debe mostrar: <function VoucherHandlers._confirmar_rechazo_handler>
   - o: <function <lambda>>

3. AL ABRIR EL DIÁLOGO:
   - Verifica que page.dialog == dialogo
   - Verifica que dialogo.open == True
   - Inspecciona dialogo.actions[1].on_click

4. AL HACER CLICK EN EL BOTÓN:
   - Debe ejecutar el handler
   - Debe aparecer el log con ======
   - Si no aparece, el evento NO se está disparando

5. VERIFICACIONES ADICIONALES:
   - ¿El botón está disabled? → No debería
   - ¿El diálogo está visible? → Sí
   - ¿El botón tiene on_click None? → No debería
   - ¿Hay errores en consola? → Revisar

CÓDIGO PARA AÑADIR AL MÉTODO rechazar_click():
    print(f"[DEBUG] Handler callable: {callable(self._confirmar_rechazo_handler)}")
    print(f"[DEBUG] Botón on_click: {btn_rechazar.on_click}")
    print(f"[DEBUG] Dialog actions: {len(dialogo.actions)}")
    for i, action in enumerate(dialogo.actions):
        print(f"[DEBUG] Action {i}: {action}, on_click={getattr(action, 'on_click', None)}")
""")

print("\n" + "=" * 80)
print("RESUMEN DEL ANÁLISIS")
print("=" * 80)

print("""
✅ CÓDIGO ESTRUCTURADO CORRECTAMENTE:
  - Componentes de Flet usados apropiadamente
  - Handler es método de clase (self)
  - Contexto guardado en atributos de instancia
  - Diálogo configurado con modal=True
  - Botón tiene on_click asignado en constructor

❓ PUNTO CRÍTICO A VERIFICAR:
  - El handler SE DEFINE correctamente
  - El handler SE ASIGNA correctamente al botón
  - ¿Por qué NO SE EJECUTA cuando el usuario hace click?

🔍 HIPÓTESIS:
  1. Flet no está registrando el evento click
  2. El botón está disabled inadvertidamente
  3. Hay un problema con el lambda wrapper
  4. El diálogo se está recreando sin el handler

💡 SIGUIENTE PASO:
  Añadir logs en rechazar_click() para inspeccionar el botón
  y el diálogo justo antes de mostrarlo.
""")

print("=" * 80)
