"""
Abstract Base Model Adapter for ModelForge Dynamic Serving.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union


class BaseModelAdapter(ABC):
    """
    Standard interface for all framework-specific model runners.
    """

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model: Any = None

    @abstractmethod
    def load(self) -> None:
        """
        Loads the model weights/binary into memory.
        """
        pass

    @abstractmethod
    def predict(self, features: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Any:
        """
        Executes prediction on the formatted input features.
        """
        pass

    @abstractmethod
    def predict_proba(self, features: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Any:
        """
        Executes probability estimation if supported by the model.
        """
        pass
