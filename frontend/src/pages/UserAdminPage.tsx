import React, { useEffect, useState } from 'react';
import { Badge } from '../components/common/Badge';
import { authService } from '../services/authService';
import { User, UserRole } from '../types';

export const UserAdminPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  const loadUsers = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await authService.getUsers();
      setUsers(data);
    } catch (err: any) {
      setError('Failed to load user roster.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleRoleChange = async (userId: number, newRole: UserRole) => {
    setUpdatingId(userId);
    setError(null);
    setSuccessMsg(null);
    try {
      await authService.updateUser(userId, { role: newRole });
      setSuccessMsg(`User #${userId} role updated to ${newRole}.`);
      await loadUsers();
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Failed to update user role.');
    } finally {
      setUpdatingId(null);
    }
  };

  const handleToggleActive = async (userId: number, currentActive: boolean) => {
    setUpdatingId(userId);
    setError(null);
    setSuccessMsg(null);
    try {
      await authService.updateUser(userId, { is_active: !currentActive });
      setSuccessMsg(`User #${userId} is now ${!currentActive ? 'Active' : 'Deactivated'}.`);
      await loadUsers();
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Failed to update user status.');
    } finally {
      setUpdatingId(null);
    }
  };

  const getRoleBadge = (role: UserRole) => {
    switch (role) {
      case 'ADMIN':
        return <Badge variant="info">ADMIN</Badge>;
      case 'ML_ENGINEER':
        return <Badge variant="success">ML_ENGINEER</Badge>;
      case 'VIEWER':
        return <Badge variant="warning">VIEWER</Badge>;
      default:
        return <Badge variant="info">{role}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
          User Management & RBAC
        </h1>
        <p className="text-sm text-slate-400">
          Administer platform users, manage permissions, and assign security roles
        </p>
      </div>

      {error && (
        <div className="bg-rose-950/60 border border-rose-800 text-rose-300 text-sm px-4 py-3 rounded-lg flex justify-between items-center">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-rose-400 hover:text-rose-200">
            ✕
          </button>
        </div>
      )}

      {successMsg && (
        <div className="bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-sm px-4 py-3 rounded-lg flex justify-between items-center">
          <span>{successMsg}</span>
          <button onClick={() => setSuccessMsg(null)} className="text-emerald-400 hover:text-emerald-200">
            ✕
          </button>
        </div>
      )}

      <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-6">
        {isLoading ? (
          <div className="py-12 text-center text-slate-400">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
            Loading platform users...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs uppercase bg-slate-900/50 text-slate-400">
                <tr>
                  <th className="px-4 py-3">User</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Current Role</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Registered</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-slate-750/30">
                    <td className="px-4 py-3 font-semibold text-slate-200">
                      {user.full_name}
                      <div className="text-xs text-slate-500 font-mono">ID: {user.id}</div>
                    </td>
                    <td className="px-4 py-3 text-slate-300 font-mono text-xs">{user.email}</td>
                    <td className="px-4 py-3">{getRoleBadge(user.role)}</td>
                    <td className="px-4 py-3">
                      {user.is_active ? (
                        <span className="text-emerald-400 font-medium text-xs flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Active
                        </span>
                      ) : (
                        <span className="text-rose-400 font-medium text-xs flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span> Deactivated
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-400">
                      {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex justify-end items-center gap-2">
                        <select
                          value={user.role}
                          disabled={updatingId === user.id}
                          onChange={(e) => handleRoleChange(user.id, e.target.value as UserRole)}
                          className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded px-2 py-1 focus:outline-none focus:border-blue-500"
                        >
                          <option value="ADMIN">ADMIN</option>
                          <option value="ML_ENGINEER">ML_ENGINEER</option>
                          <option value="VIEWER">VIEWER</option>
                        </select>
                        <button
                          type="button"
                          disabled={updatingId === user.id}
                          onClick={() => handleToggleActive(user.id, user.is_active)}
                          className={`text-xs px-2.5 py-1 rounded transition-colors ${
                            user.is_active
                              ? 'bg-rose-950/60 hover:bg-rose-900 text-rose-300 border border-rose-800'
                              : 'bg-emerald-950/60 hover:bg-emerald-900 text-emerald-300 border border-emerald-800'
                          }`}
                        >
                          {user.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
