import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AlertTriangle, Search, Filter, Bot, Clock, CheckCircle2,
  ShieldAlert, ChevronRight, User as UserIcon, RefreshCw, Sparkles,
  FileText, ArrowRight, Check, X
} from 'lucide-react';
import { incidentService } from '../services/domainServices';
import { Incident, IncidentEvidence } from '../types';
import { StatusBadge, Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { getErrorMessage } from '../services/api';

export const Incidents: React.FC = () => {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [loading, setLoading] = useState(true);

  // Detail Modal
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [resolving, setResolving] = useState(false);
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [investigating, setInvestigating] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const res = await incidentService.list({
        page,
        page_size: 20,
        status: statusFilter || undefined,
        severity: severityFilter || undefined,
      });
      setIncidents(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [page, statusFilter, severityFilter]);

  const handleInvestigate = async () => {
    if (!selectedIncident) return;
    setInvestigating(true);
    setActionError(null);
    try {
      const res = await incidentService.investigate(selectedIncident.id);
      // Reload current incident
      const updated = await incidentService.get(selectedIncident.id);
      setSelectedIncident(updated);
      fetchIncidents();
    } catch (err) {
      setActionError(getErrorMessage(err));
    } finally {
      setInvestigating(false);
    }
  };

  const handleResolve = async () => {
    if (!selectedIncident) return;
    setResolving(true);
    setActionError(null);
    try {
      const updated = await incidentService.resolve(selectedIncident.id, resolutionNotes || 'Resolved by operator review');
      setSelectedIncident(updated);
      fetchIncidents();
    } catch (err) {
      setActionError(getErrorMessage(err));
    } finally {
      setResolving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <span>Incident Commander</span>
            <span className="text-xs bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2 py-0.5 rounded font-mono">
              SLA GUARD ACTIVE
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Automated exception intake, root-cause diagnostics, and explainable intervention workflows.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate('/app/ai-investigation')}
            className="flex items-center gap-1.5 text-xs bg-purple-600 hover:bg-purple-500 text-white font-semibold px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
          >
            <Bot className="w-3.5 h-3.5" />
            <span>AI Workspace Pipeline</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-slate-900 p-3 rounded-xl border border-slate-800 text-xs">
        <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto">
          <span className="text-slate-500 flex items-center gap-1">
            <Filter className="w-3 h-3" /> Status:
          </span>
          {['', 'open', 'investigating', 'pending_action', 'resolved'].map((st) => (
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

      {/* Incident Queue */}
      <div className="space-y-3">
        {incidents.length === 0 ? (
          <div className="p-12 text-center bg-slate-900 border border-slate-800 rounded-xl text-slate-500">
            No active incidents matching the selected criteria.
          </div>
        ) : (
          incidents.map((inc) => (
            <div
              key={inc.id}
              onClick={() => setSelectedIncident(inc)}
              className="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-amber-500/40 transition-all cursor-pointer flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 group"
            >
              <div className="flex items-start gap-3">
                <div
                  className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    inc.severity === 'critical'
                      ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      : inc.severity === 'high'
                      ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  <AlertTriangle className="w-4 h-4" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-amber-400 font-semibold">{inc.incident_number}</span>
                    <Badge variant={inc.severity === 'critical' ? 'danger' : inc.severity === 'high' ? 'warning' : 'default'}>
                      {inc.severity}
                    </Badge>
                    <StatusBadge status={inc.status} />
                  </div>
                  <h3 className="text-sm font-semibold text-slate-200 mt-1">{inc.title}</h3>
                  <p className="text-xs text-slate-400 mt-0.5 line-clamp-1">{inc.description}</p>
                </div>
              </div>

              <div className="flex items-center gap-6 self-end sm:self-center text-xs">
                {inc.financial_impact && (
                  <div className="text-right">
                    <span className="text-[10px] text-slate-500 block">At Risk</span>
                    <span className="font-mono font-bold text-rose-400">
                      {inc.financial_currency || '$'} {Number(inc.financial_impact).toLocaleString()}
                    </span>
                  </div>
                )}

                {inc.sla_deadline && (
                  <div className="text-right">
                    <span className="text-[10px] text-slate-500 block">SLA Target</span>
                    <span className="font-mono text-slate-300">
                      {new Date(inc.sla_deadline).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                )}

                <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 group-hover:text-amber-400 group-hover:bg-amber-500/10 transition-colors">
                  <ChevronRight className="w-4 h-4" />
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Incident Detail Modal */}
      {selectedIncident && (
        <Modal
          isOpen={!!selectedIncident}
          onClose={() => setSelectedIncident(null)}
          title={`Incident ${selectedIncident.incident_number}: ${selectedIncident.title}`}
          description={`Created ${new Date(selectedIncident.created_at).toLocaleString()}`}
          maxWidth="4xl"
        >
          <div className="space-y-5 text-xs">
            {actionError && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400">
                {actionError}
              </div>
            )}

            {/* Severity & SLA Header */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <Badge variant={selectedIncident.severity === 'critical' ? 'danger' : 'warning'}>
                  {selectedIncident.severity.toUpperCase()} PRIORITY
                </Badge>
                <StatusBadge status={selectedIncident.status} />
                <span className="font-mono text-slate-400">Score: {selectedIncident.priority_score}/100</span>
              </div>
              {selectedIncident.financial_impact && (
                <div className="text-right">
                  <span className="text-[10px] text-slate-500">Quantified Financial Impact:</span>
                  <span className="font-mono font-bold text-rose-400 ml-2">
                    {selectedIncident.financial_currency || 'USD'} ${Number(selectedIncident.financial_impact).toLocaleString()}
                  </span>
                </div>
              )}
            </div>

            {/* Description */}
            <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800">
              <h4 className="text-slate-400 font-semibold mb-1 text-[11px] uppercase tracking-wider">Exception Description</h4>
              <p className="text-slate-200 text-xs leading-relaxed">{selectedIncident.description}</p>
            </div>

            {/* AI Investigation Report */}
            {selectedIncident.ai_report && (
              <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-800/40">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2 text-purple-300 font-semibold">
                    <Bot className="w-4 h-4" />
                    <span>Agentic Root-Cause Diagnostic Report</span>
                  </div>
                  <span className="text-[10px] text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded font-mono">
                    Deterministic Engine Output
                  </span>
                </div>
                <div className="text-slate-300 text-xs leading-relaxed whitespace-pre-line font-mono bg-slate-950/80 p-4 rounded-lg border border-purple-900/30 overflow-x-auto">
                  {selectedIncident.ai_report}
                </div>
              </div>
            )}

            {/* Resolve Form */}
            {selectedIncident.status !== 'resolved' && (
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                <h4 className="font-semibold text-slate-200 mb-2">Operator Action Sign-off</h4>
                <textarea
                  rows={2}
                  placeholder="Enter resolution notes, vendor confirmation ref, or authorization reason..."
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-100 placeholder:text-slate-500 mb-3"
                />
                <div className="flex items-center justify-between">
                  <button
                    type="button"
                    onClick={handleInvestigate}
                    disabled={investigating}
                    className="px-3 py-1.5 bg-purple-600/30 hover:bg-purple-600/50 text-purple-300 border border-purple-500/30 font-medium rounded-lg text-xs transition-colors flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${investigating ? 'animate-spin' : ''}`} />
                    <span>Re-run 7-Agent Investigation</span>
                  </button>

                  <button
                    type="button"
                    onClick={handleResolve}
                    disabled={resolving}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg text-xs transition-colors flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>Authorize & Mark Resolved</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
};
