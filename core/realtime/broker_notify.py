import json
import urllib.request
import urllib.error

BROKER_URL = 'http://127.0.0.1:8765/broadcast'


def notify(payload: dict):
    """Send a JSON payload to the local WS broker broadcast endpoint.
    This function intentionally silences errors so DB commits don't fail
    if the broker is unavailable (development-friendly).
    """
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(BROKER_URL, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            return resp.read()
    except Exception:
        # Silenciar errores para que operaciones de DB no fallen por el broker
        return None
