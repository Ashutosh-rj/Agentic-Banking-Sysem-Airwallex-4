import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CreditCard, Search, Filter, RefreshCw, Plus, ArrowRight,
  AlertTriangle, Clock, CheckCircle2, ShieldCheck, ChevronRight, X
} from 'lucide-react';
import { paymentService, treasuryService, riskService } from '../services/domainServices';
import { Payment, PaymentTimelineEvent, Account } from '../types';
import { StatusBadge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { getErrorMessage } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const Payments: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [payments, setPayments] = useState<Payment[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  // Detail Modal State
  const [selectedPayment, setSelectedPayment] = useState<Payment | null>(null);
  const [timeline, setTimeline] = useState<PaymentTimelineEvent[]>([]);
  const [timelineLoading, setTimelineLoading] = useState(false);
  const [retryLoading, setRetryLoading] = useState(false);
  const [retryError, setRetryError] = useState<string | null>(null);

  // Create Payment Drawer/Modal State
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [amount, setAmount] = useState('15000.00');
  const [currency, setCurrency] = useState('USD');
  const [reference, setReference] = useState('INV-2024-TEST');
  const [description, setDescription] = useState('Supplier settlement');
  const [selectedAccountId, setSelectedAccountId] = useState('');
  const [beneficiaryId, setBeneficiaryId] = useState('');
  const [createLoading, setCreateLoading] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const fetchPayments = async () => {
    setLoading(true);
    try {
      const res = await paymentService.list({
        page,
        page_size: 20,
        status: statusFilter || undefined,
        search: search || undefined,
      });
      setPayments(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPayments();
  }, [page, statusFilter]);

  useEffect(() => {
    // Load accounts for payment form
    treasuryService.getAccounts().then((accs) => {
      setAccounts(accs);
      if (accs.length > 0) setSelectedAccountId(accs[0].id);
    });
  }, []);

  const handleSelectPayment = async (p: Payment) => {
    setSelectedPayment(p);
    setTimelineLoading(true);
    setRetryError(null);
    try {
      const tl = await paymentService.getTimeline(p.id);
      setTimeline(tl);
    } catch (err) {
      console.error(err);
    } finally {
      setTimelineLoading(false);
    }
  };

  const handleRetry = async () => {
    if (!selectedPayment) return;
    setRetryLoading(true);
    setRetryError(null);
    try {
      const updated = await paymentService.retry(selectedPayment.id);
      setSelectedPayment(updated);
      fetchPayments();
      // refresh timeline
      const tl = await paymentService.getTimeline(updated.id);
      setTimeline(tl);
    } catch (err) {
      setRetryError(getErrorMessage(err));
    } finally {
      setRetryLoading(false);
    }
  };

  const handleCreatePayment = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateLoading(true);
    setCreateError(null);
    try {
      // First account's org beneficiary or fallback
      await paymentService.create({
        amount,
        currency,
        account_id: selectedAccountId,
        beneficiary_id: beneficiaryId || 'b1-demo-uuid',
        reference,
        description,
      });
      setIsCreateOpen(false);
      fetchPayments();
    } catch (err) {
      setCreateError(getErrorMessage(err));
    } finally {
      setCreateLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight">Payments Operations</h1>
          <p className="text-xs text-slate-400 mt-1">
            Deterministic state machine with automated duplicate protection and safe retry controls.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsCreateOpen(true)}
            className="flex items-center gap-1.5 text-xs bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Create Payment</span>
          </button>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-slate-900 p-3 rounded-xl border border-slate-800">
        <div className="flex items-center gap-2 w-full sm:w-80 bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300">
          <Search className="w-3.5 h-3.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search by ID or Reference..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && fetchPayments()}
            className="bg-transparent border-none outline-none w-full text-slate-200 placeholder:text-slate-500 text-xs"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto text-xs">
          <span className="text-slate-500 flex items-center gap-1">
            <Filter className="w-3 h-3" /> Status:
          </span>
          {['', 'SUCCEEDED', 'PENDING', 'FAILED', 'UNKNOWN', 'REQUIRES_REVIEW'].map((st) => (
            <button
              key={st}
              onClick={() => {
                setStatusFilter(st);
                setPage(1);
              }}
              className={`px-2.5 py-1 rounded-md text-xs font-medium cursor-pointer transition-colors ${
                statusFilter === st
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                  : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {st || 'All'}
            </button>
          ))}
        </div>
      </div>

      {/* Payments Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase font-semibold text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-4">Payment #</th>
                <th className="py-3 px-4">Beneficiary</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Reference</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {payments.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">
                    No payment records matching the query.
                  </td>
                </tr>
              ) : (
                payments.map((p) => (
                  <tr
                    key={p.id}
                    onClick={() => handleSelectPayment(p)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors group"
                  >
                    <td className="py-3 px-4 font-mono font-medium text-slate-200">
                      {p.payment_number}
                    </td>
                    <td className="py-3 px-4 text-slate-300">
                      {p.beneficiary_name || 'Global Supplier'}
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-slate-100">
                      {p.currency} {Number(p.amount).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={p.status} />
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-400">
                      {p.reference || '—'}
                    </td>
                    <td className="py-3 px-4 text-slate-500">
                      {new Date(p.created_at).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className="text-amber-400 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-end gap-1 text-[11px]">
                        <span>Inspect</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 bg-slate-950/40">
          <span>Showing {payments.length} of {total} payments</span>
          <div className="flex items-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 cursor-pointer"
            >
              Previous
            </button>
            <span className="px-2 font-mono">Page {page}</span>
            <button
              disabled={page * 20 >= total}
              onClick={() => setPage(page + 1)}
              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 cursor-pointer"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* Payment Detail Modal */}
      {selectedPayment && (
        <Modal
          isOpen={!!selectedPayment}
          onClose={() => setSelectedPayment(null)}
          title={`Payment ${selectedPayment.payment_number}`}
          description={`Idempotency key: ${selectedPayment.idempotency_key || 'auto'}`}
          maxWidth="2xl"
        >
          <div className="space-y-5 text-xs">
            {/* Payment Summary Header */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-[11px]">Total Transacted Amount</p>
                <p className="text-2xl font-bold font-mono text-slate-100 mt-1">
                  {selectedPayment.currency} {Number(selectedPayment.amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div className="text-right">
                <StatusBadge status={selectedPayment.status} />
                <p className="text-[10px] text-slate-500 mt-1">Retry Count: {selectedPayment.retry_count}/3</p>
              </div>
            </div>

            {/* Error banner if FAILED or UNKNOWN */}
            {selectedPayment.error_message && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs">
                <p className="font-semibold flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                  <span>Provider Exception Details</span>
                </p>
                <p className="mt-1 text-[11px] text-rose-400/90 font-mono">{selectedPayment.error_message}</p>
              </div>
            )}

            {retryError && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
                {retryError}
              </div>
            )}

            {/* Metadata Grid */}
            <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-[11px]">
              <div>
                <span className="text-slate-500 block">Beneficiary:</span>
                <span className="font-medium text-slate-200">{selectedPayment.beneficiary_name || 'GlobalTech Ltd'}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Originating Account:</span>
                <span className="font-medium text-slate-200">{selectedPayment.account_name || 'USD Operating'}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Reference:</span>
                <span className="font-mono text-slate-200">{selectedPayment.reference || 'N/A'}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Provider Ref:</span>
                <span className="font-mono text-slate-200">{selectedPayment.provider_ref || 'Pending'}</span>
              </div>
            </div>

            {/* Timeline */}
            <div>
              <h4 className="font-semibold text-slate-200 mb-3 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-amber-400" />
                <span>Transaction State Timeline</span>
              </h4>
              {timelineLoading ? (
                <div className="py-4 text-center text-slate-500">Loading timeline...</div>
              ) : (
                <div className="space-y-3 relative before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
                  {timeline.map((event, idx) => (
                    <div key={idx} className="relative pl-6">
                      <div className="absolute left-1 top-1.5 w-2.5 h-2.5 rounded-full bg-amber-500 ring-4 ring-slate-900" />
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-slate-200 text-xs">{event.event}</span>
                          <span className="text-[10px] text-slate-500">
                            {new Date(event.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 mt-0.5">{event.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
              <span className="text-[11px] text-slate-500">
                Safe retry enforces idempotency locking
              </span>
              <div className="flex items-center gap-2">
                {selectedPayment.status === 'FAILED' && (
                  <button
                    onClick={handleRetry}
                    disabled={retryLoading}
                    className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-lg text-xs transition-colors flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${retryLoading ? 'animate-spin' : ''}`} />
                    <span>Authorize Safe Retry</span>
                  </button>
                )}
                {['UNKNOWN', 'REQUIRES_REVIEW'].includes(selectedPayment.status) && (
                  <button
                    onClick={() => {
                      setSelectedPayment(null);
                      navigate('/app/incidents');
                    }}
                    className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white font-medium rounded-lg text-xs transition-colors flex items-center gap-1.5 cursor-pointer"
                  >
                    <span>Investigate in Incident Commander</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>
          </div>
        </Modal>
      )}

      {/* Create Payment Modal */}
      <Modal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Initiate New Treasury Payment"
        description="Idempotent multi-currency wire with balance reservation"
        maxWidth="lg"
      >
        <form onSubmit={handleCreatePayment} className="space-y-4 text-xs">
          {createError && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400">
              {createError}
            </div>
          )}

          <div>
            <label className="block text-slate-300 font-medium mb-1">Debiting Account</label>
            <select
              value={selectedAccountId}
              onChange={(e) => setSelectedAccountId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200"
            >
              {accounts.map((acc) => (
                <option key={acc.id} value={acc.id}>
                  {acc.name} ({acc.currency} — Available: ${Number(acc.available_balance).toLocaleString()})
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-300 font-medium mb-1">Amount</label>
              <input
                type="number"
                step="0.01"
                required
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 font-mono text-slate-100"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">Currency</label>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200"
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="SGD">SGD</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-slate-300 font-medium mb-1">Invoice / Reference</label>
            <input
              type="text"
              required
              value={reference}
              onChange={(e) => setReference(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 font-mono text-slate-100"
              placeholder="INV-2024-XXX"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-medium mb-1">Description</label>
            <textarea
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-100"
            />
          </div>

          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-[11px] text-slate-400">
            <span className="font-semibold text-amber-400 block mb-0.5">Automated Risk Protection</span>
            This payment will run duplicate-detection checks against all settled and pending payments in the last 24 hours.
          </div>

          <div className="pt-3 border-t border-slate-800 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsCreateOpen(false)}
              className="px-3 py-1.5 text-slate-400 hover:text-slate-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createLoading}
              className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-lg transition-colors cursor-pointer disabled:opacity-50"
            >
              {createLoading ? 'Validating...' : 'Submit Payment'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
