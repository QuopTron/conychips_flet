"""
Módulo de comunicación en tiempo real
Maneja dispatcher de eventos WebSocket y logs globales
"""
from typing import Dict, List, Callable, Any
import logging

log = logging.getLogger(__name__)


class EventDispatcher:
    """Dispatcher de eventos en tiempo real"""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
    
    def register(self, event_type: str, handler: Callable):
        """Registra un handler para un tipo de evento"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            log.info(f"Registered handler for event: {event_type}")
    
    def unregister(self, event_type: str, handler: Callable):
        """Desregistra un handler"""
        if event_type in self._handlers:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
                log.info(f"Unregistered handler for event: {event_type}")
    
    def dispatch(self, payload: Dict[str, Any]):
        """Despacha un evento a todos los handlers registrados"""
        event_type = payload.get('tipo') or payload.get('type')
        if not event_type:
            log.warning(f"Event without tipo/type: {payload}")
            return
        
        handlers = self._handlers.get(event_type, [])
        log.debug(f"Dispatching {event_type} to {len(handlers)} handlers")
        
        for handler in handlers:
            try:
                handler(payload)
            except Exception as e:
                log.exception(f"Error in handler for {event_type}: {e}")
    
    def clear(self):
        """Limpia todos los handlers (útil para tests)"""
        self._handlers.clear()


# Instancia global del dispatcher
dispatcher = EventDispatcher()

# Logs globales para admin/superadmin (último 1000 eventos)
logs: List[Dict[str, Any]] = []
MAX_LOGS = 1000


def append_log(payload: Dict[str, Any]):
    """Añade un evento a los logs globales"""
    logs.append(payload)
    if len(logs) > MAX_LOGS:
        logs.pop(0)
