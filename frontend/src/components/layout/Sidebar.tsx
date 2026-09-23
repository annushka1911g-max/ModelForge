import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../authentication/useAuth';

export const Sidebar: React.FC = () => {
  const { user } = useAuth();

  const links = [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/models', label: 'Model Catalog' },
    { to: '/deployments', label: 'Deployments' },
    { to: '/playground', label: 'Inference Playground' },
    { to: '/batch', label: 'Batch Prediction' },
    { to: '/monitoring', label: 'Monitoring & Metrics' },
  ];

  if (user?.role === 'ADMIN') {
    links.push({ to: '/users', label: 'User Admin' });
  }

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col p-4">
      <nav className="space-y-1">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              `flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors ${
                isActive
                  ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
              }`
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};
