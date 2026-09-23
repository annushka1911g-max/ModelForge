import React from 'react';
import { Button } from '../components/common/Button';

export const ModelsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Model Catalog</h1>
          <p className="text-sm text-slate-400">Manage registered models, framework bindings, and version lineages</p>
        </div>
        <Button>+ Register New Model</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-5 hover:border-slate-600 transition-all">
          <div className="flex justify-between items-start">
            <h3 className="font-semibold text-slate-100">churn-prediction-xgb</h3>
            <span className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded">XGBOOST</span>
          </div>
          <p className="text-sm text-slate-400 mt-2">Customer churn classifier based on subscriber activity telemetry.</p>
          <div className="mt-4 pt-4 border-t border-slate-700/50 flex justify-between items-center text-xs text-slate-400">
            <span>2 Versions</span>
            <span className="text-emerald-400">Deployed (v2)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
