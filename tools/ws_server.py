import asyncio
import json
from aiohttp import web

CLIENTS = set()

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    CLIENTS.add(ws)
    print('WS client connected, total:', len(CLIENTS))
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                # echo or ignore
                pass
    finally:
        CLIENTS.remove(ws)
        print('WS client disconnected, total:', len(CLIENTS))
    return ws

async def broadcast(request):
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({'ok': False, 'error': 'invalid json'}, status=400)
    text = json.dumps(payload)
    to_remove = []
    for ws in list(CLIENTS):
        try:
            await ws.send_str(text)
        except Exception:
            to_remove.append(ws)
    for ws in to_remove:
        CLIENTS.discard(ws)
    return web.json_response({'ok': True, 'sent': len(CLIENTS)})

async def index(request):
    return web.Response(text='WS Broker running')

app = web.Application()
app.add_routes([
    web.get('/ws', websocket_handler),
    web.post('/broadcast', broadcast),
    web.get('/', index)
])

if __name__ == '__main__':
    web.run_app(app, port=8765)
