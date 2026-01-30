"""
Test de Caja Blanca - Componentes del flujo de rechazo
Prueba unitaria de cada función/método involucrado
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import flet as ft


class TestVoucherHandlersRechazar:
    """Tests unitarios de VoucherHandlers.rechazar_click()"""
    
    def test_rechazar_click_crea_dialogo(self):
        """rechazar_click debe crear y abrir diálogo"""
        from features.admin.presentation.pages.vistas.vouchers.VoucherHandlers import VoucherHandlers
        from features.vouchers.domain.entities.Voucher import Voucher
        
        # Setup
        pagina = Mock()
        usuario = Mock()
        usuario.ID = 1
        
        handlers = VoucherHandlers(pagina, usuario)
        
        # Mock evento
        e = Mock()
        voucher = Mock(spec=Voucher)
        voucher.id = 50
        voucher.monto = 100.0
        e.control.data = voucher
        
        # Ejecutar
        handlers.rechazar_click(e)
        
        # Verificar
        assert pagina.dialog is not None, "Dialog debe ser asignado"
        assert getattr(pagina.dialog, 'open', False), "Dialog debe estar abierto"
        assert pagina.update.called, "page.update() debe ser llamado"
    
    def test_crear_dialogo_rechazo_estructura(self):
        """_crear_dialogo_rechazo debe retornar AlertDialog válido"""
        from features.admin.presentation.pages.vistas.vouchers.VoucherHandlers import VoucherHandlers
        from features.vouchers.domain.entities.Voucher import Voucher
        
        pagina = Mock()
        usuario = Mock()
        usuario.ID = 1
        
        handlers = VoucherHandlers(pagina, usuario)
        
        voucher = Mock(spec=Voucher)
        voucher.id = 50
        voucher.monto = 100.0
        boton_original = Mock()
        
        dialogo = handlers._crear_dialogo_rechazo(voucher, boton_original)
        
        assert isinstance(dialogo, ft.AlertDialog)
        assert dialogo.modal == True
        assert dialogo.title is not None
        assert dialogo.content is not None
        assert dialogo.actions is not None
        assert len(dialogo.actions) == 2  # Cancelar + Rechazar
    
    def test_confirmar_rechazo_handler_asignado(self):
        """Botón Rechazar en diálogo debe tener on_click asignado"""
        from features.admin.presentation.pages.vistas.vouchers.VoucherHandlers import VoucherHandlers
        from features.vouchers.domain.entities.Voucher import Voucher
        
        pagina = Mock()
        usuario = Mock()
        usuario.ID = 1
        
        handlers = VoucherHandlers(pagina, usuario)
        
        voucher = Mock(spec=Voucher)
        voucher.id = 50
        voucher.monto = 100.0
        boton_original = Mock()
        
        dialogo = handlers._crear_dialogo_rechazo(voucher, boton_original)
        
        # El segundo botón en actions debe ser "Rechazar"
        btn_rechazar = dialogo.actions[1]
        
        assert btn_rechazar is not None
        assert btn_rechazar.on_click is not None, "CRITICAL: on_click NO está asignado!"
        assert callable(btn_rechazar.on_click), "on_click debe ser callable"
    
    def test_confirmar_rechazo_valida_motivo(self):
        """confirmar_rechazo debe validar motivo mínimo 10 caracteres"""
        from features.admin.presentation.pages.vistas.vouchers.VoucherHandlers import VoucherHandlers
        from features.vouchers.domain.entities.Voucher import Voucher
        
        pagina = Mock()
        usuario = Mock()
        usuario.ID = 1
        
        handlers = VoucherHandlers(pagina, usuario)
        
        voucher = Mock(spec=Voucher)
        voucher.id = 50
        voucher.monto = 100.0
        boton_original = Mock()
        
        dialogo = handlers._crear_dialogo_rechazo(voucher, boton_original)
        
        # Obtener TextField del diálogo
        # NOTA: Necesitamos acceder al TextField para simular input
        
        # TODO: Simular input de motivo corto y verificar que no emite evento
        pass
    
    @patch('features.vouchers.presentation.bloc.VOUCHERS_BLOC')
    def test_confirmar_rechazo_emite_evento(self, mock_bloc):
        """confirmar_rechazo debe emitir RechazarVoucherEvento"""
        from features.admin.presentation.pages.vistas.vouchers.VoucherHandlers import VoucherHandlers
        from features.vouchers.domain.entities.Voucher import Voucher
        
        pagina = Mock()
        usuario = Mock()
        usuario.ID = 1
        
        handlers = VoucherHandlers(pagina, usuario)
        
        voucher = Mock(spec=Voucher)
        voucher.id = 50
        voucher.monto = 100.0
        boton_original = Mock()
        
        dialogo = handlers._crear_dialogo_rechazo(voucher, boton_original)
        
        # TODO: Simular click en botón Rechazar con motivo válido
        # Verificar que VOUCHERS_BLOC.AGREGAR_EVENTO fue llamado
        pass


class TestVoucherCardBuilderBotonesRechazar:
    """Tests de botones de rechazo en las tarjetas"""
    
    def test_boton_rechazar_pendiente_tiene_handler(self):
        """Voucher PENDIENTE: botón Rechazar tiene on_click"""
        from features.admin.presentation.pages.vistas.vouchers.VoucherCardBuilder import VoucherCardBuilder
        from features.vouchers.domain.entities.Voucher import Voucher
        
        voucher = Mock(spec=Voucher)
        voucher.id = 50
        voucher.estado = "PENDIENTE"
        voucher.monto = 100.0
        voucher.metodo_pago = "Pago Movil"
        voucher.fecha_subida = Mock()
        voucher.usuario_id = 5
        voucher.fecha_validacion = None
        voucher.motivo_rechazo = None
        voucher.imagen_url = None
        voucher.es_pendiente = Mock(return_value=True)
        
        on_rechazar = Mock()
        on_aprobar = Mock()
        on_ver = Mock()
        
        card = VoucherCardBuilder.crear_card(
            voucher=voucher,
            estado_actual="PENDIENTE",
            on_aprobar_click=on_aprobar,
            on_rechazar_click=on_rechazar,
            on_ver_comprobante_click=on_ver
        )
        
        # TODO: Buscar botón "Rechazar" en la card y verificar on_click
        # CRITICAL: on_click debe ser on_rechazar
        pass
    
    def test_boton_rechazar_aprobado_tiene_handler(self):
        """Voucher APROBADO: botón Rechazar tiene on_click"""
        # Similar al anterior pero con estado APROBADO
        pass


class TestBlocRechazarFlow:
    """Tests del flujo en el BLoC"""
    
    def test_agregar_evento_rechazar_llama_manejar(self):
        """AGREGAR_EVENTO con RechazarVoucherEvento llama _manejar_rechazar"""
        from features.vouchers.presentation.bloc.VouchersBloc import VouchersBloc
        from features.vouchers.presentation.bloc.VouchersEvento import RechazarVoucherEvento
        
        bloc = VouchersBloc()
        
        with patch.object(bloc, '_manejar_rechazar') as mock_manejar:
            evento = RechazarVoucherEvento(
                voucher_id=50,
                validador_id=1,
                motivo="Test rechazo"
            )
            
            bloc.AGREGAR_EVENTO(evento)
            
            assert mock_manejar.called, "_manejar_rechazar debe ser llamado"
            mock_manejar.assert_called_once_with(evento)
    
    def test_manejar_rechazar_inicia_thread(self):
        """_manejar_rechazar debe iniciar thread con _rechazar_sync"""
        from features.vouchers.presentation.bloc.VouchersBloc import VouchersBloc
        from features.vouchers.presentation.bloc.VouchersEvento import RechazarVoucherEvento
        
        bloc = VouchersBloc()
        
        evento = RechazarVoucherEvento(
            voucher_id=50,
            validador_id=1,
            motivo="Test rechazo"
        )
        
        with patch('threading.Thread') as mock_thread:
            bloc._manejar_rechazar(evento)
            
            assert mock_thread.called, "Thread debe ser creado"
            # Verificar que se llama con _rechazar_sync
            call_args = mock_thread.call_args
            assert call_args[1]['target'] == bloc._rechazar_sync
    
    def test_rechazar_sync_llama_use_case(self):
        """_rechazar_sync debe llamar al use case RechazarVoucher"""
        from features.vouchers.presentation.bloc.VouchersBloc import VouchersBloc
        
        bloc = VouchersBloc()
        
        with patch.object(bloc._rechazar_voucher, 'ejecutar') as mock_ejecutar:
            mock_ejecutar.return_value = {"exito": True, "mensaje": "Test"}
            
            bloc._rechazar_sync(voucher_id=50, validador_id=1, motivo="Test")
            
            assert mock_ejecutar.called, "Use case ejecutar debe ser llamado"
            mock_ejecutar.assert_called_once_with(50, 1, "Test")


class TestRechazarVoucherUseCase:
    """Tests del use case RechazarVoucher"""
    
    def test_ejecutar_valida_motivo_minimo(self):
        """ejecutar debe validar motivo mínimo 10 caracteres"""
        from features.vouchers.domain.usecases.RechazarVoucher import RechazarVoucher
        
        repositorio = Mock()
        use_case = RechazarVoucher(repositorio)
        
        resultado = use_case.ejecutar(
            voucher_id=50,
            validador_id=1,
            motivo="corto"  # < 10 chars
        )
        
        assert resultado["exito"] == False
        assert "10 caracteres" in resultado["mensaje"]
    
    def test_ejecutar_llama_repositorio(self):
        """ejecutar debe llamar repositorio.rechazar_voucher"""
        from features.vouchers.domain.usecases.RechazarVoucher import RechazarVoucher
        
        repositorio = Mock()
        repositorio.obtener_por_id.return_value = Mock(estado="PENDIENTE")
        repositorio.rechazar_voucher.return_value = True
        
        use_case = RechazarVoucher(repositorio)
        
        resultado = use_case.ejecutar(
            voucher_id=50,
            validador_id=1,
            motivo="Comprobante ilegible"
        )
        
        assert repositorio.rechazar_voucher.called
        repositorio.rechazar_voucher.assert_called_once_with(50, 1, "Comprobante ilegible")
        assert resultado["exito"] == True


if __name__ == "__main__":
    print("=" * 60)
    print("TESTS DE CAJA BLANCA - COMPONENTES RECHAZAR")
    print("=" * 60)
    print("\nCOMPONENTES A VERIFICAR:")
    print("  1. VoucherHandlers.rechazar_click() - Abre diálogo")
    print("  2. VoucherHandlers._crear_dialogo_rechazo() - Crea estructura")
    print("  3. confirmar_rechazo() handler - PUNTO CRÍTICO")
    print("  4. VoucherCardBuilder botones - Asignación de handlers")
    print("  5. VouchersBloc._manejar_rechazar() - Recepción de evento")
    print("  6. VouchersBloc._rechazar_sync() - Ejecución async")
    print("  7. RechazarVoucher.ejecutar() - Lógica de negocio")
    print("\nPUNTO DE FALLA CRÍTICO:")
    print("  🔴 confirmar_rechazo() handler NO se ejecuta")
    print("  🔴 Necesario verificar asignación de on_click")
    print("\n" + "=" * 60)
