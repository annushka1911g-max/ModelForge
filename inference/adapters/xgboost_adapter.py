"""
XGBoost model adapter skeleton.
"""
from typing import Any, Dict, List, Union
from inference.adapters.base import BaseModelAdapter


class XGBoostAdapter(BaseModelAdapter):
    def load(self) -> None:
        """
        Loads XGBoost booster or sklearn-compatible XGBClassifier/XGBRegressor.
        """
        raise NotImplementedError("XGBoostAdapter.load to be implemented")

    def predict(self, features: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Any:
        """
        Executes XGBoost prediction.
        """
        raise NotImplementedError("XGBoostAdapter.predict to be implemented")

    def predict_proba(self, features: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Any:
        """
        Executes XGBoost probability prediction.
        """
        raise NotImplementedError("XGBoostAdapter.predict_proba to be implemented")
