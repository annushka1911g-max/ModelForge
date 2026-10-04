import joblib
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Union
from inference.adapters.base import BaseModelAdapter

class XGBoostAdapter(BaseModelAdapter):
    def load(self):
        # XGBoost models can be saved as joblib (sklearn-compatible) or native .json/.ubj
        import xgboost as xgb
        if self.model_path.endswith(('.json', '.ubj')):
            self.model = xgb.Booster()
            self.model.load_model(self.model_path)
        else:
            # sklearn-compatible XGBClassifier/XGBRegressor saved with joblib
            self.model = joblib.load(self.model_path)
    
    def predict(self, features):
        df = pd.DataFrame([features] if isinstance(features, dict) else features)
        import xgboost as xgb
        if isinstance(self.model, xgb.Booster):
            dmatrix = xgb.DMatrix(df)
            predictions = self.model.predict(dmatrix)
            return predictions.tolist()
        return self.model.predict(df).tolist()
    
    def predict_proba(self, features):
        df = pd.DataFrame([features] if isinstance(features, dict) else features)
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(df).tolist()
        return None

    def get_feature_importance(self, feature_names: Union[List[str], None] = None) -> Union[List[Dict[str, Any]], None]:
        import xgboost as xgb
        raw_importances = None
        if isinstance(self.model, xgb.Booster):
            score = self.model.get_score(importance_type="gain")
            if not score:
                return None
            total = sum(score.values()) or 1.0
            results = [
                {
                    "feature": k,
                    "importance": round(float(v), 4),
                    "relative_contribution": round((float(v) / total) * 100, 2),
                }
                for k, v in score.items()
            ]
            results.sort(key=lambda x: x["importance"], reverse=True)
            return results
        elif hasattr(self.model, "feature_importances_"):
            raw_importances = self.model.feature_importances_

        if raw_importances is None:
            return None

        importances = np.array(raw_importances).flatten()
        total = np.sum(importances) or 1.0
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
