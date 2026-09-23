import React from 'react';
import { Button } from '../components/common/Button';

export const PlaygroundPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Inference Playground</h1>
        <p className="text-sm text-slate-400">Test live models interactively with single prediction inputs</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-slate-200">Input Features (JSON)</h2>
          <textarea
            className="w-full h-64 bg-slate-900 border border-slate-700 rounded-lg p-3 font-mono text-sm text-slate-200 focus:outline-none focus:border-blue-500"
            defaultValue={JSON.stringify({ age: 45, tenure: 3, monthly_charges: 75.5 }, null, 2)}
          />
          <Button className="w-full">Run Prediction</Button>
        </div>

        <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-slate-200">Prediction Response</h2>
          <div className="h-64 bg-slate-900 border border-slate-700 rounded-lg p-3 font-mono text-sm text-emerald-400 overflow-auto">
            <pre>{JSON.stringify({ prediction: [1], latency_ms: 14.2, version: 2 }, null, 2)}</pre>
          </div>
        </div>
      </div>
    </div>
  );
};
