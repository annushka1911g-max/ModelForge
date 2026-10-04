import React, { useState, useEffect, useRef } from 'react';
import { Bell, Check, CheckCheck, Info, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { platformService } from '../../services/platformService';
import type { NotificationItem } from '../../types';

const notifIcon = (type: string) => {
  switch (type) {
    case 'SUCCESS': return <CheckCircle className="w-4 h-4 text-emerald-400" />;
    case 'WARNING': return <AlertTriangle className="w-4 h-4 text-amber-400" />;
    case 'ERROR':   return <XCircle className="w-4 h-4 text-red-400" />;
    default:        return <Info className="w-4 h-4 text-brand-400" />;
  }
};

export const NotificationBell: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [count, setCount] = useState(0);
  const [items, setItems] = useState<NotificationItem[]>([]);
  const ref = useRef<HTMLDivElement>(null);

  const fetchCount = async () => {
    try {
      const n = await platformService.getUnreadNotificationCount();
      setCount(n);
    } catch { /* user might not be authed yet */ }
  };

  const fetchNotifications = async () => {
    try {
      const data = await platformService.listNotifications(false);
      setItems(data.slice(0, 10));
    } catch { /* ignore */ }
  };

  useEffect(() => {
    fetchCount();
    const interval = setInterval(fetchCount, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (open) fetchNotifications();
  }, [open]);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const markAll = async () => {
    await platformService.markAllNotificationsRead();
    setCount(0);
    setItems(prev => prev.map(i => ({ ...i, is_read: true })));
  };

  const markOne = async (id: number) => {
    await platformService.markNotificationRead(id);
    setItems(prev => prev.map(i => i.id === id ? { ...i, is_read: true } : i));
    setCount(prev => Math.max(0, prev - 1));
  };

  return (
    <div ref={ref} className="relative">
      <button
        id="notification-bell-btn"
        onClick={() => setOpen(!open)}
        className="relative p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
      >
        <Bell className="w-5 h-5" />
        {count > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 bg-brand-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center leading-none">
            {count > 9 ? '9+' : count}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-12 w-80 glass-panel rounded-xl shadow-glass z-50 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700/50">
            <span className="text-sm font-semibold text-slate-200">Notifications</span>
            {count > 0 && (
              <button onClick={markAll} className="flex items-center gap-1 text-xs text-brand-400 hover:text-brand-300 transition-colors">
                <CheckCheck className="w-3.5 h-3.5" /> Mark all read
              </button>
            )}
          </div>

          <div className="max-h-80 overflow-y-auto">
            {items.length === 0 ? (
              <div className="py-8 text-center text-slate-500 text-sm">No notifications</div>
            ) : (
              items.map((item) => (
                <div
                  key={item.id}
                  className={`flex gap-3 px-4 py-3 border-b border-slate-800/50 last:border-0 transition-colors ${
                    item.is_read ? 'opacity-60' : 'bg-slate-800/30'
                  }`}
                >
                  <div className="flex-shrink-0 mt-0.5">{notifIcon(item.notification_type)}</div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-slate-200 leading-snug">{item.title}</p>
                    <p className="text-xs text-slate-500 mt-0.5 truncate">{item.message}</p>
                    <p className="text-[10px] text-slate-600 mt-1">
                      {new Date(item.created_at).toLocaleString()}
                    </p>
                  </div>
                  {!item.is_read && (
                    <button
                      onClick={() => markOne(item.id)}
                      className="flex-shrink-0 p-1 text-slate-600 hover:text-slate-400"
                      title="Mark as read"
                    >
                      <Check className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};
