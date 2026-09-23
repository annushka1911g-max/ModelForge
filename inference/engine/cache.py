"""
In-memory LRU model cache for ModelForge.
"""
from collections import OrderedDict
from typing import Optional
from inference.adapters.base import BaseModelAdapter


class ModelCache:
    """
    Thread-safe or async-compatible in-memory LRU cache storing loaded model adapters.
    """

    def __init__(self, max_size: int = 5):
        self.max_size = max_size
        self._cache: OrderedDict[str, BaseModelAdapter] = OrderedDict()

    def get(self, key: str) -> Optional[BaseModelAdapter]:
        """
        Retrieves cached adapter if present, updating LRU order.
        """
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, key: str, adapter: BaseModelAdapter) -> None:
        """
        Inserts or updates an adapter in cache, evicting the oldest if limit exceeded.
        """
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = adapter
        if len(self._cache) > self.max_size:
            self._cache.popitem(last=False)

    def invalidate(self, key: str) -> None:
        """
        Removes an entry from cache on rollback or redeploy.
        """
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """
        Clears all cached adapters.
        """
        self._cache.clear()
