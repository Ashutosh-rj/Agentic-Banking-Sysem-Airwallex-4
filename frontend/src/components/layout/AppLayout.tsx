import React, { useState, useEffect } from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, CreditCard, AlertTriangle, Bot, CheckCircle2,
  Wallet, ShieldAlert, BarChart3, History, Plug, Settings,
  LogOut, Bell, Search, ShieldCheck, ChevronDown, Check,
  ExternalLink, Sparkles, AlertCircle
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';

export const AppLayout: React.FC = () => {
  const { user, logout, quickDemoLogin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isRoleMenuOpen, setIsRoleMenuOpen] = useState(false);
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const [systemHealth, setSystemHealth] = useState<'healthy' | 'checking' | 'error'>('checking');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await api.get('/health/live');
        if (res.data?.status === 'alive') setSystemHealth('healthy');
        else setSystemHealth('error');
      } catch {
        setSystemHealth('error');
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { label: 'Command Center', path: '/app', icon: LayoutDashboard },
    { label: 'Payments', path: '/app/payments', icon: CreditCard },
    { label: 'Incident Commander', path: '/app/incidents', icon: AlertTriangle, badge: 'Active' },
    { label: 'AI Investigation', path: '/app/ai-investigation', icon: Bot, isNew: true },
    { label: 'Reconciliation', path: '/app/reconciliation', icon: CheckCircle2 },
    { label: 'Treasury & Cash Flow', path: '/app/treasury', icon: Wallet },
    { label: 'Risk & Controls', path: '/app/risk', icon: ShieldAlert },
    { label: 'Analytics & ROI', path: '/app/analytics', icon: BarChart3 },
    { label: 'Audit Logs', path: '/app/audit-logs', icon: History },
    { label: 'Integrations', path: '/app/integrations', icon: Plug },
    { label: 'Settings', path: '/app/settings', icon: Settings },
  ];

  const roles = [
    { id: 'admin', label: 'Admin (Sarah Chen)', desc: 'Full system & policy access' },
    { id: 'treasury_manager', label: 'Treasury Manager (Marcus Wells)', desc: 'Approvals & liquidity management' },
    { id: 'payment_ops', label: 'Payment Ops (Priya Patel)', desc: 'Transaction investigation & retry' },
    { id: 'auditor', label: 'Auditor (James Rodriguez)', desc: 'Read-only compliance verification' },
  ];

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800/80 bg-slate-900/60 backdrop-blur-md flex flex-col flex-shrink-0">
        {/* Brand */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <NavLink to="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-amber-600 to-amber-400 flex items-center justify-center font-bold text-slate-950 text-base shadow-lg shadow-amber-500/20 group-hover:scale-105 transition-transform">
              K
            </div>
            <div>
              <span className="font-bold tracking-tight text-slate-100 flex items-center gap-1.5 text-base">
                KAIZEN
                <span className="text-[10px] font-semibold bg-amber-500/10 text-amber-400 px-1.5 py-0.2 rounded border border-amber-500/20">
                  FINTECH
                </span>
              </span>
              <p className="text-[10px] text-slate-400 tracking-wider uppercase font-medium">Treasury Intelligence</p>
            </div>
          </NavLink>
        </div>

        {/* Environment Badge */}
        <div className="px-4 py-2 bg-slate-950/40 border-b border-slate-800/60 flex items-center justify-between text-xs">
          <div className="flex items-center gap-1.5 text-slate-400">
            <span className={`w-2 h-2 rounded-full ${systemHealth === 'healthy' ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
            <span className="font-mono text-[11px]">System Online</span>
          </div>
          <span className="bg-amber-500/10 text-amber-400 text-[10px] font-semibold px-2 py-0.5 rounded border border-amber-500/30">
            DEMO MODE
          </span>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-amber-400' : 'text-slate-500'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] bg-rose-500/10 text-rose-400 px-1.5 py-0.5 rounded border border-rose-500/20 font-mono">
                    {item.badge}
                  </span>
                )}
                {item.isNew && (
                  <span className="text-[10px] bg-purple-500/10 text-purple-400 px-1.5 py-0.5 rounded border border-purple-500/20 flex items-center gap-1 font-mono">
                    <Sparkles className="w-2.5 h-2.5" /> AGENT
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* User Card & Logout */}
        <div className="p-3 border-t border-slate-800 bg-slate-900/80">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-semibold text-xs text-amber-400 flex-shrink-0">
                {user?.avatar_initials || user?.full_name?.substring(0, 2).toUpperCase() || 'KZ'}
              </div>
              <div className="truncate">
                <p className="text-xs font-semibold text-slate-200 truncate">{user?.full_name || 'Demo User'}</p>
                <p className="text-[10px] text-slate-400 capitalize truncate">{user?.role?.replace('_', ' ') || 'analyst'}</p>
              </div>
            </div>
            <button
              onClick={logout}
              title="Sign Out"
              className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="h-14 border-b border-slate-800/80 bg-slate-900/40 backdrop-blur-md px-6 flex items-center justify-between flex-shrink-0 z-20">
          {/* Quick Search */}
          <div className="flex items-center gap-2 bg-slate-950/60 border border-slate-800 rounded-lg px-3 py-1.5 w-72 text-slate-400 text-xs">
            <Search className="w-3.5 h-3.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search payments, incidents, beneficiaries..."
              className="bg-transparent border-none outline-none text-slate-200 placeholder:text-slate-500 w-full text-xs"
            />
          </div>

          {/* Right Header Actions */}
          <div className="flex items-center gap-3">
            {/* Quick Role Switcher (Hackathon MVP feature) */}
            <div className="relative">
              <button
                onClick={() => setIsRoleMenuOpen(!isRoleMenuOpen)}
                className="flex items-center gap-2 text-xs bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-200 px-3 py-1.5 rounded-lg transition-colors"
              >
                <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
                <span>Role: <strong className="text-amber-400 capitalize">{user?.role?.replace('_', ' ') || 'Admin'}</strong></span>
                <ChevronDown className="w-3 h-3 text-slate-400" />
              </button>

              {isRoleMenuOpen && (
                <div className="absolute right-0 mt-2 w-72 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-1.5 z-50">
                  <div className="px-3 py-2 border-b border-slate-800 mb-1">
                    <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Switch Persona</p>
                  </div>
                  {roles.map((r) => (
                    <button
                      key={r.id}
                      onClick={() => {
                        quickDemoLogin(r.id as any);
                        setIsRoleMenuOpen(false);
                      }}
                      className="w-full text-left px-3 py-2 rounded-lg text-xs hover:bg-slate-800 transition-colors flex items-start justify-between"
                    >
                      <div>
                        <p className="font-medium text-slate-200">{r.label}</p>
                        <p className="text-[10px] text-slate-400 mt-0.5">{r.desc}</p>
                      </div>
                      {user?.role === r.id && <Check className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Notification Bell */}
            <div className="relative">
              <button
                onClick={() => setIsNotifOpen(!isNotifOpen)}
                className="relative p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
              >
                <Bell className="w-4 h-4" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-amber-500" />
              </button>

              {isNotifOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-3 z-50">
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
                    <h4 className="text-xs font-semibold text-slate-200">Alerts & Notifications</h4>
                    <span className="text-[10px] text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded">3 Unread</span>
                  </div>
                  <div className="space-y-2 text-xs">
                    <div className="p-2 rounded bg-rose-500/10 border border-rose-500/20 text-rose-300">
                      <p className="font-semibold text-[11px]">Critical: Duplicate Payment Risk</p>
                      <p className="text-[10px] text-rose-400/80 mt-0.5">INV-2024-092 ($125,000 USD) flagged for duplicate review.</p>
                    </div>
                    <div className="p-2 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300">
                      <p className="font-semibold text-[11px]">SLA Imminent: INC-2024000007</p>
                      <p className="text-[10px] text-amber-400/80 mt-0.5">Pending USD 156,000 SLA breach in 4 hours.</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Landing page link */}
            <NavLink
              to="/"
              className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1 px-2.5 py-1 rounded-md hover:bg-slate-800 transition-colors"
            >
              <span>Landing</span>
              <ExternalLink className="w-3 h-3" />
            </NavLink>
          </div>
        </header>

        {/* Scrollable Page Outlet */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
