"""
TensorFlow / Keras model adapter skeleton.
"""
from typing import Any, Dict, List, Union
from inference.adapters.base import BaseModelAdapter


class TensorFlowAdapter(BaseModelAdapter):
    def load(self) -> None:
        """
        Loads TensorFlow SavedModel or Keras .h5 / .keras model.
        """
        raise NotImplementedError("TensorFlow framework adapter is not supported in this release")

    def predict(self, features: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Any:
        """
        Executes TF/Keras model.predict().
        """
        raise NotImplementedError("TensorFlow framework adapter is not supported in this release")

    def predict_proba(self, features: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Any:
        """
        Returns prediction probabilities.
        """
        raise NotImplementedError("TensorFlow framework adapter is not supported in this release")
