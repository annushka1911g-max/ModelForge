import React from 'react';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';

export const ModelDetailPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">churn-prediction-xgb</h1>
          <p className="text-sm text-slate-400">Framework: XGBoost | Task: Classification</p>
        </div>
        <div className="flex gap-3">
          <Button variant="secondary">Upload Version</Button>
          <Button>Deploy Active Version</Button>
        </div>
      </div>

      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-slate-100 mb-4">Version History & Lineage</h2>
        <div className="space-y-3">
          <div className="p-4 bg-slate-900/60 border border-slate-700/60 rounded-lg flex justify-between items-center">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-slate-200">Version 2 (v2)</span>
                <Badge variant="success">ACTIVE DEPLOYED</Badge>
              </div>
              <p className="text-xs text-slate-400 mt-1">Artifact: models/1/v2/model.json | SHA256: 8f3c9e...</p>
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant="secondary">Inspect Schema</Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
