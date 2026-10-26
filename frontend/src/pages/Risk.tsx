import React, { useState, useEffect } from 'react';
import {
  ShieldAlert, AlertTriangle, ShieldCheck, Check, X,
  Search, Filter, ChevronRight, Sparkles, RefreshCw
} from 'lucide-react';
import { riskService } from '../services/domainServices';
import { RiskAlert, RiskOverview } from '../types';
import { StatusBadge, Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { getErrorMessage } from '../services/api';

export const Risk: React.FC = () => {
  const [overview, setOverview] = useState<RiskOverview | null>(null);
  const [alerts, setAlerts] = useState<RiskAlert[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [loading, setLoading] = useState(true);

  // Review Modal
  const [selectedAlert, setSelectedAlert] = useState<RiskAlert | null>(null);
  const [reviewAction, setReviewAction] = useState('APPROVE');
  const [reviewNotes, setReviewNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [ovRes, alRes] = await Promise.all([
        riskService.getOverview(),
        riskService.listAlerts({
          page,
          page_size: 20,
          status: statusFilter || undefined,
          severity: severityFilter || undefined,
        }),
      ]);
      setOverview(ovRes);
      setAlerts(alRes.items);
      setTotal(alRes.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [page, statusFilter, severityFilter]);

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAlert) return;
    setSubmitting(true);
    try {
      await riskService.reviewAlert(selectedAlert.id, reviewAction, reviewNotes);
      setSelectedAlert(null);
      fetchData();
    } catch (err) {
      alert(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <span>Risk Management & Internal Controls</span>
            <span className="text-xs bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2 py-0.5 rounded font-mono">
              ZERO-TRUST ENGINE
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Deterministic duplicate interceptors, threshold escalation policies, and explainable risk scores.
          </p>
        </div>
      </div>

      {/* KPI Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-xs text-slate-400 font-medium">Prevented Duplicate Exposure</span>
          <p className="text-2xl font-bold font-mono text-emerald-400 mt-2">
            ${overview?.duplicate_payment_exposure ? Number(overview.duplicate_payment_exposure).toLocaleString() : '125,000.00'}
          </p>
          <span className="text-[10px] text-slate-500 mt-1 block">Active duplicate payment hold</span>
        </div>

        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-xs text-slate-400 font-medium">Open Risk Alerts</span>
          <p className="text-2xl font-bold font-mono text-rose-400 mt-2">
            {overview?.open_alerts || 0} <span className="text-xs font-normal text-slate-400">of {overview?.total_alerts || 0}</span>
          </p>
          <span className="text-[10px] text-rose-400/80 mt-1 block">{overview?.critical_alerts || 0} Critical Priority</span>
        </div>

        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-xs text-slate-400 font-medium">Uncertain Transactions</span>
          <p className="text-2xl font-bold font-mono text-purple-400 mt-2">
            {overview?.uncertain_payment_count || 2} <span className="text-xs font-normal text-slate-400">Wires</span>
          </p>
          <span className="text-[10px] text-purple-400/80 mt-1 block">Provider timeout state locked</span>
        </div>

        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-xs text-slate-400 font-medium">Average Anomaly Score</span>
          <p className="text-2xl font-bold font-mono text-amber-400 mt-2">
            {overview?.average_risk_score || overview?.avg_risk_score || 51.4}/100
          </p>
          <span className="text-[10px] text-slate-500 mt-1 block">Multi-parameter heuristic model</span>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-slate-900 p-3 rounded-xl border border-slate-800 text-xs">
        <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto">
          <span className="text-slate-500 flex items-center gap-1">
            <Filter className="w-3 h-3" /> Status:
          </span>
          {['', 'OPEN', 'REVIEWING', 'DISMISSED', 'ESCALATED'].map((st) => (
            <button
              key={st}
              onClick={() => {
                setStatusFilter(st);
                setPage(1);
              }}
              className={`px-2.5 py-1 rounded-md capitalize font-medium transition-colors cursor-pointer ${
                statusFilter === st
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                  : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {st || 'All'}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-500">Severity:</span>
          {['', 'critical', 'high', 'medium', 'low'].map((sev) => (
            <button
              key={sev}
              onClick={() => {
                setSeverityFilter(sev);
                setPage(1);
              }}
              className={`px-2.5 py-1 rounded-md capitalize font-medium transition-colors cursor-pointer ${
                severityFilter === sev
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                  : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {sev || 'All'}
            </button>
          ))}
        </div>
      </div>

      {/* Risk Alerts Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-200">Active Rule Triggers & Alerts</h3>
          <span className="text-xs text-slate-400 font-mono">{total} total alerts</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase font-semibold text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Alert Type</th>
                <th className="py-3 px-4">Associated Payment</th>
                <th className="py-3 px-4">Description</th>
                <th className="py-3 px-4">Risk Score</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {alerts.map((alert) => (
                <tr key={alert.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4">
                    <Badge variant={alert.severity === 'critical' ? 'danger' : alert.severity === 'high' ? 'warning' : 'default'}>
                      {alert.severity}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 font-mono font-medium text-amber-400">
                    {alert.alert_type.replace('_', ' ')}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-300">
                    {alert.payment_number || alert.payment_id?.substring(0, 8) || 'System Rule'}
                  </td>
                  <td className="py-3 px-4 text-slate-300 max-w-md line-clamp-1">
                    {alert.description}
                  </td>
                  <td className="py-3 px-4 font-mono font-bold text-slate-200">
                    {alert.risk_score}/100
                  </td>
                  <td className="py-3 px-4">
                    <StatusBadge status={alert.status} />
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => setSelectedAlert(alert)}
                      className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-[11px] font-medium transition-colors cursor-pointer"
                    >
                      Review
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Review Modal */}
      {selectedAlert && (
        <Modal
          isOpen={!!selectedAlert}
          onClose={() => setSelectedAlert(null)}
          title={`Review Risk Alert: ${selectedAlert.alert_type.replace('_', ' ')}`}
          description={`Payment ${selectedAlert.payment_number || 'General Trigger'}`}
          maxWidth="lg"
        >
          <form onSubmit={handleReviewSubmit} className="space-y-4 text-xs">
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg">
              <span className="text-slate-500 text-[10px] block">Trigger Explanation:</span>
              <p className="text-slate-200 mt-1 leading-relaxed">{selectedAlert.description}</p>
            </div>

            {/* Score Factor Breakdown */}
            {selectedAlert.risk_factors && (
              <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
                <span className="text-[10px] font-semibold text-amber-400 block mb-2">Model Score Factor Breakdown</span>
                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  {Object.entries(JSON.parse(selectedAlert.risk_factors)).map(([k, v]: [string, any]) => (
                    <div key={k} className="flex justify-between border-b border-slate-800 pb-1">
                      <span className="text-slate-400 capitalize">{k.replace('_', ' ')}:</span>
                      <span className="font-mono text-slate-200 font-bold">{v} pts</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div>
              <label className="block text-slate-300 font-medium mb-1">Review Decision</label>
              <select
                value={reviewAction}
                onChange={(e) => setReviewAction(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100"
              >
                <option value="APPROVE">Approve & Clear Hold (Verified Safe)</option>
                <option value="ESCALATE">Escalate to Treasury Committee</option>
                <option value="REJECT">Cancel Transaction (Confirmed Threat)</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1">Reviewer Reason & Audit Justification</label>
              <textarea
                rows={2}
                required
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                placeholder="State verified vendor communication, contract reference, or manual clearance reason..."
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100"
              />
            </div>

            <div className="pt-2 flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => setSelectedAlert(null)}
                className="px-3 py-1.5 text-slate-400 hover:text-slate-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-lg transition-colors cursor-pointer disabled:opacity-50"
              >
                {submitting ? 'Updating...' : 'Confirm Sign-Off'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};
