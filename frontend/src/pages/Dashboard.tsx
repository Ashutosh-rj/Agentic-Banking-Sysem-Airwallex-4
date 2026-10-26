import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Wallet, AlertTriangle, CreditCard, CheckCircle2, TrendingUp,
  ArrowUpRight, ArrowDownRight, Clock, ShieldAlert, Sparkles,
  RefreshCw, Check, ArrowRight
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';
import { dashboardService } from '../services/domainServices';
import { DashboardSummary, ActivityItem, TrendPoint } from '../types';
import { StatusBadge } from '../components/ui/Badge';
import { getErrorMessage } from '../services/api';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [trends, setTrends] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumRes, actRes, trRes] = await Promise.all([
        dashboardService.getSummary(),
        dashboardService.getActivity(10),
        dashboardService.getTrends(14),
      ]);
      setSummary(sumRes);
      setActivity(actRes);
      setTrends(trRes);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-slate-400">Loading Treasury Command Center metrics...</p>
        </div>
      </div>
    );
  }

  if (error && !summary) {
    return (
      <div className="p-6 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-300">
        <p className="font-semibold text-sm">Failed to load command center data</p>
        <p className="text-xs mt-1 text-rose-400/80">{error}</p>
        <button
          onClick={fetchData}
          className="mt-3 px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-medium cursor-pointer"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <span>Treasury Command Center</span>
            <span className="text-xs font-mono font-medium text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">
              LIVE TELEMETRY
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time multi-currency balances, incident queue, and automated risk diagnostics.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchData}
            className="flex items-center gap-1.5 text-xs bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
          <button
            onClick={() => navigate('/app/payments')}
            className="flex items-center gap-1.5 text-xs bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
          >
            <CreditCard className="w-3.5 h-3.5" />
            <span>Initiate Payment</span>
          </button>
        </div>
      </div>

      {/* Primary KPI Grid (clickable) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Available */}
        <div
          onClick={() => navigate('/app/treasury')}
          className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-amber-500/40 transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Total Available Liquidity</span>
            <div className="w-7 h-7 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <Wallet className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold font-mono text-slate-100 mt-2">
            ${summary?.total_available_usd_equivalent ? Number(summary.total_available_usd_equivalent).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00'}
          </p>
          <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-800/60 text-[11px]">
            <span className="text-slate-400">USD Equivalent</span>
            <span className="text-amber-400 group-hover:underline flex items-center gap-0.5">
              <span>View accounts</span>
              <ArrowUpRight className="w-3 h-3" />
            </span>
          </div>
        </div>

        {/* Pending Commitment */}
        <div
          onClick={() => navigate('/app/payments?status=PENDING,SUBMITTED')}
          className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-amber-500/40 transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Pending Payments</span>
            <div className="w-7 h-7 rounded-lg bg-sky-500/10 text-sky-400 flex items-center justify-center">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold font-mono text-sky-400 mt-2">
            ${summary?.pending_amount ? Number(summary.pending_amount).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00'}
          </p>
          <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-800/60 text-[11px]">
            <span className="text-slate-400">{summary?.pending_payments || 0} In Flight</span>
            <span className="text-sky-400 group-hover:underline flex items-center gap-0.5">
              <span>Inspect</span>
              <ArrowUpRight className="w-3 h-3" />
            </span>
          </div>
        </div>

        {/* Open Incidents */}
        <div
          onClick={() => navigate('/app/incidents')}
          className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-rose-500/40 transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Incident Queue</span>
            <div className="w-7 h-7 rounded-lg bg-rose-500/10 text-rose-400 flex items-center justify-center">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold font-mono text-rose-400 mt-2">
            {summary?.open_incidents || 0} <span className="text-xs font-normal text-slate-400">Open</span>
          </p>
          <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-800/60 text-[11px]">
            <span className="text-rose-400">{summary?.critical_incidents || 0} Critical</span>
            <span className="text-rose-400 group-hover:underline flex items-center gap-0.5">
              <span>Resolve</span>
              <ArrowUpRight className="w-3 h-3" />
            </span>
          </div>
        </div>

        {/* SLA Breaches & Recon */}
        <div
          onClick={() => navigate('/app/reconciliation')}
          className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-purple-500/40 transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Reconciliation Exceptions</span>
            <div className="w-7 h-7 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold font-mono text-purple-400 mt-2">
            {summary?.unresolved_exceptions || 0} <span className="text-xs font-normal text-slate-400">Items</span>
          </p>
          <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-800/60 text-[11px]">
            <span className="text-slate-400">{summary?.sla_breach_count || 0} SLA Breached</span>
            <span className="text-purple-400 group-hover:underline flex items-center gap-0.5">
              <span>Workbench</span>
              <ArrowUpRight className="w-3 h-3" />
            </span>
          </div>
        </div>
      </div>

      {/* Account Balances Grid */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-slate-200">Segregated Operating Accounts</h3>
          <button
            onClick={() => navigate('/app/treasury')}
            className="text-xs text-amber-400 hover:underline flex items-center gap-1"
          >
            <span>All Currency Balances</span>
            <ArrowRight className="w-3 h-3" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {summary?.accounts?.map((acc) => (
            <div key={acc.id} className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                <span className="font-medium text-slate-300">{acc.name}</span>
                <span className="font-mono text-amber-400 font-bold">{acc.currency}</span>
              </div>
              <p className="text-lg font-bold font-mono text-slate-100">
                {Number(acc.available_balance).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
              <div className="flex items-center justify-between text-[10px] text-slate-500 mt-1">
                <span>Reserved: ${Number(acc.reserved_balance).toLocaleString()}</span>
                <span>{acc.provider || 'Airwallex'}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Charts & Activity Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Chart (2 columns) */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">14-Day Payment & Incident Velocity</h3>
              <p className="text-xs text-slate-400 mt-0.5">Correlating payment throughput with exception detection</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                <span className="text-slate-300">Payments</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                <span className="text-slate-300">Incidents</span>
              </div>
            </div>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="payGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="incGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                />
                <Area type="monotone" dataKey="payments" stroke="#f59e0b" strokeWidth={2} fillOpacity={1} fill="url(#payGrad)" />
                <Area type="monotone" dataKey="incidents" stroke="#f43f5e" strokeWidth={2} fillOpacity={1} fill="url(#incGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Real-time Activity Stream */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-200">Recent Operations</h3>
            <span className="text-[10px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">Live Stream</span>
          </div>

          <div className="space-y-3 flex-1 overflow-y-auto max-h-64 pr-1">
            {activity.map((item) => (
              <div
                key={item.id}
                onClick={() => {
                  if (item.type === 'incident') navigate('/app/incidents');
                  else navigate('/app/payments');
                }}
                className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 transition-colors cursor-pointer text-xs"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-slate-200">{item.title}</span>
                  {item.status && <StatusBadge status={item.status} />}
                </div>
                <p className="text-[11px] text-slate-400 truncate">{item.description}</p>
                <span className="text-[10px] text-slate-500 mt-1 block">
                  {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
