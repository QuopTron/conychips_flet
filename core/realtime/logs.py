from collections import deque
from typing import List, Dict

# In-memory ring buffer for recent realtime events (dev use)
_BUFFER = deque(maxlen=500)


def append(payload: Dict):
    try:
        _BUFFER.appendleft(payload)
    except Exception:
        pass


def recent(limit: int = 100) -> List[Dict]:
    return list(_BUFFER)[:limit]
