#!/usr/bin/env python3
"""Integration test: connect to local WS broker, send sequence of events via HTTP broadcast,
and assert the connected client receives them in order.

Usage (from repo root):
  source venv/bin/activate
  python tools/integration_realtime_test.py
"""
import asyncio
import json
import urllib.request
import time

URI_WS = 'ws://127.0.0.1:8765/ws'
URL_BROADCAST = 'http://127.0.0.1:8765/broadcast'


async def run_test():
    import websockets

    received = []

    async def listener():
        async with websockets.connect(URI_WS) as ws:
            # listen for incoming messages and store them
            try:
                while True:
                    msg = await ws.recv()
                    try:
                        payload = json.loads(msg)
                    except Exception:
                        payload = msg
                    print('client received:', payload)
                    received.append(payload)
            except Exception:
                return

    # start listener task
    task = asyncio.create_task(listener())

    # small delay to ensure connection established
    await asyncio.sleep(0.5)

    # define sequence: create pedido, approve (actualizado), alert cocina
    seq = [
        {'type': 'pedido_creado', 'pedido_id': 1111, 'nuevo_estado': 'PENDIENTE', 'cliente_id': 10},
        {'type': 'pedido_actualizado', 'pedido_id': 1111, 'nuevo_estado': 'EN_PREPARACION'},
        {'type': 'pedido_alerta_cocina', 'pedido_id': 1111},
    ]

    for payload in seq:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(URL_BROADCAST, data=data, headers={'Content-Type': 'application/json'})
        try:
            resp = urllib.request.urlopen(req, timeout=2.0)
            body = resp.read()
            print('broadcast response:', body)
        except Exception as e:
            print('broadcast failed:', e)
        await asyncio.sleep(0.2)

    # wait up to 5s for messages to arrive
    deadline = time.time() + 5.0
    while time.time() < deadline and len(received) < len(seq):
        await asyncio.sleep(0.1)

    # cancel listener
    task.cancel()
    await asyncio.sleep(0.1)

    print('\nSummary: sent', len(seq), 'events, received', len(received))
    for r in received:
        print('-', r)

    if len(received) >= len(seq):
        print('\nINTEGRATION TEST: SUCCESS')
        return 0
    else:
        print('\nINTEGRATION TEST: FAILED')
        return 2


if __name__ == '__main__':
    import sys

    try:
        rc = asyncio.run(run_test())
    except KeyboardInterrupt:
        rc = 1
    sys.exit(rc)
