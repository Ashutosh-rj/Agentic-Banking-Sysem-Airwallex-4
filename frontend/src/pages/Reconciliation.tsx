import React, { useState, useEffect } from 'react';
import {
  CheckCircle2, RefreshCw, AlertTriangle, FileText, Check,
  Search, Filter, ChevronRight, Layers, ArrowRight, ShieldCheck
} from 'lucide-react';
import { reconciliationService } from '../services/domainServices';
import { ReconciliationRun, ReconciliationRecord } from '../types';
import { StatusBadge, Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { getErrorMessage } from '../services/api';

export const Reconciliation: React.FC = () => {
  const [runs, setRuns] = useState<ReconciliationRun[]>([]);
  const [selectedRun, setSelectedRun] = useState<ReconciliationRun | null>(null);
  const [records, setRecords] = useState<ReconciliationRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [reviewModalRecord, setReviewModalRecord] = useState<ReconciliationRecord | null>(null);
  const [reviewNotes, setReviewNotes] = useState('');
  const [reviewResolution, setReviewResolution] = useState('VERIFIED_MATCH');
  const [reviewLoading, setReviewLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRuns = async () => {
    setLoading(true);
    try {
      const res = await reconciliationService.listRuns(1, 20);
      setRuns(res.items);
      if (res.items.length > 0 && !selectedRun) {
        setSelectedRun(res.items[0]);
        loadRunRecords(res.items[0].id);
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const loadRunRecords = async (runId: string) => {
    try {
      const res = await reconciliationService.getRunRecords(runId, 1, 50);
      setRecords(res.items);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchRuns();
  }, []);

  const handleTriggerRun = async () => {
    setTriggering(true);
    setError(null);
    try {
      const newRun = await reconciliationService.triggerRun();
      setSelectedRun(newRun);
      await fetchRuns();
      await loadRunRecords(newRun.id);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setTriggering(false);
    }
  };

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewModalRecord) return;
    setReviewLoading(true);
    try {
      await reconciliationService.reviewMatch(reviewModalRecord.id, reviewResolution, reviewNotes);
      setReviewModalRecord(null);
      if (selectedRun) loadRunRecords(selectedRun.id);
    } catch (err) {
      alert(getErrorMessage(err));
    } finally {
      setReviewLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <span>Reconciliation Center</span>
            <span className="text-xs bg-purple-500/10 text-purple-400 border border-purple-500/20 px-2 py-0.5 rounded font-mono">
              AUTOMATED MATCHING ENGINE
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Exact and probable matching of internal payment ledgers against bank statements and provider settlement lines.
          </p>
        </div>

        <button
          onClick={handleTriggerRun}
          disabled={triggering}
          className="flex items-center gap-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-4 py-2 rounded-lg text-xs transition-colors cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${triggering ? 'animate-spin' : ''}`} />
          <span>Trigger Reconciliation Run</span>
        </button>
      </div>

      {error && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs rounded-xl">
          {error}
        </div>
      )}

      {/* Runs Selector Carousel/Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {runs.map((r) => {
          const isSelected = selectedRun?.id === r.id;
          return (
            <div
              key={r.id}
              onClick={() => {
                setSelectedRun(r);
                loadRunRecords(r.id);
              }}
              className={`p-4 rounded-xl border transition-all cursor-pointer ${
                isSelected
                  ? 'bg-slate-900 border-amber-500/50 shadow-lg shadow-amber-500/5'
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-xs font-bold text-amber-400">{r.run_number}</span>
                <StatusBadge status={r.status} />
              </div>

              <div className="grid grid-cols-3 gap-2 text-center text-xs pt-2 border-t border-slate-800/80">
                <div>
                  <span className="text-[10px] text-slate-500 block">Matched</span>
                  <span className="font-mono font-bold text-emerald-400">{r.matched_count}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 block">Unmatched</span>
                  <span className="font-mono font-bold text-amber-400">{r.unmatched_count}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 block">Exceptions</span>
                  <span className="font-mono font-bold text-rose-400">{r.exception_count}</span>
                </div>
              </div>

              <span className="text-[10px] text-slate-500 mt-2 block text-right">
                {new Date(r.created_at).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          );
        })}
      </div>

      {/* Records Table for Selected Run */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">
              Matched & Discrepant Records — {selectedRun?.run_number}
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Review unmatched exceptions, amount rounding differences, and duplicate candidates.
            </p>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            {records.length} records in this batch
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase font-semibold text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-4">Internal Payment</th>
                <th className="py-3 px-4">Provider Ref</th>
                <th className="py-3 px-4">Match Status</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Discrepancy Notes</th>
                <th className="py-3 px-4 text-right">Review</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {records.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500">
                    No individual discrepancy records logged for this batch run.
                  </td>
                </tr>
              ) : (
                records.map((rec) => (
                  <tr key={rec.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 font-mono font-medium text-slate-200">
                      {rec.payment_number || rec.payment_id?.substring(0, 8) || 'N/A'}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-400">
                      {rec.provider_reference || '—'}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={rec.match_status} />
                    </td>
                    <td className="py-3 px-4 font-mono">
                      {rec.match_confidence ? (
                        <span className={rec.match_confidence > 0.9 ? 'text-emerald-400' : 'text-amber-400'}>
                          {Math.round(rec.match_confidence * 100)}%
                        </span>
                      ) : (
                        <span className="text-slate-500">—</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-slate-300">
                      {rec.discrepancy_notes || 'Clean match — zero variance'}
                    </td>
                    <td className="py-3 px-4 text-right">
                      {rec.match_status !== 'matched' && rec.match_status !== 'reviewed' ? (
                        <button
                          onClick={() => setReviewModalRecord(rec)}
                          className="px-2.5 py-1 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded text-[11px] font-medium transition-colors cursor-pointer"
                        >
                          Review & Resolve
                        </button>
                      ) : (
                        <span className="text-[11px] text-emerald-400 flex items-center justify-end gap-1">
                          <Check className="w-3.5 h-3.5" /> Resolved
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Review Match Modal */}
      {reviewModalRecord && (
        <Modal
          isOpen={!!reviewModalRecord}
          onClose={() => setReviewModalRecord(null)}
          title="Review Reconciliation Discrepancy"
          description={`Payment ${reviewModalRecord.payment_number || reviewModalRecord.payment_id?.substring(0, 8)}`}
          maxWidth="md"
        >
          <form onSubmit={handleReviewSubmit} className="space-y-4 text-xs">
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg">
              <span className="text-slate-500 text-[10px] block">Identified Discrepancy:</span>
              <p className="font-semibold text-slate-200 mt-0.5">{reviewModalRecord.discrepancy_notes || 'Amount or timestamp variance'}</p>
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1">Resolution Decision</label>
              <select
                value={reviewResolution}
                onChange={(e) => setReviewResolution(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100"
              >
                <option value="VERIFIED_MATCH">Approve as Match (Tolerate Variance)</option>
                <option value="HOLD_PAYMENT">Flag for Vendor Communication</option>
                <option value="MANUAL_LEDGER_ADJUSTMENT">Post FX / Fee Adjustment</option>
                <option value="DISMISS_VARIANCE">Dismiss Discrepancy</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1">Operator Justification Notes</label>
              <textarea
                rows={2}
                required
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                placeholder="Reference supporting bank statement statement line or FX rate sheet..."
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100"
              />
            </div>

            <div className="pt-2 flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => setReviewModalRecord(null)}
                className="px-3 py-1.5 text-slate-400 hover:text-slate-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={reviewLoading}
                className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-lg transition-colors cursor-pointer disabled:opacity-50"
              >
                {reviewLoading ? 'Submitting...' : 'Sign Off & Update'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};
