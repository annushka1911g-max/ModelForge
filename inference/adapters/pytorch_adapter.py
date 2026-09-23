"""
PyTorch model adapter skeleton.
"""
from typing import Any, Dict, List, Union
from inference.adapters.base import BaseModelAdapter


class PyTorchAdapter(BaseModelAdapter):
    def load(self) -> None:
        """
        Loads PyTorch TorchScript or state_dict model on CPU.
        """
        raise NotImplementedError("PyTorchAdapter.load to be implemented")

    def predict(self, features: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Any:
        """
        Executes torch model forward pass.
        """
        raise NotImplementedError("PyTorchAdapter.predict to be implemented")

    def predict_proba(self, features: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Any:
        """
        Executes softmax probability calculation.
        """
        raise NotImplementedError("PyTorchAdapter.predict_proba to be implemented")
