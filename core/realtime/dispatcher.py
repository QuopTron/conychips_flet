from typing import Callable, Dict, List

# Simple in-process event dispatcher for realtime events
_HANDLERS: Dict[str, List[Callable]] = {}


def register(event_type: str, callback: Callable):
    """Register a callback for a specific event type. Use '*' to subscribe to all."""
    handlers = _HANDLERS.setdefault(event_type, [])
    if callback not in handlers:
        handlers.append(callback)


def unregister(event_type: str, callback: Callable):
    handlers = _HANDLERS.get(event_type)
    if not handlers:
        return
    try:
        handlers.remove(callback)
    except ValueError:
        pass


def dispatch(payload: dict):
    """Dispatch a payload to handlers registered for its `type` and to '*' handlers."""
    if not isinstance(payload, dict):
        return
    et = payload.get('type')
    # copy lists to avoid modification during iteration
    global_handlers = list(_HANDLERS.get('*', []))
    specific_handlers = list(_HANDLERS.get(et, [])) if et else []

    for cb in global_handlers + specific_handlers:
        try:
            cb(payload)
        except Exception:
            # Handlers should guard their own errors
            pass
