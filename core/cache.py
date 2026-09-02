import threading
import time
from typing import Any


class TTLCache:
    """Cache em memória com expiração por tempo (thread-safe)."""

    def __init__(self, max_entries: int = 128):
        self._max_entries = max_entries
        self._store: dict[Any, tuple[Any, float]] = {}
        self._lock = threading.RLock()

    def get(self, key) -> Any | None:
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None

            value, expires = item
            if expires < time.monotonic():
                del self._store[key]
                return None

            return value

    def set(self, key, value, ttl: float) -> None:
        with self._lock:
            if len(self._store) >= self._max_entries:
                # Limite simples: quando estoura, limpa tudo (evita crescimento
                # infinito com combinações de filtros diferentes).
                self._store.clear()

            self._store[key] = (value, time.monotonic() + ttl)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()