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
        raise NotImplementedError("PyTorch framework adapter is not supported in this release")

    def predict(self, features: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Any:
        """
        Executes torch model forward pass.
        """
        raise NotImplementedError("PyTorch framework adapter is not supported in this release")

    def predict_proba(self, features: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Any:
        """
        Executes softmax probability calculation.
        """
        raise NotImplementedError("PyTorch framework adapter is not supported in this release")
