import React from 'react';
import { Button } from '../components/common/Button';

export const BatchPredictPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Batch Prediction Console</h1>
        <p className="text-sm text-slate-400">Upload bulk dataset CSVs for high-throughput batch inference</p>
      </div>

      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-8 text-center border-dashed border-2 border-slate-600">
        <p className="text-slate-300 font-medium">Drag & Drop Batch CSV File</p>
        <p className="text-xs text-slate-500 mt-1">Accepts UTF-8 encoded .csv files up to 50MB</p>
        <div className="mt-4">
          <Button variant="secondary">Select File</Button>
        </div>
      </div>
    </div>
  );
};
