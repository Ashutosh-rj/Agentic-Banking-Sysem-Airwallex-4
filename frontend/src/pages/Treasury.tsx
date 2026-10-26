import React, { useState, useEffect } from 'react';
import {
  Wallet, TrendingUp, AlertTriangle, ArrowUpRight, ArrowDownRight,
  Clock, ShieldCheck, Sparkles, Filter, ChevronRight, Sliders
} from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';
import { treasuryService } from '../services/domainServices';
import { Account, TreasuryPosition, PaymentObligation, CashFlowForecastEntry } from '../types';
import { StatusBadge, Badge } from '../components/ui/Badge';
import { getErrorMessage } from '../services/api';

export const Treasury: React.FC = () => {
  const [positions, setPositions] = useState<TreasuryPosition[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [obligations, setObligations] = useState<PaymentObligation[]>([]);
  const [forecast, setForecast] = useState<CashFlowForecastEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [simulatedOutflow, setSimulatedOutflow] = useState<number>(0);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [posRes, accRes, obRes, fcRes] = await Promise.all([
          treasuryService.getPositions(),
          treasuryService.getAccounts(),
          treasuryService.getObligations(1, 20),
          treasuryService.getForecast(14),
        ]);
        setPositions(posRes);
        setAccounts(accRes);
        setObligations(obRes.items);
        setForecast(fcRes);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Compute simulated forecast based on slider
  const displayedForecast = forecast.map((f, i) => {
    const base = Number(f.cumulative || f.projected_balance || 450000);
    // Apply simulated outflow on day 3 onwards
    const adjusted = i >= 2 ? base - simulatedOutflow : base;
    return {
      ...f,
      projected_balance: adjusted.toFixed(2),
      simulated: (base - simulatedOutflow).toFixed(2),
    };
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <span>Treasury & Working Capital</span>
            <span className="text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded font-mono">
              DECIMAL-PRECISION LEDGER
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time balance reservations, multi-currency segregation, and forward cash obligation forecasting.
          </p>
        </div>
      </div>

      {/* Multi-Currency Positions Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {positions.map((pos) => {
          const avail = Number(pos.available || pos.available_balance || 0);
          const reserved = Number(pos.reserved || pos.reserved_balance || 0);
          const total = Number(pos.total || pos.total_balance || (avail + reserved));

          return (
            <div key={pos.currency} className="p-5 rounded-xl bg-slate-900 border border-slate-800">
              <div className="flex items-center justify-between">
                <span className="font-bold text-base text-amber-400 font-mono">{pos.currency} Position</span>
                <span className="text-[10px] bg-slate-800 px-2 py-0.5 rounded text-slate-400 font-mono">
                  Active
                </span>
              </div>

              <p className="text-2xl font-bold font-mono text-slate-100 mt-3">
                {pos.currency} {avail.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
              <p className="text-[11px] text-slate-400 mt-0.5">Available for Disbursal</p>

              <div className="mt-3 pt-3 border-t border-slate-800/80 space-y-1 text-xs">
                <div className="flex items-center justify-between text-slate-400">
                  <span>Reserved Obligations:</span>
                  <span className="font-mono text-amber-400/90 font-medium">
                    {reserved.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Gross Bank Total:</span>
                  <span className="font-mono text-slate-200 font-medium">
                    {total.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 14-Day Cash Flow Forecast with Scenario Simulator */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">14-Day Forward Liquidity Projection</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Net balance incorporating pending obligations and scheduled supplier settlements
            </p>
          </div>

          {/* Interactive Scenario Slider */}
          <div className="flex items-center gap-3 bg-slate-950 p-2 rounded-lg border border-slate-800 text-xs">
            <Sliders className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
            <span className="text-slate-400 text-[11px]">Simulate Stress Wire:</span>
            <input
              type="range"
              min="0"
              max="300000"
              step="25000"
              value={simulatedOutflow}
              onChange={(e) => setSimulatedOutflow(Number(e.target.value))}
              className="accent-amber-500 w-28 cursor-pointer"
            />
            <span className="font-mono text-amber-400 font-semibold w-16 text-right">
              ${(simulatedOutflow / 1000).toFixed(0)}k
            </span>
          </div>
        </div>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={displayedForecast} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 10 }} />
              <YAxis
                stroke="#64748b"
                tick={{ fontSize: 10 }}
                tickFormatter={(v) => `$${(Number(v) / 1000).toFixed(0)}k`}
              />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                formatter={(val: any) => [`$${Number(val).toLocaleString()}`, 'Projected Available']}
              />
              <Line
                type="monotone"
                dataKey="projected_balance"
                stroke="#f59e0b"
                strokeWidth={2.5}
                dot={{ r: 3, fill: '#f59e0b' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Upcoming Obligations Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">Committed Payment Obligations</h3>
            <p className="text-xs text-slate-400 mt-0.5">Prioritized supplier milestones ranked by contract urgency</p>
          </div>
          <span className="text-xs text-slate-400 font-mono">{obligations.length} upcoming</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase font-semibold text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-4">Milestone / Contract</th>
                <th className="py-3 px-4">Due Date</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {obligations.map((ob) => (
                <tr key={ob.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4">
                    <span className="font-semibold text-slate-200 block">{ob.description}</span>
                    <span className="text-[10px] text-slate-500 font-mono">ID: {ob.id.substring(0, 8)}</span>
                  </td>
                  <td className="py-3 px-4 text-slate-300 font-mono">
                    {new Date(ob.due_date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
                  </td>
                  <td className="py-3 px-4 font-mono font-bold text-slate-100">
                    {ob.currency} {Number(ob.amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </td>
                  <td className="py-3 px-4">
                    <Badge variant={ob.priority === 'critical' ? 'danger' : ob.priority === 'high' ? 'warning' : 'default'}>
                      {ob.priority}
                    </Badge>
                  </td>
                  <td className="py-3 px-4">
                    <StatusBadge status={ob.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
