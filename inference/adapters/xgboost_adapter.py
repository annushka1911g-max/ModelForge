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
