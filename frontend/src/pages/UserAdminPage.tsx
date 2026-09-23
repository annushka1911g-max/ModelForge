import React from 'react';
import { Badge } from '../components/common/Badge';

export const UserAdminPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">User Management (RBAC)</h1>
        <p className="text-sm text-slate-400">Manage platform users, roles, and administrative permissions</p>
      </div>

      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-6">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="text-xs uppercase bg-slate-900/50 text-slate-400">
            <tr>
              <th className="px-4 py-3">User</th>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Role</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/50">
            <tr>
              <td className="px-4 py-3 font-semibold text-slate-200">Admin User</td>
              <td className="px-4 py-3 text-slate-400">admin@modelforge.local</td>
              <td className="px-4 py-3"><Badge variant="info">ADMIN</Badge></td>
              <td className="px-4 py-3 text-emerald-400">Active</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};
