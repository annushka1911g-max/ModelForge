import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../authentication/useAuth';
import {
  LayoutDashboard,
  Box,
  Rocket,
  Terminal,
  Layers,
  ActivitySquare,
  FlaskConical,
  ScrollText,
  Users,
  Settings,
  ChevronRight,
} from 'lucide-react';

interface NavItem {
  to: string;
  label: string;
  icon: React.ReactNode;
  roles?: string[];
}

const NAV_ITEMS: NavItem[] = [
  { to: '/dashboard',   label: 'Dashboard',       icon: <LayoutDashboard className="w-4 h-4" /> },
  { to: '/models',      label: 'Model Catalog',    icon: <Box className="w-4 h-4" /> },
  { to: '/deployments', label: 'Deployments',      icon: <Rocket className="w-4 h-4" /> },
  { to: '/playground',  label: 'Playground',       icon: <Terminal className="w-4 h-4" /> },
  { to: '/batch',       label: 'Batch Predict',    icon: <Layers className="w-4 h-4" /> },
  { to: '/monitoring',  label: 'Monitoring',       icon: <ActivitySquare className="w-4 h-4" /> },
  { to: '/experiments', label: 'Experiments',      icon: <FlaskConical className="w-4 h-4" /> },
  { to: '/predictions', label: 'Predictions',      icon: <ScrollText className="w-4 h-4" /> },
  { to: '/audit-logs',  label: 'Audit Logs',       icon: <ScrollText className="w-4 h-4" />, roles: ['ADMIN', 'ML_ENGINEER'] },
  { to: '/settings',    label: 'Settings & Keys',  icon: <Settings className="w-4 h-4" /> },
  { to: '/users',       label: 'User Admin',       icon: <Users className="w-4 h-4" />, roles: ['ADMIN'] },
];

export const Sidebar: React.FC = () => {
  const { user } = useAuth();

  const visibleLinks = NAV_ITEMS.filter(item => {
    if (!item.roles) return true;
    return item.roles.includes(user?.role ?? '');
  });

  return (
    <aside className="w-60 flex-shrink-0 bg-slate-900/60 border-r border-slate-800/60 flex flex-col pt-2 pb-4">
      <nav className="flex-1 px-3 space-y-0.5">
        {visibleLinks.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            id={`nav-${link.to.replace('/', '')}`}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-all group relative ${
                isActive
                  ? 'bg-brand-600/15 text-brand-300 border border-brand-500/20'
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
              }`
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-brand-500 rounded-full" />
                )}
                <span className={`transition-colors ${isActive ? 'text-brand-400' : 'text-slate-500 group-hover:text-slate-400'}`}>
                  {link.icon}
                </span>
                <span className="flex-1">{link.label}</span>
                {isActive && <ChevronRight className="w-3 h-3 text-brand-500/70" />}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="px-3 mt-4">
        <div className="rounded-lg bg-gradient-to-br from-brand-950/80 to-slate-900 border border-brand-800/30 p-3">
          <p className="text-xs font-semibold text-brand-300">ModelForge</p>
          <p className="text-[11px] text-slate-500 mt-0.5">v2.0 — Production-Ready MLOps</p>
        </div>
      </div>
    </aside>
  );
};
