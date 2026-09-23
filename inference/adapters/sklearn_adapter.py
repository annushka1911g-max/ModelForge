"""
Scikit-learn model adapter skeleton.
"""
from typing import Any, Dict, List, Union
from inference.adapters.base import BaseModelAdapter


class SklearnAdapter(BaseModelAdapter):
    def load(self) -> None:
        """
        Loads .joblib or .pkl model.
        """
        raise NotImplementedError("SklearnAdapter.load to be implemented")

    def predict(self, features: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Any:
        """
        Executes scikit-learn model.predict().
        """
        raise NotImplementedError("SklearnAdapter.predict to be implemented")

    def predict_proba(self, features: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Any:
        """
        Executes scikit-learn model.predict_proba().
        """
        raise NotImplementedError("SklearnAdapter.predict_proba to be implemented")
