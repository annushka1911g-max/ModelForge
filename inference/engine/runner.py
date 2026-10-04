import time
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from inference.engine.cache import ModelCache
from inference.adapters.base import BaseModelAdapter
from inference.adapters.sklearn_adapter import SklearnAdapter
from inference.adapters.xgboost_adapter import XGBoostAdapter
from inference.adapters.pytorch_adapter import PyTorchAdapter
from inference.adapters.tensorflow_adapter import TensorFlowAdapter

logger = logging.getLogger("modelforge.inference.runner")

FRAMEWORK_ADAPTERS = {
    "SCIKIT_LEARN": SklearnAdapter,
    "XGBOOST": XGBoostAdapter,
    "PYTORCH": PyTorchAdapter,
    "TENSORFLOW": TensorFlowAdapter,
}

class ModelRunner:
    def __init__(self, cache: ModelCache):
        self.cache = cache
    
    def _get_cache_key(self, deployment_id: int, version_id: int) -> str:
        return f"dep:{deployment_id}:v:{version_id}"
    
    def _load_adapter(self, artifact_path: str, framework: str) -> BaseModelAdapter:
        adapter_cls = FRAMEWORK_ADAPTERS.get(framework)
        if not adapter_cls:
            raise ValueError(f"Unsupported framework: {framework}. Supported: {list(FRAMEWORK_ADAPTERS.keys())}")
        adapter = adapter_cls(artifact_path)
        adapter.load()
        logger.info("Loaded model adapter for framework=%s from %s", framework, artifact_path)
        return adapter
    
    def execute_prediction(self, deployment_id, version_id, artifact_path, framework, features) -> Tuple[Any, Optional[List], float]:
        cache_key = self._get_cache_key(deployment_id, version_id)
        adapter = self.cache.get(cache_key)
        
        if adapter is None:
            adapter = self._load_adapter(artifact_path, framework)
            self.cache.put(cache_key, adapter)
        
        start = time.perf_counter()
        prediction = adapter.predict(features)
        probabilities = adapter.predict_proba(features)
        latency_ms = (time.perf_counter() - start) * 1000
        
        return prediction, probabilities, latency_ms
    
    def invalidate_cache(self, deployment_id: int, version_id: int):
        cache_key = self._get_cache_key(deployment_id, version_id)
        self.cache.invalidate(cache_key)
