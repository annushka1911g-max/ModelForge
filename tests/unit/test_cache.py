"""
Unit tests for ModelCache LRU behavior.
"""
from inference.engine.cache import ModelCache
from inference.adapters.base import BaseModelAdapter


class _StubAdapter(BaseModelAdapter):
    """Minimal concrete adapter for testing the cache."""
    def load(self): pass
    def predict(self, features): return [0]
    def predict_proba(self, features): return [[0.9, 0.1]]


def _make_adapter(path="dummy/path") -> _StubAdapter:
    return _StubAdapter(path)


def test_cache_put_and_get():
    cache = ModelCache(max_size=3)
    adapter = _make_adapter()
    cache.put("dep:1:v1", adapter)
    assert cache.get("dep:1:v1") is adapter


def test_cache_miss_returns_none():
    cache = ModelCache(max_size=3)
    assert cache.get("non-existent") is None


def test_cache_evicts_lru_entry():
    cache = ModelCache(max_size=2)
    a1 = _make_adapter("a1")
    a2 = _make_adapter("a2")
    a3 = _make_adapter("a3")
    cache.put("k1", a1)
    cache.put("k2", a2)
    # Access k1 so k2 becomes LRU
    cache.get("k1")
    # Adding k3 should evict k2 (least recently used)
    cache.put("k3", a3)
    assert cache.get("k2") is None
    assert cache.get("k1") is a1
    assert cache.get("k3") is a3


def test_cache_invalidate():
    cache = ModelCache(max_size=3)
    adapter = _make_adapter()
    cache.put("dep:1:v1", adapter)
    cache.invalidate("dep:1:v1")
    assert cache.get("dep:1:v1") is None


def test_cache_clear():
    cache = ModelCache(max_size=5)
    for i in range(3):
        cache.put(f"key:{i}", _make_adapter())
    cache.clear()
    for i in range(3):
        assert cache.get(f"key:{i}") is None
