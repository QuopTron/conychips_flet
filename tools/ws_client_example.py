import asyncio
import json
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import websockets
from features.vouchers.presentation.bloc.VouchersBloc import VOUCHERS_BLOC
from features.vouchers.presentation.bloc.VouchersEvento import CargarVouchers

URI = 'ws://127.0.0.1:8765/ws'

async def run():
    async with websockets.connect(URI) as ws:
        print('Connected to WS broker')
        async for msg in ws:
            try:
                payload = json.loads(msg)
            except Exception:
                print('Invalid message:', msg)
                continue
            print('Received event:', payload)
            # Handle any voucher-related events; dispatch to VOUCHERS_BLOC and refresh pending
            if payload.get('type', '').startswith('voucher'):
                nuevo_estado = payload.get('nuevo_estado')
                sucursal_id = payload.get('sucursal_id')
                print('WS event for vouchers:', payload.get('type'), 'estado=', nuevo_estado, 'sucursal=', sucursal_id)
                try:
                    if nuevo_estado:
                        VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado=nuevo_estado, sucursal_id=sucursal_id))
                    if nuevo_estado != 'PENDIENTE':
                        VOUCHERS_BLOC.AGREGAR_EVENTO(CargarVouchers(estado='PENDIENTE', sucursal_id=sucursal_id))
                except Exception as e:
                    print('Error dispatching voucher events to bloc:', e)

def start_ws_client_in_thread():
    import threading

    def _run_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run())
        finally:
            loop.close()

    t = threading.Thread(target=_run_loop, daemon=True)
    t.start()
    return t

if __name__ == '__main__':
    asyncio.run(run())
