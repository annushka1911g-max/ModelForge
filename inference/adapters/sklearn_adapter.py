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

    def get_feature_importance(self, feature_names: Union[List[str], None] = None) -> Union[List[Dict[str, Any]], None]:
        estimator = self.model
        if hasattr(estimator, 'steps'):
            # It's an sklearn Pipeline, inspect the final estimator
            estimator = estimator.steps[-1][1]

        raw_importances = None
        if hasattr(estimator, 'feature_importances_'):
            raw_importances = estimator.feature_importances_
        elif hasattr(estimator, 'coef_'):
            coef = estimator.coef_
            raw_importances = np.mean(np.abs(coef), axis=0) if len(coef.shape) > 1 else np.abs(coef)

        if raw_importances is None:
            return None

        importances = np.array(raw_importances).flatten()
        total = np.sum(importances)
        total = total if total > 0 else 1.0

        names = feature_names or [f"feature_{i}" for i in range(len(importances))]
        results = []
        for i, val in enumerate(importances):
            name = names[i] if i < len(names) else f"feature_{i}"
            float_val = float(val)
            results.append({
                "feature": name,
                "importance": round(float_val, 4),
                "relative_contribution": round((float_val / total) * 100, 2),
            })

        results.sort(key=lambda x: x["importance"], reverse=True)
        return results
