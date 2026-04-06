# backend/app/utils/cache.py
import hashlib
import time
import logging
from typing import Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class InMemoryCache:
    """
    Simple TTL-based in-memory cache.
    For production, swap with Redis.
    """

    def __init__(self, ttl: int = 3600, max_size: int = 500):
        self._store: dict[str, dict] = {}
        self.ttl = ttl
        self.max_size = max_size

    def _make_key(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def get(self, text: str) -> Optional[Any]:
        key = self._make_key(text)
        entry = self._store.get(key)
        if not entry:
            return None
        if time.time() - entry['timestamp'] > self.ttl:
            del self._store[key]
            logger.debug(f"Cache expired for key {key[:8]}...")
            return None
        logger.debug(f"Cache HIT for key {key[:8]}...")
        return entry['value']

    def set(self, text: str, value: Any) -> None:
        if len(self._store) >= self.max_size:
            # Evict oldest entry
            oldest = min(self._store.items(), key=lambda x: x[1]['timestamp'])
            del self._store[oldest[0]]

        key = self._make_key(text)
        self._store[key] = {'value': value, 'timestamp': time.time()}
        logger.debug(f"Cache SET for key {key[:8]}...")

    def get_by_key(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if not entry:
            return None
        if time.time() - entry['timestamp'] > self.ttl:
            del self._store[key]
            logger.debug(f"Cache expired for key {key[:8]}...")
            return None
        logger.debug(f"Cache HIT for key {key[:8]}...")
        return entry['value']

    def set_by_key(self, key: str, value: Any) -> None:
        if len(self._store) >= self.max_size:
            # Evict oldest entry
            oldest = min(self._store.items(), key=lambda x: x[1]['timestamp'])
            del self._store[oldest[0]]

        self._store[key] = {'value': value, 'timestamp': time.time()}
        logger.debug(f"Cache SET for key {key[:8]}...")

    def clear(self) -> int:
        count = len(self._store)
        self._store.clear()
        return count

    def stats(self) -> dict:
        now = time.time()
        live = sum(1 for v in self._store.values() if now - v['timestamp'] <= self.ttl)
        return {
            'total_entries': len(self._store),
            'live_entries': live,
            'expired_entries': len(self._store) - live,
            'ttl_seconds': self.ttl,
        }


# Singleton cache instance
_cache = InMemoryCache()


def get_cache() -> InMemoryCache:
    return _cache


def cached(ttl: Optional[int] = None):
    """
    Decorator for caching function results based on first string argument.
    Usage:
        @cached(ttl=3600)
        def analyze(text: str) -> dict: ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Use first str arg as cache key
            text_key = next((a for a in args if isinstance(a, str)), None)
            if not text_key:
                return fn(*args, **kwargs)

            cache = get_cache()
            cached_result = cache.get(text_key)
            if cached_result is not None:
                logger.info(f"Returning cached result for {fn.__name__}")
                return cached_result

            result = fn(*args, **kwargs)
            cache.set(text_key, result)
            return result
        return wrapper
    return decorator