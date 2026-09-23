import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'neutral' }) => {
  const styles = {
    success: 'bg-emerald-950 text-emerald-400 border border-emerald-800',
    warning: 'bg-amber-950 text-amber-400 border border-amber-800',
    danger: 'bg-rose-950 text-rose-400 border border-rose-800',
    info: 'bg-sky-950 text-sky-400 border border-sky-800',
    neutral: 'bg-slate-800 text-slate-300 border border-slate-700',
  }[variant];

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles}`}>
      {children}
    </span>
  );
};
