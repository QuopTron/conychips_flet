import asyncio
import json
import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import websockets
from websockets.exceptions import ConnectionClosed

from features.vouchers.presentation.bloc.VouchersBloc import VOUCHERS_BLOC
from features.vouchers.presentation.bloc.VouchersEvento import CargarVouchers

URI = 'ws://127.0.0.1:8765/ws'

log = logging.getLogger(__name__)


async def run_client(stop_event: asyncio.Event = None):
    backoff = 1
    max_backoff = 60
    while True:
        if stop_event is not None and stop_event.is_set():
            log.info('WS client stop requested; exiting')
            return
        try:
            log.info('Attempting to connect to WS broker at %s', URI)
            async with websockets.connect(URI, ping_interval=20, ping_timeout=10) as ws:
                log.info('Connected to WS broker')
                backoff = 1
                async for msg in ws:
                    try:
                        payload = json.loads(msg)
                    except Exception:
                        log.warning('Invalid WS message: %s', msg)
                        continue
                    log.debug('Received WS event: %s', payload)
                    # Log and dispatch to registered local callbacks
                    try:
                        from core.realtime import dispatcher, logs
                        # append to logs for admin/superadmin
                        try:
                            logs.append(payload)
                        except Exception:
                            pass

                        # dispatch to any registered handlers
                        try:
                            dispatcher.dispatch(payload)
                        except Exception:
                            pass
                    except Exception as e:
                        log.exception('Error dispatching event to local dispatcher: %s', e)
        except (ConnectionClosed, OSError, websockets.InvalidURI, websockets.InvalidHandshake) as e:
            log.warning('WS connection lost or failed: %s', e)
        except Exception:
            log.exception('Unexpected error in WS client')

        # Exponential backoff before reconnecting
        log.info('Reconnecting to WS broker in %s seconds...', backoff)
        try:
            await asyncio.sleep(backoff)
        except asyncio.CancelledError:
            log.info('WS client cancelled during backoff')
            return
        backoff = min(backoff * 2, max_backoff)


def start_ws_client_in_thread():
    import threading

    stop_event = threading.Event()

    def _run_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        stop_async = asyncio.Event()

        def _stop_when_requested():
            while not stop_event.is_set():
                stop_event.wait(0.1)
            loop.call_soon_threadsafe(stop_async.set)

        stopper = threading.Thread(target=_stop_when_requested, daemon=True)
        stopper.start()

        try:
            loop.run_until_complete(run_client(stop_async))
        finally:
            loop.close()

    t = threading.Thread(target=_run_loop, daemon=True)
    t.start()
    return t, stop_event


if __name__ == '__main__':
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        pass
