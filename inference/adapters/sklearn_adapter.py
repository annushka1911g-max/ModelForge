import joblib
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Union
from inference.adapters.base import BaseModelAdapter

class SklearnAdapter(BaseModelAdapter):
    def load(self):
        self.model = joblib.load(self.model_path)
    
    def predict(self, features: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Any:
        df = pd.DataFrame([features] if isinstance(features, dict) else features)
        predictions = self.model.predict(df)
        return predictions.tolist()
    
    def predict_proba(self, features: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Any:
        df = pd.DataFrame([features] if isinstance(features, dict) else features)
        if hasattr(self.model, 'predict_proba'):
            probas = self.model.predict_proba(df)
            return probas.tolist()
        return None
